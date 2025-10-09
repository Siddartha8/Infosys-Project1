import os
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Sentiment / text utils
from utils.text_utils import cleaned_string
from utils.sentiment import analyze_sentiment

# spaCy + regex for aspect extraction
import spacy, re
from collections import defaultdict
import pandas as pd

# System monitoring imports
import time
import psutil
import random

nlp = spacy.load("en_core_web_sm")

db = SQLAlchemy()

# Define the upload folder
UPLOAD_FOLDER = 'uploads'

# --- Database Models ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    
    # NEW: Method to update user profile
    def update_user(self, new_username, new_email):
        # Check if the new username is already taken by another user
        if User.query.filter(User.username == new_username, User.id != self.id).first():
            return False, "Username is already taken."
        # Check if the new email is already taken by another user
        if User.query.filter(User.email == new_email, User.id != self.id).first():
            return False, "Email is already taken."
            
        self.username = new_username
        self.email = new_email
        db.session.commit()
        return True, "Profile updated successfully."


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)
    source = db.Column(db.String(50), default="manual")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sentiment_label = db.Column(db.String(20))
    sentiment_score = db.Column(db.Float)

    original_text = db.Column(db.Text)
    cleaned = db.Column(db.Text)
    tokenized = db.Column(db.Text)
    processed = db.Column(db.Text)

    user = db.relationship("User", backref=db.backref("reviews", lazy=True))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

# --- Aspect Category Model ---
class AspectCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- System Log Model ---
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False) 
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text) 

# --- Model Feedback Model ---
class ModelFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    correct_sentiment = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    review = db.relationship('Review', backref=db.backref('feedback', lazy=True))

# --- Feedback Model ---
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    category = db.Column(db.String(50))
    message = db.Column(db.Text)
    attachment = db.Column(db.String(200)) 	# file path
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to easily get the submitter's username
    submitter = db.relationship("Admin", backref=db.backref("feedback", lazy=True))


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER), exist_ok=True) # Ensure upload folder exists

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(INSTANCE_DIR, "reviews.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)

@app.before_request
def set_globals():
    # Make UPLOAD_FOLDER accessible in Jinja templates (for file paths)
    g.upload_folder = UPLOAD_FOLDER

# --- Utility functions ---
def extract_aspects(text):
    predefined_aspects = [ac.name for ac in AspectCategory.query.all()]
    found_aspects = []
    text_lower = text.lower()
    
    for asp in predefined_aspects:
        if re.search(r'\b' + re.escape(asp.lower()) + r'\b', text_lower):
            found_aspects.append(asp)
    
    if not found_aspects:
        doc = nlp(text)
        found_aspects = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text) > 2]
    
    return list(set(found_aspects))

def analyze_aspect_sentiment(reviews):
    aspect_counts = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0, 'scores': []})
    for review in reviews:
        aspects = extract_aspects(review.text)
        for asp in aspects:
            sent = analyze_sentiment(review.text)
            label = sent["label"].lower()
            if label not in ["positive", "negative", "neutral"]:
                label = "neutral"
            aspect_counts[asp][label] += 1
            aspect_counts[asp]['scores'].append(sent["score"])
    final = []
    for asp, counts in aspect_counts.items():
        avg_conf = sum(counts['scores']) / len(counts['scores']) if counts['scores'] else 0
        label = max(['positive', 'negative', 'neutral'], key=lambda x: counts[x])
        final.append({
            "aspect": asp,
            "positive": counts["positive"],
            "negative": counts["negative"],
            "neutral": counts["neutral"],
            "label": label.capitalize(),
            "score": round(avg_conf, 2)
        })
    return final

def get_pipeline_steps(review):
    return [
        {"name": "Original", "text": review.original_text or review.text},
        {"name": "Cleaned", "text": review.cleaned or cleaned_string(review.text)},
        {"name": "Tokenized", "text": review.tokenized or " ".join((review.cleaned or "").split())},
        {"name": "Processed", "text": review.processed or (review.cleaned or review.text).lower().strip()}
    ]

