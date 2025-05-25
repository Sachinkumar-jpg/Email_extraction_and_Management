# 🧠 AI-Powered Job Application Tracker

The **AI-Powered Job Application Tracker** streamlines job application management by automatically reading emails, extracting key details using NLP, and storing them in a structured database. It helps users track application statuses, improve resumes based on job descriptions, and stay organized throughout the job search journey.

---

## 🚀 Features

- 📥 Automatically reads job-related emails from your inbox.
- 🧠 Uses Hugging Face + PyTorch models to extract:
  - Company name
  - Role applied for
  - Date of application
  - Application status
  - Days since last update
- 🗂️ Stores extracted data in a MySQL database.
- 🌐 REST API built with Spring Boot (Java).
- 💻 Frontend-ready (Bootstrap) for UI extension.
- 🔐 Future-ready for cloud deployment.

---

## 🛠 Tech Stack

| Layer         | Technology                     |
|---------------|--------------------------------|
| NLP Extraction| Python, Hugging Face, PyTorch |
| Backend API   | Java, Spring Boot             |
| Database      | MySQL                          |
| Frontend UI   | Bootstrap (optional extension) |
| Email Reading | Python IMAP                    |

---

## 📦 Project Structure

```bash
project-root/
│
├── emailExtractor/             # Python scripts
│   ├── main.py                 # Reads inbox and extracts info
│   ├── extract.py              # Hugging Face + PyTorch NER
│   └── insert_to_mysql.py     # Insert JSON into MySQL
│
├── jobtracker-backend/        # Java Spring Boot backend
│   ├── src/main/java/
│   └── pom.xml
│
└── README.md



---------------------------------------------------------------------------
Phase 1: Email Reader + NLP (Python)
✅ Requirements
	Python 3.9+

	PyTorch

	Transformers

	imaplib, email

	mysql-connector-python

▶️ Steps
	Create and activate a virtual environment:

		python -m venv venv
		venv\Scripts\activate
Install dependencies:

		pip install torch transformers mysql-connector-python
		Set email credentials and MySQL config inside main.py.

Run:

	python main.py
	python pipeline.py

☕ Phase 2: Spring Boot Backend (Java)
✅ Requirements
	JDK 17+

	Maven

	MySQL running locally

▶️ Steps
Go to the backend directory:

	cd jobtracker-backend
Run:

	mvn spring-boot:run
Access API:

	http://localhost:8080/api/applications
🧪 API Testing with Postman
🔹 GET /api/applications
	URL: http://localhost:8080/api/applications

Response: List of job applications.

🔹 POST /api/applications
	URL: http://localhost:8080/api/applications

Body (JSON):

json
{
  "companyName": "Google",
  "roleApplied": "Software Engineer",
  "applicationDate": "2025-04-10",
  "status": "Submitted",
  "lastUpdated": "2025-04-12"
}.


🎯 Phase 3 Goal
Create a simple web-based UI to:

	View all job applications

	Add a new application

	Refresh the list

tools required

	HTML/CSS	UI structure + styling
	Bootstrap	Pre-built styling + layout
	JavaScript	Fetch API calls to backend
	VS Code	Editor for HTML/JS
	Spring Boot API	Already running backend

structure

frontend/
├── index.html
├── style.css        
└── app.js

--------------------------------------end-------------------------------------------