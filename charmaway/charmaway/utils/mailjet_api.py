import os
from mailjet_rest import Client

def send_mail_via_mailjet(subject, html_content, recipients):
    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_SECRET_KEY")
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    data = {
      'Messages': [
        {
          "From": {
            "Email": "charmaway88@gmail.com",
            "Name": "Charmaway"
          },
          "To": [{"Email": r, "Name": ""} for r in recipients],
          "Subject": subject,
          "HTMLPart": html_content
        }
      ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code, result.json()