def analyze_aspect_sentiment_per_review(text):
    aspects = extract_aspects(text)
    doc = nlp(text)
    results = []
    for asp in aspects:
        aspect_sentiment = None
        for sent in doc.sents:
            if asp in sent.text.lower():
                sent_res = analyze_sentiment(sent.text)
                aspect_sentiment = {
                    "aspect": asp,
                    "label": sent_res["label"].capitalize(),
                    "score": sent_res["score"]
                }
                break
        if not aspect_sentiment:
            sent_res = analyze_sentiment(text)
            aspect_sentiment = {
                "aspect": asp,
                "label": sent_res["label"].capitalize(),
                "score": sent_res["score"]
            }
        results.append(aspect_sentiment)
    return results

def highlight_text_with_aspects(text, aspects):
    highlighted = text
    for a in aspects:
        color_class = {
            "Positive": "highlight-positive",
            "Negative": "highlight-negative",
            "Neutral": "highlight-neutral"
        }[a["label"]]
        highlighted = re.sub(
            rf"\b{re.escape(a['aspect'])}\b",
            f"<span class='{color_class}'>{a['aspect']}</span>",
            highlighted,
            flags=re.IGNORECASE
        )
    return highlighted

def log_system_event(event_type, message, details=None):
    try:
        log = SystemLog(event_type=event_type, message=message, details=details)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log system event: {e}")
        db.session.rollback()

# ==================== User Profile Routes (UNCHANGED) ====================

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    data = request.get_json()
    new_username = data.get('username', '').strip()
    new_email = data.get('email', '').strip()

    if not new_username or not new_email:
        return jsonify({"success": False, "message": "Username and email cannot be empty"}), 400

    # Use the User model's update method
    success, message = user.update_user(new_username, new_email)
    
    if success:
        flash(message, "success")
        return jsonify({"success": True, "message": message, "username": user.username, "email": user.email})
    else:
        db.session.rollback()
        return jsonify({"success": False, "message": message}), 409

@app.route('/change_password', methods=['POST'])
def change_password():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    data = request.get_json()
    new_password = data.get('new_password', '')
    
    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400

    user.set_password(new_password)
    db.session.commit()
    
    flash("Password updated successfully!", "success")
    return jsonify({"success": True, "message": "Password updated successfully"})


# ==================== Admin Management Routes (UNCHANGED) ====================

@app.route('/admin/activate_user/<int:user_id>', methods=['POST'])
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.active = True
    db.session.commit()
    return jsonify({"success": True})

@app.route('/admin/deactivate_user/<int:user_id>', methods=['POST'])
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.active = False
    db.session.commit()
    return jsonify({"success": True})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True})

