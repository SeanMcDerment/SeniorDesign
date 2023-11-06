from flask import Flask, render_template, request
import os
import sendgrid
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# Your SendGrid API key
SENDGRID_API_KEY = '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'

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    to_email = request.form['to']
    sender_email = 'CybersenseTestEmail@gmail.com'  # Replace with your email
    subject = request.form['subject']
    message = request.form['message']

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
