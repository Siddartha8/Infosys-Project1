📌 Project Overview
This is a comprehensive web application designed to collect, store, and analyze user reviews using Sentiment Analysis. It provides dedicated interfaces for both standard users (for submission and viewing personal history) and administrators (for system-wide monitoring and data management).

The application is built using the Python ecosystem, adhering to a modular structure for scalability and maintainability.

✨ Key Features
Secure User & Admin Authentication: Separate login and registration flows for users and system administrators.

Database Management: Uses SQLite for data persistence, with Alembic ensuring safe and version-controlled database migrations.

Sentiment Analysis Engine: A core utility module that processes raw text input and determines its emotional tone (e.g., Positive, Negative, Neutral).

Modular Design: Clear separation between web logic (app.py), database models (models.py), and utility functions (utils/).

Dedicated Dashboards: Separate user interface designs for general users (dashboard.html) and system admins (admin_dashboard.html).

🛠️ Technology Stack
Category	Technology	Key Components
Backend	Python 3.x	app.py, models.py, utils/
Web Framework	Flask or Django (Inferred)	Routing and Template Rendering (templates/)
Database	SQLite	Stored in instance/admin.db and instance/reviews.db
DB Migrations	Alembic	migrations/, alembic.ini, env.py
NLP/ML	NLTK / TextBlob / scikit-learn (Inferred)	utils/sentiment.py, utils/text_utils.py
Frontend	HTML5, CSS, Jinja Templating	templates/, static/

Export to Sheets
🚀 Getting Started
Follow these steps to set up and run the project locally.

Prerequisites
Ensure you have Python 3.x and pip (the Python package installer) installed on your system.

Step 1: Clone the Repository
Bash

git clone https://github.com/Siddartha8/Infosys-Project1.git
cd Infosys-Project1
Step 2: Set Up the Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

Bash

# Create the environment
python -m venv venv

# Activate the environment
# For macOS/Linux:
source venv/bin/activate
# For Windows (Command Prompt/PowerShell):
.\venv\Scripts\activate
Step 3: Install Dependencies
All necessary packages are defined in requirements.txt.

Bash

pip install -r requirements.txt
Step 4: Configure NLP Resources (If using NLTK)
If the sentiment.py module uses NLTK, you may need to download specific data files:

Bash

python
# Inside the Python interpreter, run:
import nltk
nltk.download('vader_lexicon') # If VADER is used
nltk.download('punkt') # Common requirement
exit()
Step 5: Initialize the Database
The project uses Alembic to manage the database schema.

Run Migrations: Apply the existing schema definitions to create the tables in your database files (admin.db, reviews.db):

Bash

alembic upgrade head
Note: This command will read the migration scripts in the migrations/versions folder and create the necessary tables defined in models.py inside the instance/ folder.

Step 6: Run the Application
Start the web server using the main application file:

Bash

python app.py
The application should now be running, typically accessible at: http://127.0.0.1:5000/ (check your console output for the exact address).

🗺️ Project Structure Guide
File/Folder	Description
app.py	Main Application Logic. Contains all Flask routes, handles HTTP requests, and orchestrates calls to utilities and models.
models.py	Database Schema. Defines the SQLAlchemy models (e.g., User, Review) for the application data.
requirements.txt	Lists all required Python packages.
templates/	Web Pages. Stores all Jinja HTML files, including base.html, dashboard.html, and all authentication pages.
static/	Frontend Assets. Contains CSS, JavaScript, and images for styling the application.
instance/	Local Database. Holds the actual SQLite files (admin.db, reviews.db). This folder should be ignored by Git.
migrations/	Database Versioning. Contains Alembic configuration (alembic.ini) and version scripts for managing schema changes.
utils/	Custom Logic. A Python package containing helper modules:
   sentiment.py	The module containing the core sentiment analysis algorithm or model loading.
   text_utils.py	Helper functions for cleaning and preparing text data before analysis.

Export to Sheets
✍️ How to Contribute
We welcome contributions to the project!

Fork the repository.

Create a feature branch (git checkout -b feature/NewFeature).

Commit your changes (git commit -m 'Add new feature').

Push to the branch (git push origin feature/NewFeature).

Open a Pull Request describing your changes.

📄 License
This project is licensed under the [Specify your license, e.g., MIT License] - see the LICENSE file for details.
