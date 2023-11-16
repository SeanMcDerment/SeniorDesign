from flask import Flask, render_template, request
import os
import sendgrid
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# Your SendGrid API key
SENDGRID_API_KEY = '' # Put API Key Here

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    to_email = request.form['to']
    sender_email = 'CybersenseTestEmail@gmail.com'      
    malicious_intent = request.form['MaliciousIntent']
    social_engineering_tactic = request.form['SocialEngineeringTatic']

    subject = ""
    message = ""
# Prompts
    if malicious_intent == 'harvesting credentials':
        subject = 'Urgent: Verify Your Account Information'
        message = 'Dear User, it is imperative to confirm your account credentials immediately.'

    elif malicious_intent == 'malicious attachment':
        subject = 'Important Document Attached'
        message = 'Please review the attached document. Your prompt attention is required.'

    elif malicious_intent == 'gathering information':
        subject = 'Request for Information'
        message = 'We require some information. Kindly provide it at your earliest convenience.'


    if social_engineering_tactic == 'urgency':
        subject = 'Urgent: ' + subject
        message = 'URGENT: ' + message

    elif social_engineering_tactic == 'scarcity':
        subject = 'Last Chance: ' + subject
        message = 'Limited availability, act now. The document will be removed soon.'

    elif social_engineering_tactic == 'familiarity':
        subject = 'For Your Attention: ' + subject
        message = 'As discussed earlier, kindly find the requested document.'


    message = Mail(
        from_email=sender_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=message)

    try:
        response = sg.send(message)
        if response.status_code == 202:
            return 'Email sent successfully'
        else:
            return 'Failed to send email', response.status_code
    except Exception as e:
        return f'Failed to send email: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)

