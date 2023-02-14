import streamlit as st
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# Set up Google credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["google_credentials"],
    scopes=["https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents"]
)

# Define the document ID of the template document
TEMPLATE_DOCUMENT_ID = "1UAKsBpDK_AhPtWdV6dL3Wm7kyU2kwnIK5Qh0uYYVTBI"

def update_document(name, url, state):
    # Build the service object for the Google Docs API
    service = build("docs", "v1", credentials=creds)

    # Make a copy of the template document
    copy_title = f"{name}'s Document"
    body = {
        'title': copy_title
    }
    response = service.documents().copy(documentId=TEMPLATE_DOCUMENT_ID, body=body).execute()
    copy_document_id = response.get('documentId')

    # Replace placeholders in the copied document with user inputs
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{Name}}',
                    'matchCase': True
                },
                'replaceText': name,
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{URL}}',
                    'matchCase': True
                },
                'replaceText': url,
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{State}}',
                    'matchCase': True
                },
                'replaceText': state,
            }
        },
    ]
    result = service.documents().batchUpdate(documentId=copy_document_id, body={'requests': requests}).execute()

    # Export the copied document as a PDF
    export_title = f"{name}'s Document.pdf"
    export_uri = f"export?mimeType=application/pdf&fileName={export_title}"
    export_link = f"https://docs.google.com/document/d/{copy_document_id}/{export_uri}"
    return export_link

# Define Streamlit app layout
st.title("Automated Document Creation")
name = st.text_input("Name")
url = st.text_input("URL")
state = st.text_input("State")
if st.button("Create Document"):
    link = update_document(name, url, state)
    st.write(f"Document created! You can download it from [this link]({link}).")