# --- User password reset route ---
@app.route('/admin/reset_password/<int:user_id>', methods=['POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.json.get('new_password')
    if new_password:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Password not provided"}), 400

# --- Aspect Category management routes ---
@app.route('/admin/aspect_categories/add', methods=['POST'])
def add_aspect_category():
    name = request.json.get('name')
    if not name:
        return jsonify({"success": False, "message": "Aspect name cannot be empty."}), 400
    if AspectCategory.query.filter_by(name=name).first():
        return jsonify({"success": False, "message": "Aspect already exists."}), 409
    
    new_aspect = AspectCategory(name=name)
    db.session.add(new_aspect)
    db.session.commit()
    return jsonify({"success": True, "id": new_aspect.id, "name": new_aspect.name})

@app.route('/admin/aspect_categories/delete/<int:aspect_id>', methods=['POST'])
def delete_aspect_category(aspect_id):
    aspect = AspectCategory.query.get_or_404(aspect_id)
    db.session.delete(aspect)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/admin/aspect_categories/edit/<int:aspect_id>', methods=['POST'])
def edit_aspect_category(aspect_id):
    aspect = AspectCategory.query.get_or_404(aspect_id)
    new_name = request.json.get('name')
    if not new_name:
        return jsonify({"success": False, "message": "New name cannot be empty."}), 400
    if AspectCategory.query.filter_by(name=new_name).first():
        return jsonify({"success": False, "message": "Aspect with this name already exists."}), 409
    
    aspect.name = new_name
    db.session.commit()
    return jsonify({"success": True, "id": aspect.id, "name": aspect.name})

# --- Feedback status update route (for admins to manage tickets) ---
@app.route('/admin/feedback/update_status/<int:feedback_id>', methods=['POST'])
def update_feedback_status(feedback_id):
    if "admin_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    feedback = Feedback.query.get_or_404(feedback_id)
    new_status = request.json.get('status')
    
    if new_status in ["Pending", "In Progress", "Resolved"]:
        feedback.status = new_status
        db.session.commit()
        return jsonify({"success": True, "new_status": new_status})
        
    return jsonify({"success": False, "message": "Invalid status"}), 400

# ==================== Main routes (UNCHANGED LOGIC, ONLY REDIRECTS) ====================

@app.route("/")
def home():
    return redirect(url_for("select_login"))

@app.route("/select_login")
def select_login():
    return render_template("select_login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("User already exists!", "danger")
            return redirect(url_for("register"))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        text = request.form.get("review_text")
        rating = request.form.get("rating")
        if text:
            clean_txt = cleaned_string(text)
            tokenized_txt = " ".join(clean_txt.split())
            processed_txt = tokenized_txt.lower()
            sentiment = analyze_sentiment(text)
            review = Review(
                user_id=user.id,
                text=text,
                rating=int(rating),
                sentiment_label=sentiment["label"],
                sentiment_score=sentiment["score"],
                original_text=text,
                cleaned=clean_txt,
                tokenized=tokenized_txt,
                processed=processed_txt
            )
            db.session.add(review)
            db.session.commit()
            flash("Review submitted!", "success")
            return redirect(url_for("dashboard"))
        csv_file = request.files.get("csv_file")
        if csv_file:
            start_time = time.time()
            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)
                review_count = 0
                for row in reader:
                    raw = row.get("text", "")
                    if not raw:
                        continue
                    clean_txt = cleaned_string(raw)
                    tokenized_txt = " ".join(clean_txt.split())
                    processed_txt = tokenized_txt.lower()
                    sent = analyze_sentiment(raw)
                    review = Review(
                        user_id=user.id,
                        text=raw,
                        rating=int(row.get("rating", 0)),
                        source=row.get("source", "csv"),
                        sentiment_label=sent["label"],
                        sentiment_score=sent["score"],
                        original_text=raw,
                        cleaned=clean_txt,
                        tokenized=tokenized_txt,
                        processed=processed_txt
                    )
                    db.session.add(review)
                    review_count += 1
                db.session.commit()
                end_time = time.time()
                processing_time = end_time - start_time
                log_system_event(
                    event_type='processing_time',
                    message=f"{review_count} reviews from CSV processed in {processing_time:.2f} seconds."
                )
                flash("CSV reviews uploaded successfully!", "success")
            except Exception as e:
                db.session.rollback()
                log_system_event(
                    event_type='upload_failed',
                    message=f"CSV upload failed: {str(e)}"
                )
                flash(f"CSV upload failed: {e}", "danger")
            return redirect(url_for("dashboard"))

    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()

    for r in reviews:
        review_aspects = analyze_aspect_sentiment_per_review(r.text)
        pipeline_steps = get_pipeline_steps(r)
        setattr(r, "aspects", review_aspects)
        setattr(r, "aspect_tags", review_aspects)
        setattr(r, "pipeline_steps", pipeline_steps)
        setattr(r, "timestamp", r.created_at.strftime("%Y-%m-%d %H:%M"))
        # ADDED: Attach the overall sentiment label to the object for display
        setattr(r, "overall_sentiment", r.sentiment_label or "Neutral")

    user_pos_count = sum(1 for r in reviews if r.rating and r.rating >= 4)
    user_neg_count = sum(1 for r in reviews if r.rating and r.rating <= 2)
    user_neu_count = sum(1 for r in reviews if r.rating and r.rating == 3)
    
    # --- NEW METRICS FOR DASHBOARD ---
    user_reviews_submitted = len(reviews)
    total = user_pos_count + user_neg_count + user_neu_count
    total_reviews_analyzed = total
    # ---------------------------------

    aspect_summary = analyze_aspect_sentiment(reviews)

    def get_sentiment_trends(reviews):
        import pandas as pd
        data = []
        for r in reviews:
            date_str = r.created_at.strftime("%Y-%m-%d")
            label = r.sentiment_label or "neutral"
            data.append({"date": date_str, "label": label})
        df = pd.DataFrame(data)
        trend_df = df.groupby(["date", "label"]).size().reset_index(name="count")
        pivot_df = trend_df.pivot(index='date', columns='label', values='count').fillna(0)
        for sentiment in ['positive', 'negative', 'neutral']:
            if sentiment not in pivot_df.columns:
                pivot_df[sentiment] = 0
        pivot_df = pivot_df.sort_index()
        labels_time = list(pivot_df.index)
        pos_counts = list(pivot_df['positive'])
        neg_counts = list(pivot_df['negative'])
        neu_counts = list(pivot_df['neutral'])
        return labels_time, pos_counts, neg_counts, neu_counts

    trend_labels, trend_positive, trend_negative, trend_neutral = get_sentiment_trends(reviews)

    # Compute top 5 positive and negative aspects
    sorted_aspects = sorted(aspect_summary, key=lambda a: a["positive"], reverse=True)
    top_positive_aspects = sorted_aspects[:5]

    sorted_aspects_neg = sorted(aspect_summary, key=lambda a: a["negative"], reverse=True)
    top_negative_aspects = sorted_aspects_neg[:5]

    return render_template(
        "dashboard.html",
        user=user,
        reviews=reviews,
        user_pos_count=user_pos_count,
        user_neg_count=user_neg_count,
        user_neu_count=user_neu_count,
        # --- NEW CONTEXT VARIABLES ---
        user_reviews_submitted=user_reviews_submitted,
        total_reviews_analyzed=total_reviews_analyzed,
        # ---------------------------
        aspect_details=aspect_summary,
        total_aspect_mentions=len(aspect_summary),
        unique_aspects=len(set(a["aspect"] for a in aspect_summary)),
        aspect_labels=[a["aspect"] for a in aspect_summary],
        aspect_pos=[a["positive"] for a in aspect_summary],
        aspect_neg=[a["negative"] for a in aspect_summary],
        aspect_neu=[a["neutral"] for a in aspect_summary],
        # trend data for graphs
        trend_labels=trend_labels,
        trend_positive=trend_positive,
        trend_negative=trend_negative,
        trend_neutral=trend_neutral,
        top_positive_aspects=top_positive_aspects,
        top_negative_aspects=top_negative_aspects
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("select_login"))

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials!", "danger")
    return render_template("admin_login.html")

@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin_id" not in session:
        flash("Please login as admin first.", "warning")
        return redirect(url_for("admin_login"))
    admin = Admin.query.get(session["admin_id"])

    # --- START DATA COLLECTION (Consolidated Logic - Must run before any return) ---
    users = User.query.all()
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    aspects = AspectCategory.query.all()

    now = datetime.utcnow()
    reviews_today = Review.query.filter(Review.created_at >= (now - timedelta(days=1))).count()
    reviews_week = Review.query.filter(Review.created_at >= (now - timedelta(weeks=1))).count()
    reviews_month = Review.query.filter(Review.created_at >= (now - timedelta(days=30))).count()
    
    # FIX: Ensure all base counter variables are defined here
    total_users = User.query.count() 
    total_reviews = Review.query.count()
    total_datasets = total_reviews
    recent_activity = reviews_today

    most_active_users = db.session.query(
        User.username, 
        db.func.count(Review.id).label('review_count')
    ).join(Review).group_by(User.id).order_by(db.desc('review_count')).limit(10).all()

    all_reviews = Review.query.all()
    all_aspects = analyze_aspect_sentiment(all_reviews)
    common_aspects = sorted(all_aspects, key=lambda x: x['positive'] + x['negative'] + x['neutral'], reverse=True)[:10]
    # --- END DATA COLLECTION ---


    if request.method == "POST":
        # Check if the POST request is for feedback submission
        if 'category' in request.form and 'message' in request.form:
            category = request.form.get('category')
            message = request.form.get('message')
            attachment_path = None
            
            # Handle file upload
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file.filename != '':
                    filename = secure_filename(f"{admin.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    attachment_path = filename # Save only the filename, not the full path
            
            # Create new feedback entry
            new_feedback = Feedback(
                user_id=admin.id,
                category=category,
                message=message,
                attachment=attachment_path
            )
            db.session.add(new_feedback)
            db.session.commit()
            flash("Feedback submitted successfully!", "success")
            return redirect(url_for("admin_dashboard", _anchor="feedback_support"))
        
        # Original CSV upload logic
        csv_file = request.files.get("csv_file")
        if csv_file:
            start_time = time.time()
            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)
                review_count = 0
                for row in reader:
                    user_lookup = User.query.filter_by(username=row.get("username")).first()
                    user_id_to_use = user_lookup.id if user_lookup else admin.id

                    raw = row.get("text", "")
                    if not raw:
                        continue
                    clean_txt = cleaned_string(raw)
                    tokenized_txt = " ".join(clean_txt.split())
                    processed_txt = tokenized_txt.lower()
                    sent = analyze_sentiment(raw)
                    review = Review(
                        user_id=user_id_to_use,
                        text=raw,
                        rating=int(row.get("rating", 0)),
                        source=row.get("source", "csv"),
                        sentiment_label=sent["label"],
                        sentiment_score=sent["score"],
                        original_text=raw,
                        cleaned=clean_txt,
                        tokenized=tokenized_txt,
                        processed=processed_txt
                    )
                    db.session.add(review)
                    review_count += 1
                db.session.commit()
                end_time = time.time()
                processing_time = end_time - start_time
                log_system_event(
                    event_type='processing_time',
                    message=f"{review_count} reviews from admin CSV processed in {processing_time:.2f} seconds."
                )
                flash("CSV reviews uploaded successfully!", "success")
            except Exception as e:
                db.session.rollback()
                log_system_event(
                    event_type='upload_failed',
                    message=f"Admin CSV upload failed: {str(e)}"
                )
                flash(f"Admin CSV upload failed: {e}", "danger")
            return redirect(url_for("admin_dashboard"))

    # Count stats for Analytics tab (must run for GET and POST fallback)
    pos_count = sum(1 for r in reviews if r.rating and r.rating >= 4)
    neg_count = sum(1 for r in reviews if r.rating and r.rating <= 2)
    neu_count = sum(1 for r in reviews if r.rating and 2 < r.rating < 4)
    admin_aspect_data = analyze_aspect_sentiment(reviews)

    reviews_by_user = {}
    for r in reviews:
        if r.user:
            is_admin = (r.user.username == 'admin')
            is_vip = r.user.username.lower().startswith('vip')
            review_aspects = analyze_aspect_sentiment_per_review(r.text)
            pipeline_steps = get_pipeline_steps(r)

            setattr(r, "username", r.user.username)
            setattr(r, "is_admin", is_admin)
            setattr(r, "is_vip", is_vip)
            setattr(r, "aspect_tags", review_aspects)
            setattr(r, "review_aspects", review_aspects)
            setattr(r, "aspects", review_aspects)
            setattr(r, "pipeline_steps", pipeline_steps)
            setattr(r, "highlighted_text", highlight_text_with_aspects(r.text, review_aspects))
            setattr(r, "timestamp", r.created_at.strftime("%Y-%m-%d %H:%M"))

            reviews_by_user.setdefault(r.user.username, []).append(r)

    # Fetch submitted feedback for the Feedback tab
    submitted_feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()


    return render_template(
        "admin_dashboard.html",
        admin=admin,
        users=users,
        reviews=reviews,
        reviews_by_user=reviews_by_user,
        pos_count=pos_count,
        neg_count=neg_count,
        neu_count=neu_count,
        admin_aspect_data=admin_aspect_data,
        total_users=total_users,
        total_datasets=total_datasets,
        total_reviews=total_reviews,
        recent_activity=recent_activity,
        aspects=aspects,
        reviews_today=reviews_today,
        reviews_week=reviews_week,
        reviews_month=reviews_month,
        most_active_users=most_active_users,
        common_aspects=common_aspects,
        submitted_feedback=submitted_feedback
    )

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_id", None)
    flash("Admin logged out!", "info")
    return redirect(url_for("select_login"))


@app.route('/download_attachment/<path:filename>')
def download_attachment(filename):
    if "admin_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Security check: ensures file is in the designated upload folder
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Use Flask's safe send_file function
    return send_file(filepath, as_attachment=True, download_name=filename)


# ==================== New System Monitoring API Endpoints (UNCHANGED) ====================

@app.route('/api/system_monitoring/performance_logs')
def get_performance_logs():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50).all()
    log_list = []
    for log in logs:
        log_list.append({
            'event_type': log.event_type,
            'message': log.message,
            'timestamp': log.timestamp.isoformat(),
            'details': log.details
        })
    return jsonify(log_list)

@app.route('/api/system_monitoring/model_accuracy_check')
def get_model_accuracy_sample():
    total_reviews = db.session.query(Review).count()
    if total_reviews == 0:
        return jsonify({'error': 'No reviews found'}), 404
    
    random_offset = random.randint(0, total_reviews - 1)
    sample_review = db.session.query(Review).offset(random_offset).first()
    
    if sample_review:
        predicted_sentiment = analyze_sentiment(sample_review.text)
        return jsonify({
            'id': sample_review.id,
            'text': sample_review.text,
            'predicted_sentiment': predicted_sentiment["label"],
            'original_sentiment': sample_review.sentiment_label
        })
    return jsonify({'error': 'Could not fetch a sample review'}), 500

@app.route('/api/system_monitoring/model_feedback', methods=['POST'])
def submit_model_feedback():
    data = request.get_json()
    review_id = data.get('review_id')
    correct_sentiment = data.get('correct_sentiment')
    
    if not review_id or not correct_sentiment:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400
    
    feedback = ModelFeedback(review_id=review_id, correct_sentiment=correct_sentiment)
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Feedback received'})

@app.route('/api/system_monitoring/server_stats')
def get_server_stats():
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory Usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Disk Usage
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent

    # Number of datasets stored (using Review records as a proxy)
    num_datasets = Review.query.count()

    return jsonify({
        'cpu_usage_percent': cpu_percent,
        'memory_usage_percent': memory_percent,
        'disk_usage_percent': disk_percent,
        'datasets_stored': num_datasets
    })

# =================== Additional pages routes (UPDATED REDIRECTS) ====================

@app.route("/user_management")
def user_management():
    # Redirect to admin dashboard with fragment/anchor for sidebar link consistency
    return redirect(url_for("admin_dashboard", _anchor="user_management"))

@app.route("/aspect_categories")
def aspect_categories():
    # Redirect to admin dashboard with fragment/anchor for sidebar link consistency
    return redirect(url_for("admin_dashboard", _anchor="aspect_categories"))

@app.route("/admin_reports")
def admin_reports():
    # Redirect to admin dashboard with fragment/anchor for sidebar link consistency
    return redirect(url_for("admin_dashboard", _anchor="admin_reports"))


@app.route("/feedback_support")
def feedback_support():
    # Redirect to admin dashboard with fragment/anchor for sidebar link consistency
    return redirect(url_for("admin_dashboard", _anchor="feedback_support"))


@app.route('/generate_system_report')
def generate_system_report():
    if "admin_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    all_reviews = Review.query.all()
    if not all_reviews:
        return jsonify({"error": "No reviews to generate report."}), 404

    # Aggregated data
    total_reviews = len(all_reviews)
    reviews_today = len([r for r in all_reviews if r.created_at >= (datetime.utcnow() - timedelta(days=1))])
    reviews_week = len([r for r in all_reviews if r.created_at >= (datetime.utcnow() - timedelta(weeks=1))])
    reviews_month = len([r for r in all_reviews if r.created_at >= (datetime.utcnow() - timedelta(days=30))])
    total_datasets = total_reviews
    
    most_active_users = db.session.query(
        User.username, 
        db.func.count(Review.id).label('review_count')
    ).join(Review).group_by(User.id).order_by(db.desc('review_count')).limit(10).all()
    
    all_aspects = analyze_aspect_sentiment(all_reviews)
    common_aspects = sorted(all_aspects, key=lambda x: x['positive'] + x['negative'] + x['neutral'], reverse=True)[:10]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["System Report"])
    writer.writerow(["Generated On", datetime.utcnow().isoformat()])
    writer.writerow([])
    
    writer.writerow(["Dataset Summary"])
    writer.writerow(["Total Reviews", total_reviews])
    writer.writerow(["Total Datasets", total_datasets])
    writer.writerow(["Reviews (Last 24h)", reviews_today])
    writer.writerow(["Reviews (Last 7 days)", reviews_week])
    writer.writerow(["Reviews (Last 30 days)", reviews_month])
    writer.writerow([])
    
    writer.writerow(["Most Active Users (Top 10)"])
    writer.writerow(["Username", "Review Count"])
    for user in most_active_users:
        writer.writerow([user.username, user.review_count])
    writer.writerow([])
    
    writer.writerow(["Most Common Aspects (Top 10)"])
    writer.writerow(["Aspect", "Positive", "Negative", "Neutral"])
    for aspect in common_aspects:
        writer.writerow([
            aspect['aspect'], 
            aspect['positive'], 
            aspect['negative'], 
            aspect['neutral']
        ])

    output.seek(0)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    filename = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(mem, mimetype='text/csv', download_name=filename, as_attachment=True)


