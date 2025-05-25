from __future__ import print_function
import os
import os.path
import base64
import requests
from email import message_from_bytes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope (read-only)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Hugging Face API config
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/philschmid/bart-large-cnn-samsum"
HUGGING_FACE_API_TOKEN = "use your hugging face APItoken"  

def get_gmail_service():
    """Authenticate and return Gmail service object"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def analyze_email_with_ai(email_body):
    """Send email body to Hugging Face model and extract structured info"""
    prompt = f"""
You are an AI assistant that extracts structured job application information from emails.

Extract the following fields in JSON format:
- type: confirmation | update | other
- company: Company name mentioned
- role: Job title mentioned
- date: Date of application or update (if mentioned)

Respond only with the JSON format.

Email:
\"\"\"
{email_body}
\"\"\"
"""


    ''' prompt = f"""
You are an AI assistant for analyzing job application emails.

Based on the following email, identify:
- type: "confirmation" or "update" or "other"
- company: name of the company mentioned
- role: the job title mentioned
- date: the date of the application or update

Respond only in this JSON format:
{{
  "type": "confirmation | update | other",
  "company": "...",
  "role": "...",
  "date": "YYYY-MM-DD"
}}

Email:
\"\"\"
{email_body}
\"\"\"
"""'''

    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": prompt
    }

    response = requests.post(HUGGING_FACE_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and isinstance(result[0], dict):
            return result[0].get("generated_text") or result[0].get("summary_text") or str(result[0])
        else:
            return str(result)
    else:
        return f"❌ Hugging Face API error: {response.status_code} - {response.text}"

def read_unread_emails():
    """Fetch unread emails and analyze them using Hugging Face AI"""
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])

    if not messages:
        print("✅ No unread emails found.")
        return

    for msg in messages[:5]:  # Limit to 5 for testing
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw_msg = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        mime_msg = message_from_bytes(raw_msg)

        subject = mime_msg['Subject']
        sender = mime_msg['From']

        body = ""
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode()
        else:
            body = mime_msg.get_payload(decode=True).decode()

        print("\n📩 New Email:")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Body Preview: {body.strip()[:300]}")

        # 🔍 Analyze using Hugging Face
        try:
            ai_response = analyze_email_with_ai(body.strip())
            print("\n🤖 AI Response:")
            print(ai_response)
        except Exception as e:
            print(f"❌ Error during AI analysis: {e}")

if __name__ == '__main__':
    read_unread_emails()
