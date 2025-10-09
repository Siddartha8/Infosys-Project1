Infosys-Project1: Customer Review Insight AI

Customer Review Insight AI
Project Overview
Customer Review Insight AI is an advanced Natural Language Processing (NLP) system developed during the Infosys Internship 6.0 to help businesses extract actionable insights from large volumes of customer reviews. Unlike traditional sentiment analysis, which only delivers an overall positive or negative score, this project performs Aspect-Based Sentiment Analysis (ABSA). It identifies specific product/service attributes (aspects) and determines sentiment (positive, negative, or neutral) for each, offering granular business intelligence.

Key Outcomes & Benefits
Granular Sentiment Insights: Accurately determines sentiment towards specific product or service aspects.

Automated Review Analysis: Reduces manual effort in processing feedback.

Actionable Business Intelligence: Delivers clear, data-driven insights for product/service improvement.

Trend Identification: Highlights sentiment shifts and evolving customer preferences over time.

Scalable & Flexible: Adapted for multiple industries and product categories.

Interactive Visualizations: User-friendly dashboards summarizing complex sentiment data.

Core Features & Modules
NLP Analysis Module

Aspect Extraction: Identifies key attributes in reviews

Overall Sentiment: Scores full review sentiments

Aspect-Based Sentiment: Detects sentiment for each aspect

Data Ingestion & Preprocessing

Upload CSV or text files

Automated text cleaning, tokenization, normalization

Data Aggregation & Insights

Aggregates sentiment scores per aspect across reviews

Identifies most positive/negative aspects

Authentication & Security

JWT-secured user registration and login

Profile management for datasets/reports

Visualization & Reporting

Interactive dashboards with aspect-level sentiment distribution, product/time filtering

Admin dashboard for review categories, system monitoring, and model performance

Technical Architecture & Stack
Category	Technology/Tools
Backend	Flask / Python
NLP Libraries	NLTK, spaCy, Hugging Face Transformers
Visualization	Streamlit, Dash, Plotly
Data Processing	Pandas
Database/ORM	SQLAlchemy, Alembic
Security	JWT Authentication
Deployment	Docker, Cloud Platforms (future)
Implementation Timeline
Milestone 1 (Weeks 1-2):

Secure user authentication with JWT, login, profile management

Enable dataset uploads for customer reviews (CSV, text)

Milestone 2 (Weeks 3-4):

Text preprocessing pipeline using NLTK, spaCy, Hugging Face models

Enhanced UI to display review sentiments

Milestone 3 (Weeks 5-6):

Aspect-based sentiment analysis (rule-based extraction, spaCy parsing)

Sentiment scoring with Hugging Face/VADER, detailed analysis using Pandas

Milestone 4 (Weeks 7-8):

Interactive dashboards with Streamlit/Dash/Plotly

Admin interface for aspect category management

Local Setup & Installation
Prerequisites

Python 3.x

Git

Step 1: Clone and Set Up Environment

bash
git clone https://github.com/Siddartha8/Infosys-Project1.git
cd Infosys-Project1

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate # Windows
Step 2: Install Dependencies

bash
pip install -r requirements.txt
Step 3: Configure NLP Data
If using NLTK for VADER sentiment analysis:

python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
Step 4: Initialize and Migrate Database

bash
alembic upgrade head
Step 5: Run the Application

bash
python app.py
App accessible at address printed in console (e.g., http://127.0.0.1:5000/).

Business Impact & Use Cases
Product Development: Discover features customers love/dislike for targeted improvements.

Service Improvement: Pinpoint service quality issues or pain points.

Marketing Strategy: Shape promotional campaigns around top-rated aspects.

Quality Assurance: Monitor product/service trends and feedback.

Competitive Analysis: Compare sentiment across different categories and competitors.

Target Industries: Consumer Electronics, E-commerce/Retail, Hospitality/Tourism, Financial Services, Healthcare Services.

Team & Supervision
Team Members: Aryan Amit Pardeshi, Vinukollu Hima Janani, Kandadi Siddartha, Akasapu Venkata Sai Manikanta Gangadhar Dharshan.

Supervisor: Mukilan Selvaraj.

Contribution
Contributions are welcome! Please open issues or submit pull requests for improvements.

License
This project is licensed under the MIT License