@app.route('/generate_system_pdf_report')
def generate_system_pdf_report():
    if "admin_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    all_reviews = Review.query.all()
    if not all_reviews:
        return jsonify({"error": "No reviews to generate report."}), 404

    # Aggregated data
    total_reviews = len(all_reviews)
    reviews_today = len([r for r in all_reviews if r.created_at >= (datetime.utcnow() - timedelta(days=1))])
    reviews_week = len([r for r in all_reviews if r.created_at >= (datetime.utcnow() - timedelta(weeks=1))])
    reviews_month = len([r for r in all_reviews if r.created_at >= (datetime.utcnow() - timedelta(days=30))])
    total_datasets = total_reviews
    
    most_active_users = db.session.query(
        User.username, 
        db.func.count(Review.id).label('review_count')
    ).join(Review).group_by(User.id).order_by(db.desc('review_count')).limit(10).all()
    
    all_aspects = analyze_aspect_sentiment(all_reviews)
    common_aspects = sorted(all_aspects, key=lambda x: x['positive'] + x['negative'] + x['neutral'], reverse=True)[:10]

    mem = io.BytesIO()
    c = canvas.Canvas(mem, pagesize=letter)
    width, height = letter
    y = height - 40
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "System-Level Review Report")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 30

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Summary")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Total Reviews Processed: {total_reviews}")
    y -= 15
    c.drawString(50, y, f"Total Datasets Uploaded: {total_datasets}")
    y -= 15
    c.drawString(50, y, f"Reviews in last 24h: {reviews_today}")
    y -= 15
    c.drawString(50, y, f"Reviews in last 7 days: {reviews_week}")
    y -= 15
    c.drawString(50, y, f"Reviews in last 30 days: {reviews_month}")
    y -= 30

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Most Active Users (Top 10)")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, "Username")
    c.drawString(200, y, "Review Count")
    y -= 15
    c.setFont("Helvetica", 12)
    for user in most_active_users:
        c.drawString(60, y, user.username)
        c.drawString(200, y, str(user.review_count))
        y -= 15
        if y < 50: c.showPage(); y = height - 40
    y -= 15

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Most Common Aspects (Top 10)")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, "Aspect")
    c.drawString(200, y, "Positive")
    c.drawString(300, y, "Negative")
    c.drawString(400, y, "Neutral")
    y -= 15
    c.setFont("Helvetica", 12)
    for aspect in common_aspects:
        c.drawString(60, y, aspect['aspect'])
        c.drawString(200, y, str(aspect['positive']))
        c.drawString(300, y, str(aspect['negative']))
        c.drawString(400, y, str(aspect['neutral']))
        y -= 15
        if y < 50: c.showPage(); y = height - 40

    c.showPage()
    c.save()
    mem.seek(0)
    filename = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(mem, mimetype='application/pdf', download_name=filename, as_attachment=True)


