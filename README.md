# 🤖 Customer Review Insight AI

## 📝 Project Overview
Customer Review Insight AI is an Infosys internship project that uses Artificial Intelligence and Natural Language Processing (NLP) to analyze customer feedback at a fine-grained, aspect level.  
It goes beyond basic sentiment scoring, delivering exactly which product/service features are loved or criticized—enabling actionable improvements and strategic business insights.

---

## 🎯 Objectives
- Classify reviews as Positive, Negative, or Neutral, both overall and by aspect.
- Automatically extract frequent aspects, topics, and keywords from customer feedback.
- Visualize satisfaction trends, aspect rankings, and sentiment flows for business clarity.
- Provide a scalable, accurate, and AI-powered review insight platform suitable for any industry.

---

## 🧠 Features
- 🧹 Text Preprocessing: Tokenization, stopword removal, lemmatization, normalization.
- 🏷️ Aspect Extraction: Identifies features using rule-based and NLP methods (battery, service, delivery, etc.).
- 🔍 Aspect-Based Sentiment Analysis: Positive/negative/neutral scoring for each aspect.
- 🚦 General Sentiment Analysis: Summarized sentiment for each review.
- 📊 Visualization: Dashboards showing aspect distributions, trends, and keyword clouds.
- 🛡️ Authentication & Security: JWT-secured registration/login, profile and report management.
- 📈 Performance Metrics: Accuracy, confusion matrix, user analytics.
- 🌐 (Optional) Flask web app for interactive analyses and reporting.
- 👨‍💼 Admin Dashboard: Category management, system monitoring, and advanced analytics.

---

## 🧰 Tech Stack
| Component         | Technologies Used                           |
|-------------------|--------------------------------------------|
| Language          | Python                                     |
| Libraries         | NLTK, spaCy, Hugging Face Transformers, Pandas |
| Visualization     | Streamlit, Dash, Plotly                    |
| Database          | SQLAlchemy, Alembic, SQLite                |
| Security          | JWT Authentication                         |
| Environment       | VS Code, Jupyter Notebook, Docker          |
| API/UI            | Flask / Streamlit                          |
| Version Control   | Git & GitHub                               |

---

## 📂 Project Structure
Customer_Review_Insight_AI/  
│  
├── __pycache__/  
├── .vscode/  
├── instance/  
├── migrations/  
│   ├── __pycache__/  
│   ├── versions/  
│   ├── alembic.ini  
│   ├── env.py  
│   ├── README  
│   └── script.py.mako  
├── static/  
│   ├── images/  
│   └── styles.css  
├── templates/  
│   ├── admin_dashboard.html  
│   ├── admin_login.html  
│   ├── base.html  
│   ├── dashboard.html  
│   ├── login.html  
│   ├── register.html  
│   └── select_login.html  
├── uploads/  
├── utils/  
├── app.py  
├── models.py  
├── requirements.txt  
├── test/  
├── test_utils.py  
├── view_reviews.py  
├── env  
└── README.md  

---

## 🚀 Future Enhancements
- Integrate transformer models (BERT / RoBERTa) for deeper aspect-level accuracy.
- Add real-time review collection from APIs and social media.
- Enable multilingual sentiment analysis.
- Deploy a full-stack enterprise analytics dashboard for business ops.
- Scale via Docker and cloud platforms for robust enterprise use.

---

## 👩‍💻 Team & Supervision
**Team Members:**  
Aryan Amit Pardeshi  
Vinukollu Hima Janani  
Kandadi Siddartha  
Akasapu Venkata Sai Manikanta Gangadhar Dharshan  
**Supervisor:** Mukilan Selvaraj

---

## 💼 Business Impact & Use Cases
- Product Development: See which features customers truly care about.
- Service Improvement: Pinpoint pain points and recurring satisfaction issues.
- Marketing Strategy: Tailor campaigns to top-performing aspects.
- Quality Assurance: Track feedback changes, regressions, and improvements.
- Competitive Analysis: Benchmark sentiment for products/services and industries.
- Supported Industries: Consumer Electronics, E-commerce, Hospitality, Media, Healthcare, Financial Services.

---

## 📝 How to Run Locally

**1. Clone the repo:**  

git clone https://github.com/Siddartha8/Infosys-Project1.git
- cd Infosys-Project1

**2. Create and activate environment:**  
- python -m venv venv
- source venv/bin/activate # On Windows: .\venv\Scripts\activate

**3. Install requirements:**  
- pip install -r requirements.txt

**4. Download NLTK resources:**  
- import nltk
- nltk.download('vader_lexicon')
- nltk.download('punkt')

**5. Initialize the database:**  
- alembic upgrade head

**6. Run the app:**  
- python app.py

Visit: http://127.0.0.1:5000/ or the address shown in your console.

---

## 🎓 Author
Kandadi Siddartha  
Final Year B.Tech (CSE)   
Sree Dattha Institute of Engineering and Science, Hyderabad  
[siddharthakandadi@gmail.com](mailto:siddharthakandadi@gmail.com)  
LinkedIn: [https://linkedin.com/in/siddartha-kandadi-90593326b](https://linkedin.com/in/siddarthakandadi)

---

*For questions or contributions, open an issue or pull request!*
















