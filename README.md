Infosys-Project1: Customer Review Insight AI

Customer Review Insight AI


Project Overview
Customer Review Insight AI is an advanced Natural Language Processing (NLP) platform developed for transforming raw customer feedback into granular, actionable business intelligence. Unlike general sentiment systems, this project leverages Aspect-Based Sentiment Analysis (ABSA) to extract and analyze sentiment tied to specific product or service features, revealing what customers actually think about individual aspects (e.g., “battery,” “delivery,” “support”).

What Problem Does It Solve?
Volume and Complexity: Businesses often have thousands of reviews, making manual assessment virtually impossible.

Lack of Nuance: Basic sentiment tools only offer an overall rating, missing out on what features are liked or disliked.

Slow Reaction: Without fine-grained insights, product or service teams can’t rapidly address what matters most to customers.

Key Features & Modules
NLP Analysis Module
Aspect Extraction: Automatically identifies and extracts key product/service aspects from unstructured text (e.g., “screen,” “battery life,” “customer service”).

Aspect-Based Sentiment Detection: Determines if each aspect is mentioned positively, negatively, or neutrally using rule-based methods and deep learning models.

Overall Sentiment Scoring: Provides a sentiment summary for each review as a fallback or supplement.

Explainability: Includes transparency methods (e.g., SHAP values or attention heatmaps) to clarify why a sentiment was assigned, supporting trust and actionable data.

Data Ingestion & Preprocessing
Upload reviews via CSV or raw text files.

Automated text cleaning: tokenization, normalization, spelling correction, lemmatization/stemming, stopword removal, punctuation and digit stripping, and casing normalization.

Supports named entity recognition (optional) for further customization.

Interactive UI options for batch and single review analysis.

Data Aggregation & Insights
Aggregates aspect sentiment scores across all inputs for robust reporting.

Ranks and highlights most positively/negatively discussed aspects.

Trends: Tracks sentiment shifts over time for products/aspects, powering early detection of emerging issues or strengths.

Authentication & Security
JWT-based Authentication: Secure registration/login for all users and administrators.

Profile Management: Each user has a personal dashboard to manage analyses, data uploads, and reports.

Role-Based Access: Admin interface for managing categories and monitoring usage.

Visualization & Reporting
Live Dashboards: Interactive charts (Streamlit/Dash/Plotly) showing sentiment distributions by aspect, product, or over time.

Filtering: Drill down by product, aspect, or any timestamp for focused reporting.

Downloadable Reports: Export results as CSV or PDF for sharing or further analytics.

Admin Dashboard
Aspect Management: Define, edit, or merge aspect categories.

Monitoring: Track system usage, performance stats, review counts, and positive/negative/neutral distributions.

Quality Assurance: Review model and analysis quality with downloadable logs and reports.

Technology Architecture & Stack
Layer/Feature	Technology/Library	Role
Backend	Flask / Python	API and core server logic
NLP Processing	NLTK, spaCy, Hugging Face Transformers	Text preprocessing, aspect extraction, sentiment modeling
Data Processing	Pandas	Data cleansing, transformation, aggregation
Visualization	Streamlit / Dash / Plotly	Dashboards, charts, interactive reporting
Database/ORM	SQLAlchemy, Alembic	Data persistence, schema migrations, ORM layer
Security	JWT	Securing user authentication and sessions
Deployment	Docker, cloud infrastructure (future)	Containerization and scalable deployment
Implementation Timeline
Milestone	Weeks	Deliverables
Milestone 1	1–2	User management/authentication via JWT; Data upload UI
Milestone 2	3–4	Preprocessing pipeline (tokenization, lemmatization, etc.), enhanced review UI
Milestone 3	5–6	Aspect extraction (spaCy/rule-based); Sentiment detection (VADER/Hugging Face)
Milestone 4	7–8	Interactive dashboards; Admin category management interface
Local Setup and Installation
Prerequisites
Python 3.x

Git

SQLite (default) or compatible RDBMS

(Optional) Docker for containerized deployments

1. Clone and Set Up Environment
bash
git clone https://github.com/Siddartha8/Infosys-Project1.git
cd Infosys-Project1
python -m venv venv


source venv/bin/activate  # macOS/Linux


# .\venv\Scripts\activate # Windows


2. Install Dependencies
bash
pip install -r requirements.txt



4. Configure NLP Data
If using NLTK for VADER, initialize required datasets:

python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')


4. Initialize and Migrate Database
Ensure the schema is ready:

bash
alembic upgrade head


5. Run the Application
bash
python app.py
The local app will be available at the address shown in your terminal.

Example Usage
Sign up/login: Create an account or use admin credentials to access advanced controls.

Upload reviews: Use the dashboard to import customer reviews in CSV/text formats.

Run analysis: The system preprocesses and analyzes for aspects/sentiment, showing live stats.

View/download reports: Customize dashboard views, visualize insights, and export CSV/PDF results.

Admin (optional): Monitor user activity, update aspect categories, and track system performance.

Business Impact & Use Cases
Product Development: Pinpoint exactly which features are loved or disliked, fueling rapid, targeted improvements.

Service Improvement: Uncover recurring pain points in customer support or logistics.

Marketing Strategy: Clearly identify “hero” aspects for promotional focus.

Quality Assurance: Monitor real-time feedback for regression or improvement signals.

Competitor Benchmarking: Compare internal sentiment to market/industry baselines for strategic edge.

Target Industries
Consumer Electronics

E-commerce & Retail

Hospitality & Tourism

Entertainment & Media

Healthcare Services

Financial Services

Project Screenshots
Login/Register Page: Basic and secure forms for authentication.

User Profile: Manage uploads, review status, and download past reports.

Analytics Dashboard: Visualizes sentiment distributions, trends over time, and most discussed aspects.

Admin Panel: Review total usage, monitor recent activity, download systemwide reports, adjust configurations.

Team & Supervision
Team Members: Aryan Amit Pardeshi, Vinukollu Hima Janani, Kandadi Siddartha, Akasapu Venkata Sai Manikanta Gangadhar Dharshan

Supervisor: Mukilan Selvaraj

Contribution
Contributions via pull requests or issues are encouraged! Please see CONTRIBUTING.md or open an issue for help

License
This project is licensed under the MIT License
