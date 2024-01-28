"""
Project: CyberSense
Last Edited: 12/1
By: Sean McDerment
"""
from flask import Flask, render_template, request, redirect, url_for
import os
import sendgrid
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from leaderboard_app.leaderboard_utils import read_data, create_leaderboard, calculate_department_averages
   


app = Flask(__name__, template_folder=r'C:\Users\nxiao\Desktop\Testing Grounds - Trial\templates', static_folder='static')


# SendGrid API key
SENDGRID_API_KEY = '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'

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

pending_emails = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
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
# The Different Message and Subject for each Intent 
    if malicious_intent == 'harvesting credentials':
        subject = 'Verify Your Account Information'
        message = 'Dear User, it is imperative to confirm your account credentials immediately.'

    elif malicious_intent == 'malicious attachment':
        subject = 'Important Document Attached'
        message = 'Please review the attached document. Your prompt attention is required.'

    elif malicious_intent == 'gathering information':
        subject = 'Request for Information'
        message = 'We require some information. Kindly provide it at your earliest convenience.'

# The Different Message and Subject for each tatic
    if social_engineering_tactic == 'urgency':
        subject = 'Urgent: ' + subject
        message = 'URGENT: ' + message

    elif social_engineering_tactic == 'scarcity':
        subject = 'Last Chance: ' + subject
        message = 'Limited availability, act now. The document will be removed soon.'

    elif social_engineering_tactic == 'familiarity':
        subject = 'For Your Attention: ' + subject
        message = 'As discussed earlier, kindly find the requested document.'

    pending_emails.append({'to_email': to_email, 'sender_email': sender_email, 'subject': subject, 'message': message})
# Response when the user presses the SEND EMAIL button
    response_html = """
    <p>Email sent for approval by admin</p>
    <form action="/admin" method="get">
        <button type="submit">Go to Admin</button>
    </form>
    """
    
    return response_html
# Needs to rely on a database so emails will save across sessions
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form['action']

        if action == 'Approve':
            # Send the approved emails to the user specified
            send_approved_emails()

        # Clear the pending emails list after processing. Needs Change to not clear unresolved emails 
        pending_emails.clear()

    return render_template('admin.html', pending_emails=pending_emails)

def send_approved_emails():
    for email in pending_emails:
        message = Mail(
            from_email=email['sender_email'],
            to_emails=email['to_email'],
            subject=email['subject'],
            plain_text_content=email['message']
        )
#Error Handling if the the email sends or not
        try:
            response = sg.send(message)
            if response.status_code == 202:
                print(f'Email to {email["to_email"]} sent successfully.')
            else:
                print(f'Failed to send email to {email["to_email"]}. Status code: {response.status_code}')
        except Exception as e:
            print(f'Failed to send email to {email["to_email"]}: {str(e)}')

@app.route('/leaderboard/')
def leaderboard():
    file_path = r'c:\Users\nxiao\Desktop\Cybersense_Leaderboard\data\leaderboard_data.csv'
    data = read_data(file_path)

    # Apply filters
    user_filter = request.args.get('user')
    department_filter = request.args.get('department')

    filtered_data = apply_filters(data, user_filter, department_filter)

    if department_filter:
        department_averages = calculate_department_averages(data)
        sorted_averages = sorted(department_averages.items(), key=lambda x: x[1], reverse=True)
        return render_template('leaderboard.html', leaderboard=filtered_data, department_averages=sorted_averages)

    sorted_data = create_leaderboard(filtered_data)
    return render_template('leaderboard.html', leaderboard=sorted_data)
# Filteres based on users or Departments.
def apply_filters(data, user_filter, department_filter):
    filtered_data = data

    if user_filter:
        filtered_data = [entry for entry in filtered_data if entry['username'] == user_filter]

    if department_filter:
        filtered_data = [entry for entry in filtered_data if entry['department'] == department_filter]

    return filtered_data

if __name__ == '__main__':
    app.run(debug=True)