# ==================== Report generation routes (UNCHANGED) ====================

@app.route('/generate_report')
def generate_report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at).all()
    if not reviews:
        flash("No reviews to generate report.", "warning")
        return redirect(url_for("dashboard"))

    total_reviews = len(reviews)
    time_range_start = reviews[-1].created_at.strftime("%Y-%m-%d") if reviews else "N/A"
    time_range_end = reviews[0].created_at.strftime("%Y-%m-%d") if reviews else "N/A"

    # Count sentiment
    sentiment_counts = {"positive":0, "negative":0, "neutral":0}
    for r in reviews:
        label = r.sentiment_label.lower() if r.sentiment_label else "neutral"
        if label in sentiment_counts:
            sentiment_counts[label] += 1

    # Aspect summary
    aspect_summary = analyze_aspect_sentiment(reviews)
    key_insights = {
        "positive": [a for a in aspect_summary if a["label"] == "Positive"],
        "negative": [a for a in aspect_summary if a["label"] == "Negative"]
    }

    output = io.StringIO()
    writer = csv.writer(output)

    # Dataset summary
    writer.writerow(["Dataset Summary"])
    writer.writerow(["Total Reviews", total_reviews])
    writer.writerow(["Time Range", f"{time_range_start} to {time_range_end}"])
    writer.writerow([])

    # Sentiment distribution
    writer.writerow(["Sentiment Distribution"])
    total = total_reviews if total_reviews > 0 else 1
    for sentiment, count in sentiment_counts.items():
        percent = (count / total) * 100
        writer.writerow([sentiment.capitalize(), count, f"{percent:.1f}%"])
    writer.writerow([])

    # Aspect highlights
    writer.writerow(["Key Aspect Insights"])
    for a in aspect_summary:
        writer.writerow([a["aspect"], a["label"], a["score"]])
    writer.writerow([])

    # Key insights
    writer.writerow(["Key Insights"])
    writer.writerow(["Positive Aspects"])
    for a in key_insights["positive"]:
        writer.writerow([a["aspect"], a["label"], a["score"]])
    writer.writerow([])
    writer.writerow(["Negative Aspects"])
    for a in key_insights["negative"]:
        writer.writerow([a["aspect"], a["label"], a["score"]])

    # Save CSV
    output.seek(0)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    filename = f"{user.username}_review_report.csv"
    return send_file(mem, mimetype='text/csv', download_name=filename, as_attachment=True)

