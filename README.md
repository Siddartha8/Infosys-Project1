Infosys-Project1: Customer Review Insight AI
📌 Project Overview

Customer Review Insight AI is an advanced Natural Language Processing (NLP) system developed during the Infosys Internship 6.0 that addresses the challenge of manually extracting actionable insights from large volumes of customer reviews.



Unlike traditional sentiment analysis, which provides only an overall positive or negative score , this project performs Aspect-Based Sentiment Analysis (ABSA). The goal is to identify specific features or attributes (aspects) and determine the sentiment (positive, negative, or neutral) associated with each one , providing granular, data-driven insights for businesses.



Team Members & Supervision

Team Members: Aryan Amit Pardeshi , Vinukollu Hima Janani , Kandadi Siddartha , Akasapu Venkata Sai Manikanta Gangadhar Dharshan.





Supervisor: Mukilan Selvaraj.

✨ Core Features & Functionality
The application is structured around the following key modules and features:

NLP Analysis Module:


Aspect Extraction: Identify key aspects/features mentioned in reviews.


Overall Sentiment Analysis: General sentiment score for the entire review.


Aspect-Based Sentiment: Accurately identifies sentiment (positive, negative, neutral) towards specific aspects.

Data Ingestion & Preprocessing:

Interface for uploading review datasets (CSV, text files).

Automated text cleaning, tokenization, and normalization.

Data Aggregation & Insight Generation:

Aggregate sentiment scores per aspect across multiple reviews.

Identify top positive/negative aspects.

Authentication & Security:

User registration and login secured with JWT Authentication.


Profile management for datasets and analysis reports.

Visualization & Reporting:

Interactive dashboards with aspect-level sentiment distribution.


Filter capabilities by aspect, product, or time.

Admin Dashboard:

Management of review categories/industries.

System usage and performance monitoring.

🛠️ Technical Architecture & Stack 

Category	Technology	Files/Dependencies
Backend Framework		
Flask / Python 

app.py, templates/
NLP Libraries		
NLTK, spaCy, Hugging Face Transformers 

utils/sentiment.py, utils/text_utils.py
Visualization		
Streamlit, Dash, or Plotly 

Interactive dashboards and reporting.
Data Processing		
Pandas 

Data cleaning, aggregation, and insight generation.
Database/ORM		
SQLAlchemy (with Alembic migrations) 

models.py, instance/, migrations/
Security		
JWT Authentication 

For securing user and admin sessions.
Deployment	
Docker, Cloud Platforms (Future) 


Export to Sheets
📅 Implementation Timeline
The project was executed across four milestones over approximately 8 weeks:

Milestone 1 (Weeks 1-2): Developed secure user authentication with JWT, login, and profile management. Enabled review data upload via Flask/Streamlit supporting CSV and text inputs.


Milestone 2 (Weeks 3-4): Implemented a text preprocessing pipeline with NLTK, spaCy, and Hugging Face models. Enhanced the UI to display review sentiments.



Milestone 3 (Weeks 5-6): Implemented aspect-based sentiment analysis using rule-based extraction and spaCy parsing. Analyzed aspect sentiments with Hugging Face, VADER, and Pandas.



Milestone 4 (Weeks 7-8): Created interactive dashboards with Streamlit, Dash, or Plotly to show sentiment trends over time. Developed an admin interface for managing aspect categories.


💻 Local Setup and Installation
Prerequisites
Python 3.x

Git

Step 1: Clone and Set Up Environment
Bash

git clone https://github.com/Siddartha8/Infosys-Project1.git
cd Infosys-Project1

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate # Windows
Step 2: Install Dependencies
Bash

pip install -r requirements.txt
Step 3: Configure NLP Data
If the project uses NLTK for VADER sentiment analysis, run the following to download necessary data:

Bash

python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
exit()
Step 4: Initialize and Migrate Database
Apply the database schema defined in models.py using Alembic:

Bash

alembic upgrade head
Step 5: Run the Application
Start the Flask server:

Bash

python app.py
The application will be accessible at the address printed in your console (e.g., http://127.0.0.1:5000/).

📊 Business Impact & Use Cases 

This system is designed to transform customer feedback into strategic intelligence for various target industries  and applications:


Product Development: Identify features customers love or dislike.


Service Improvement: Understand service quality pain points.


Marketing Strategy: Focus campaigns on positive aspects.


Quality Assurance: Monitor product/service quality trends.


Target Industries: Consumer Electronics , E-commerce & Retail , Hospitality & Tourism , Financial Services , and Healthcare Services.





🤝 Contribution
Contributions are welcome! Please feel free to open issues or submit pull requests.

📄 License
This project is licensed under the [Specify your license, e.g., MIT License] - see the LICENSE file for details.
