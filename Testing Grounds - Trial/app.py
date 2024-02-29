"""
Project: CyberSense
Last Edited: 12/1
By: Sean McDerment
Version: 0.0.1
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
from  flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid import SendGridAPIClient
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from leaderboard_app.leaderboard_utils import read_data, create_leaderboard, calculate_department_averages

app = Flask(__name__, template_folder=r'C:\Users\mcder\Desktop\Testing Grounds - Post Email\templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] ='7Loi3RNcylXFwE4QsE3x8iNSuSa'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['UPLOAD_FOLDER'] = r'C:\Users\mcder\Desktop\Testing Grounds - Post Email\uploads'
migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    group = db.Column(db.String(50), name='user_group')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# SendGrid API key
SENDGRID_API_KEY = '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'

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)


pending_emails = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        flash('Login failed. Incorrect username or password.', 'danger')

    return render_template('login.html')
  

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        group = request.form['group']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hashed_password, group=group)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')



@app.route('/send-email', methods=['GET', 'POST'])
@login_required
def send_email():
    to_email = request.form['to']
    sender_email = 'CybersenseTestEmail@gmail.com'
    malicious_intent = request.form['MaliciousIntent']
    social_engineering_tactic = request.form['SocialEngineeringTatic']

    attachment = request.files.get('attachment')

    subject = request.form['subject']  # User subject
    message = Mail()
    message_content = request.form['message']  # user message

    # Set the predefined subject and message only if the user did not input any
    if not subject:
        if malicious_intent == 'harvesting credentials':
            subject = 'Verify Your Account Information'
        elif malicious_intent == 'malicious attachment':
            subject = 'Important Document Attached'
        elif malicious_intent == 'gathering information':
            subject = 'Request for Information'

        if social_engineering_tactic == 'urgency':
            subject = 'Urgent: ' + subject
        elif social_engineering_tactic == 'scarcity':
            subject = 'Last Chance: ' + subject
        elif social_engineering_tactic == 'familiarity':
            subject = 'For Your Attention: ' + subject

    if not message_content:
        if malicious_intent == 'harvesting credentials':
            message_content = 'Dear User, it is imperative to confirm your account credentials immediately.'
        elif malicious_intent == 'malicious attachment':
            message_content = 'Please review the attached document. Your prompt attention is required.'
        elif malicious_intent == 'gathering information':
            message_content = 'We require some information. Kindly provide it at your earliest convenience.'

        if social_engineering_tactic == 'urgency':
            message_content = 'URGENT: ' + message_content
        elif social_engineering_tactic == 'scarcity':
            message_content = 'Limited availability, act now. The document will be removed soon.'
        elif social_engineering_tactic == 'familiarity':
            message_content = 'As discussed earlier, kindly find the requested document.'

    # Set the user-inputted values to the message
    message.plain_text_content = message_content

    if attachment:
        secure_attachment_filename = secure_filename(attachment.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_attachment_filename)

        # Save the file to the specified path
        attachment.save(file_path)

        # Add the file to the email
        with open(file_path, 'rb') as file:
            attachment_content = file.read()
            attachment_content_type = attachment.content_type
            attachment_name = secure_attachment_filename

            # Debugging statements
            print(f"Attachment Content Type: {attachment_content_type}")
            print(f"Attachment File Name: {attachment_name}")

            # Create the attachment
            attachment = Attachment()
            attachment.file_content = FileContent(base64.b64encode(attachment_content).decode())
            attachment.file_name = FileName(attachment_name)
            attachment.file_type = FileType(attachment_content_type)
            attachment.disposition = Disposition('attachment')

            # Add the attachment to the message
            message.attachment = attachment

    else:
        # Handle the case when no attachment is present
        attachment = None 

    # Append to pending_emails regardless of attachment presence
    pending_emails.append({'to_email': to_email, 'sender_email': sender_email, 'subject': subject, 'message': message, 'attachment':attachment})

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
@login_required  # Add this decorator
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
        from_email = email['sender_email']
        to_email = email['to_email']
        subject = email['subject']
        attachment = email['attachment']
        plain_text_content = email['message'].plain_text_content

        try:
            # Create a SendGrid message
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=plain_text_content
            )

            # Attachments
            if attachment is not None:
                message    .add_attachment(attachment)

            # Send the email
            response = sg.send(message)

            if response.status_code == 202:
                print(f'Email to {to_email} sent successfully.')
            else:
                print(f'Failed to send email to {to_email}. Status code: {response.status_code}')

        except Exception as e:
            print(f'Failed to send email to {to_email}: {str(e)}')



@app.route('/leaderboard/')
@login_required
def leaderboard():
    file_path = r'c:\Users\mcder\Desktop\Cybersense_Leaderboard\data\leaderboard_data.csv'
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)