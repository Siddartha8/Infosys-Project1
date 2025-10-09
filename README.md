Infosys-Project1: Customer Review Insight AI
📌 Project Overview

Customer Review Insight AI is an advanced Natural Language Processing (NLP) system developed during the Infosys Internship 6.0 that addresses the challenge of manually extracting actionable insights from large volumes of customer reviews.


Unlike traditional sentiment analysis, which only provides an overall positive or negative score, this project performs Aspect-Based Sentiment Analysis (ABSA). The goal is to identify specific product features or attributes (aspects) and determine the sentiment (positive, negative, or neutral) associated with each one, providing granular, data-driven insights for businesses.


Team Members & Supervision

Team Members: Aryan Amit Pardeshi, Vinukollu Hima Janani, Kandadi Siddartha, Akasapu Venkata Sai Manikanta Gangadhar Dharshan.


Supervisor: Mukilan Selvaraj.

✨ Core Features & Functionality
The application is structured around the following key modules and features:

Module	Features	Benefit
NLP Analysis Module		
Aspect Extraction, Overall Sentiment Analysis, and Aspect-Based Sentiment Analysis using Hugging Face, VADER, and spaCy.


Provides granular sentiment insights towards specific aspects.

Data Ingestion	
Interface for uploading review datasets in CSV or text file format.


Automated Review Analysis to significantly reduce manual effort.

Authentication & Security	
User registration and login secured with JWT Authentication.




Secure management of user profiles, datasets, and analysis reports.

Visualization & Reporting		
Interactive dashboards (built with Streamlit, Dash, or Plotly) showing sentiment trends over time and aspect-level distribution.



Delivers Actionable Business Intelligence in a digestible format.



Admin Dashboard	
Management of review categories/industries, system usage monitoring, and review of analysis quality.



Enables effective system maintenance and strategic management of aspect categories.


Export to Sheets
🛠️ Technical Architecture & Stack
The project relies on a powerful and modern Python stack:

Category	Technology	Files/Dependencies
Backend Framework		
Flask / Python 

app.py, templates/
NLP Libraries		
NLTK, spaCy, Hugging Face Transformers 

utils/sentiment.py, utils/text_utils.py
Visualization		
Streamlit, Dash, or Plotly 

Used for interactive dashboards and reporting.
Data Processing		
Pandas 

Used for data cleaning, aggregation, and insight generation.


Database/ORM		
SQLAlchemy  (with Alembic migrations)

models.py, instance/, migrations/
Security		
JWT Authentication 

For securing user and admin sessions.
Deployment	
Docker, Cloud Platforms (Future) 


Export to Sheets
📅 Implementation Timeline
The project was executed across four distinct milestones (weeks 1-8):

Milestone	Weeks	Key Activities
Milestone 1	
Weeks 1-2 

Developed secure user authentication with JWT, login, and profile management. Enabled review data upload via Flask/Streamlit supporting CSV and text inputs.



Milestone 2	
Weeks 3-4 

Implemented a text preprocessing pipeline with NLTK and spaCy. Enhanced the UI to display review sentiments.


Milestone 3	
Weeks 5-6 

Implemented aspect-based sentiment analysis using rule-based extraction and spaCy parsing. Analyzed aspect sentiments with Hugging Face, VADER, and Pandas.


Milestone 4	
Weeks 7-8 


Created interactive dashboards with Streamlit/Dash/Plotly to show sentiment trends over time. Developed the admin interface for managing aspect categories.



Export to Sheets
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
If NLTK is used for preprocessing or VADER, run the following to download necessary data:

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
Start the Flask server.

Bash

python app.py
The application will be accessible at the address printed in your console (e.g., http://127.0.0.1:5000/).

📊 Application Use Cases
This system is designed to transform customer feedback into strategic intelligence for target industries:


Product Development: Identify features customers love or dislike.


Service Improvement: Understand service quality pain points.


Marketing Strategy: Focus campaigns on positive aspects.


Quality Assurance: Monitor product or service quality trends.


Target Industries: Consumer Electronics, E-commerce & Retail, Hospitality & Tourism, Financial Services, and Healthcare Services.

🤝 Contribution
Contributions are welcome! Please feel free to open issues or submit pull requests.

📄 License
This project is licensed under the [Specify your license, e.g., MIT License] - see the LICENSE file for details.