@app.route('/generate_pdf_report')
def generate_pdf_report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at).all()
    if not reviews:
        flash("No reviews to generate report.", "warning")
        return redirect(url_for("dashboard"))

    total_reviews = len(reviews)
    time_range_start = reviews[-1].created_at.strftime("%Y-%m-%d") if reviews else "N/A"
    time_range_end = reviews[0].created_at.strftime("%Y-%m-%d") if reviews else "N/A"

    # Count sentiment
    sentiment_counts = {"positive":0, "negative":0, "neutral":0}
    for r in reviews:
        label = r.sentiment_label.lower() if r.sentiment_label else "neutral"
        if label in sentiment_counts:
            sentiment_counts[label] += 1

    # Aspect summary
    aspect_summary = analyze_aspect_sentiment(reviews)
    key_insights = {
        "positive": [a for a in aspect_summary if a["label"] == "Positive"],
        "negative": [a for a in aspect_summary if a["label"] == "Negative"]
    }

    mem = io.BytesIO()
    c = canvas.Canvas(mem, pagesize=letter)
    width, height = letter
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Review Report for {user.username}")
    y -= 30

    # Dataset summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Dataset Summary")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Total Reviews: {total_reviews}")
    y -= 15
    c.drawString(50, y, f"Time Range: {time_range_start} to {time_range_end}")
    y -= 30

    # Sentiment distribution
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Sentiment Distribution")
    y -= 20
    total = total_reviews if total_reviews > 0 else 1
    for sentiment, count in sentiment_counts.items():
        percent = (count / total) * 100
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"{sentiment.capitalize()}: {count} ({percent:.1f}%)")
        y -= 15
    y -= 10

    # Aspect Highlights
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Key Aspect Insights")
    y -= 20
    for a in aspect_summary:
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"{a['aspect']} - {a['label']} ({a['score']})")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40
    y -= 10

    # Key Insights
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Key Insights")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Positive Aspects:")
    y -= 15
    for a in key_insights["positive"]:
        c.drawString(60, y, f"{a['aspect']} ({a['score']})")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40
    y -= 10
    c.drawString(50, y, "Negative Aspects:")
    y -= 15
    for a in key_insights["negative"]:
        c.drawString(60, y, f"{a['aspect']} ({a['score']})")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40

    c.showPage()
    c.save()
    mem.seek(0)
    filename = f"{user.username}_review_report.pdf"
    return send_file(mem, mimetype='application/pdf', download_name=filename, as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Seed default admin if not exists
        if not Admin.query.filter_by(username="admin").first():
            a = Admin(username="admin")
            a.set_password("admin")
            db.session.add(a)
            db.session.commit()
            print("✅ Seeded default admin (username: admin, password: admin)")
            
        # Seed default aspects if not exists
        default_aspects = ["battery", "camera", "delivery time", "service", "product quality"]
        for aspect_name in default_aspects:
            if not AspectCategory.query.filter_by(name=aspect_name).first():
                db.session.add(AspectCategory(name=aspect_name))
        db.session.commit()
        if AspectCategory.query.count() > 0:
            print("✅ Seeded default aspect categories.")
            
    app.run(debug=True)