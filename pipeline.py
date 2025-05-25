import os
import json
import imaplib
import email
from dotenv import load_dotenv
from transformers import pipeline
import mysql.connector
from datetime import datetime

load_dotenv()

# Config
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# Hugging Face NER model
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def connect_email():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_USER, EMAIL_PASS)
    imap.select("inbox")
    return imap

def fetch_emails(imap, max_emails=10):
    status, messages = imap.search(None, 'ALL')
    email_ids = messages[0].split()[-max_emails:]
    result = []
    
    for eid in email_ids:
        res, msg = imap.fetch(eid, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject = msg["subject"]
                date = msg["date"]
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                result.append({"subject": subject, "date": date, "body": body})
    return result

def extract_info(text):
    entities = ner(text)
    company = role = status = "Unknown"

    for ent in entities:
        label = ent.get("entity_group")
        word = ent["word"]
        if label == "ORG" and company == "Unknown":
            company = word
        if label == "MISC" and role == "Unknown":
            role = word

    return {
        "company_name": company,
        "role_applied_for": role,
        "date_applied": datetime.now().date().isoformat(),
        "status": "Applied",
        "days_since_update": 0
    }

def insert_to_db(data):
    conn = mysql.connector.connect(
        host="localhost",
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cursor = conn.cursor()
    query = """
        INSERT INTO job_application
        (company_name, role_applied_for, date_applied, status, days_since_update)
        VALUES (%s, %s, %s, %s, %s)
    """
    for d in data:
        cursor.execute(query, (
            d["company_name"],
            d["role_applied_for"],
            d["date_applied"],
            d["status"],
            d["days_since_update"]
        ))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    imap = connect_email()
    emails = fetch_emails(imap)
    extracted = [extract_info(email["body"]) for email in emails]
    insert_to_db(extracted)
    print("✅ All emails processed and saved to DB.")

if __name__ == "__main__":
    main()