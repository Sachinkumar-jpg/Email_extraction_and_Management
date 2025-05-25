import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from transformers import pipeline
import torch

# --- Configuration ---
EMAIL = "skumar843096@gmail.com"
APP_PASSWORD = "axgd cydl jwdc lfoy"  # Replace with your actual app password

# --- Connect to Gmail ---
def connect_to_gmail():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL, APP_PASSWORD)
    imap.select("inbox")
    return imap

# --- Fetch Emails ---
def fetch_emails(imap, num_emails=50):
    status, messages = imap.search(None, 'ALL')
    email_ids = messages[0].split()[-num_emails:]
    emails = []

    for eid in email_ids:
        res, msg_data = imap.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                subject = subject.decode(encoding or "utf-8") if isinstance(subject, bytes) else subject

                # Get sender domain
                from_address = msg.get("From")
                match = re.search(r"@([\w.-]+)", from_address)
                sender_domain = match.group(1).split('.')[0].capitalize() if match else "Unknown"

                # Get date received
                date_tuple = email.utils.parsedate_tz(msg['Date'])
                received_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime("%Y-%m-%d")

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain" or content_type == "text/html":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode(errors='ignore')
                                break
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')

                if "<html" in body:
                    soup = BeautifulSoup(body, "html.parser")
                    body = soup.get_text()

                # Filter out non-job-related emails
                if is_job_related(subject, body):
                    emails.append({"subject": subject, "body": body, "sender_domain": sender_domain, "date_received": received_date})
    return emails

# --- Check if Email is Job-Related ---
def is_job_related(subject, body):
    job_keywords = [
        "job", "application", "interview", "offer", "position", "role", "hiring", "career", "resume", "candidate", "recruitment"
    ]
    subject = subject.lower()
    body = body.lower()

    # Check if any of the keywords are found in the subject or body
    for keyword in job_keywords:
        if keyword in subject or keyword in body:
            return True
    return False

# --- Load NER Model ---
device = 0 if torch.cuda.is_available() else -1
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", device=device)

# --- Info Extraction ---
def extract_info(email_data):
    text = email_data['body']
    sender_domain = email_data['sender_domain']
    received_date = email_data['date_received']

    entities = ner_pipeline(text)
    org_entities = [ent["word"].replace("##", "") for ent in entities if "ORG" in ent["entity"] or "PER" in ent["entity"] or "MISC" in ent["entity"]]

    company_name = extract_company_name(text) or sender_domain or "Unknown"
    role = guess_role(text)
    status = guess_status(text, role)

    return {
        "company_name": company_name,
        "date_applied": received_date,
        "days_since_update": calculate_days_since(received_date),
        "role_applied_for": role,
        "status": status
    }

# --- Helpers ---
def extract_company_name(text):
    match = re.search(r"applied to\s+(.*?)(?:\s+at|\s*[\-–—_.])", text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def guess_role(text):
    patterns = [
        r"applied to\s+(.*?)(?:\s+at|\s*\.)",
        r"applied for the position of\s+(.*?)(?:\s+at|\s*\.)",
        r"application for\s+(.*?)(?:\s+at|\s*\.)",
        r"position of\s+(.*?)(?:\s+at|\s*\.)",
        r"role of\s+(.*?)(?:\s+at|\s*\.)",
        r"applied to\s+.*?[\-–—_]\s*(.*?)(?:\s*\.)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            role = match.group(1).strip()
            role = re.sub(r"[_\-]+", " ", role)
            role = re.sub(r"\s+", " ", role)
            return role

    job_keywords = ["Engineer", "Developer", "Analyst", "Manager", "Executive", "Designer", "Consultant", "Intern"]
    ner_result = ner_pipeline(text)
    job_words = [
        ent["word"].replace("##", "") for ent in ner_result
        if ent["entity"] == "B-MISC" and any(keyword.lower() in ent["word"].lower() for keyword in job_keywords)
    ]
    if job_words:
        return " ".join(job_words).strip()

    return "Unknown"

def guess_status(text, role_found):
    text = text.lower()

    status_patterns = {
        "Rejected": [
            r"\bnot selected\b",
            r"\bunsuccessful\b",
            r"\brejected\b",
            r"we (apologize|apologise).*?(sorry|regret) to inform you",
            r"sorry to inform you",
            r"we regret to inform you",
            r"unfortunately.*?not (been )?selected",
            r"after careful consideration.*?(we (will not|won't) move forward|not moving forward)",
        ],
        "Interview Scheduled": [r"\binterview\b", r"\bmeeting\b", r"\bscheduled\b"],
        "Shortlisted": [r"\bshortlisted\b", r"\bselected for next round\b"],
        "Pending": [r"\bunder review\b", r"\bpending\b", r"\bwaiting\b"],
        "Applied": [
            r"\bthank you for applying\b",
            r"\byou'?ve applied\b",
            r"\byour application has been received\b"
        ]
    }

    for status, patterns in status_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return status

    if role_found and role_found.lower() != "unknown":
        return "Applied"

    if "congratulations" in text or "welcome" in text:
        return "Shortlisted"

    return "Unknown"

def calculate_days_since(date_str):
    applied_date = datetime.strptime(date_str, "%Y-%m-%d")
    return (datetime.today() - applied_date).days

# --- Main ---
def main():
    imap = connect_to_gmail()
    emails = fetch_emails(imap)
    extracted_data = []

    for email_data in emails:
        print(f"\n📨 Subject: {email_data['subject']}")
        extracted = extract_info(email_data)
        print(f"✅ Extracted: {extracted}")
        extracted_data.append(extracted)

    with open("email_applications.json", "w") as f:
        json.dump(extracted_data, f, indent=2)

    print("\n📁 Saved data to email_applications.json")
    imap.logout()

if __name__ == "__main__":
    main()
