from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import os
import threading
from flask_cors import CORS
from dotenv import load_dotenv
import tiktoken
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
import traceback
import random
import smtplib
from datetime import datetime, timedelta
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"]=openai_api_key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI1') # PostgreSQL
# engine = sqlalchemy.create_engine(os.getenv('SQLALCHEMY_DATABASE_URI2'))
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@someaitools.com'
app.config['MAIL_SERVER']='mail.someaitools.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'maxloo@someaitools.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD0')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

summary_status = {}
db = SQLAlchemy(app) # PostgreSQL
mail = Mail(app)
from server import mail
# Base = declarative_base()
# Session = sqlalchemy.orm.sessionmaker()
# Session.configure(bind=engine)
# Session = Session()

class Users(db.Model): # PostgreSQL
    email = db.Column(db.String(120), primary_key=True)
    password_hash = db.Column(db.String(128))
    email_authenticated = db.Column(db.Boolean, default=False)
    login_authenticated = db.Column(db.Boolean, default=False)
    confirmation_code = db.Column(db.Integer)
    confirmation_code_time = db.Column(db.DateTime)
# class Users(Base):
#     __tablename__ = 'users'
#     email = sqlalchemy.Column(sqlalchemy.String(120), primary_key=True)
#     password_hash = sqlalchemy.Column(sqlalchemy.String(128))
#     email_authenticated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
#     login_authenticated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
#     confirmation_code = sqlalchemy.Column(sqlalchemy.Integer)
#     confirmation_code_time = sqlalchemy.Column(sqlalchemy.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_confirmation_code(self):
        self.confirmation_code = random.randint(100000, 999999)

def summarize_background(file_path, filename):
    global summary_status
    summary_status[filename] = {'status': 'processing'}
    try:
        summary = summarize_pdf(file_path, filename)
        summary_status[filename] = {'status': 'completed', 'summary': summary}
    except Exception as e:
        summary_status[filename] = {'status': 'error', 'error': str(e)}

def summarize_pdf(file_path, filename):
    try:
        # Read the uploaded file content into a bytes-like object
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split()
        # Process only the first two pages
        docs_two_pages = docs[:2]
        summaries = []
        text_splitter1=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_splitter2=RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
        text_splitter3=RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=800)
        llm=ChatOpenAI(model_name="gpt-3.5-turbo-1106")
        for page_number, page_text in enumerate(docs_two_pages, start=1):
            word_count = len(str(page_text).split())
            texts1 = text_splitter1.split_text(str(page_text))
            texts2 = text_splitter2.split_text(str(page_text))
            texts3 = text_splitter3.split_text(str(page_text))
            chain1 = load_summarize_chain(llm, chain_type="map_reduce")
            chain2 = load_summarize_chain(llm, chain_type="stuff")
            chain3 = load_summarize_chain(llm, chain_type="refine")

            temp = chain1.run(text_splitter1.create_documents(texts1))
            page_summary = f"(Summary One: {len(str(temp).split())} words)\n" + temp
            # temp = chain1.run(text_splitter2.create_documents(texts2))
            # page_summary = page_summary + "\n\n" + f"(Summary: {len(str(temp).split())} words)\n" + temp
            # temp = chain1.run(text_splitter3.create_documents(texts3))
            # page_summary = page_summary + "\n\n" + f"(Summary: {len(str(temp).split())} words)\n" + temp

            # temp = chain2.run(text_splitter1.create_documents(texts1))
            # page_summary = page_summary + "\n\n" + f"(Summary: {len(str(temp).split())} words)\n" + temp
            temp = chain2.run(text_splitter2.create_documents(texts2))
            page_summary = page_summary + "\n\n" + f"(Summary Two: {len(str(temp).split())} words)\n" + temp
            # temp = chain2.run(text_splitter3.create_documents(texts3))
            # page_summary = page_summary + "\n\n" + f"(Summary: {len(str(temp).split())} words)\n" + temp
            
            # temp = chain3.run(text_splitter1.create_documents(texts1))
            # page_summary = page_summary + "\n\n" + f"(Summary: {len(str(temp).split())} words)\n" + temp
            # temp = chain3.run(text_splitter2.create_documents(texts2))
            # page_summary = page_summary + "\n\n" + f"(Summary: {len(str(temp).split())} words)\n" + temp
            temp = chain3.run(text_splitter3.create_documents(texts3))
            page_summary = page_summary + "\n\n" + f"(Summary Three: {len(str(temp).split())} words)\n" + temp

            summaries.append(f"Page {page_number} (Original Word Count: {word_count}): {page_summary}\n\n\n")
        combined_summary = '  '.join(summaries)
        all_combined = "Summary of " + filename + ":\n\n" + combined_summary
        total = all_combined
    except Exception as e:
        # Print the stack trace to the console
        print(traceback.format_exc())
        # Optionally, return the error message to the Gradio interface
        return f"An error occurred: {str(e)}"
    return total

@app.route('/login-signup', methods=['POST'])
def login_signup():
    data = request.json
    user_email = data.get('userEmail')
    password = data.get('password')
    # Fetch user from the database
    user = Users.query.filter_by(email=user_email).first()
    # Check if user exists
    if user:
        # Existing user, check password
        if user.check_password(password):
            # Password matches, login success
            return jsonify({'status': 'login_success'}), 200
        else:
            # Password does not match
            return jsonify({'status': 'login_failed'}), 200
    else:
        # New user, create account and send confirmation code
        new_user = Users(email=user_email)
        new_user.set_password(password)
        new_user.set_confirmation_code()
        new_user.confirmation_code_time = datetime.utcnow()
        db.session.add(new_user)
        db.session.commit()
        # Send email with confirmation code (configure Flask-Mail to use this)
        msg = Message('Some AI Tools - Confirm your Login account', sender='no-reply@someaitools.com', recipients=[user_email])
        msg.body = f'Your confirmation code is: {new_user.confirmation_code}'
        try:
            mail.send(msg)
        except smtplib.SMTPServerDisconnected as e:
            print(f"Failed to send email: {e}")
        return jsonify({'status': 'signup_in_progress'}), 200
    # return jsonify({'status': 'signup_in_progress'}), 200

@app.route('/confirm', methods=['POST'])
def confirm():
    try:
        data = request.json
        user_email = data.get('userEmail')
        confirmation_code = data.get('confirmationCode')
        user = Users.query.filter_by(email=user_email).first()
        if user:
            time_diff = datetime.utcnow() - user.confirmation_code_time  # Assuming confirmation_code_time is stored in UTC
            if time_diff > timedelta(minutes=5):
                db.session.delete(user)  # Remove the user's record
                db.session.commit()
                return jsonify({'status': 'confirmation_failed_timeout'}), 200  # 408 Request Timeout

            if user.confirmation_code == confirmation_code:
                # Correct confirmation code and within the time limit
                user.email_authenticated = True
                db.session.commit()
                return jsonify({'status': 'confirmation_success'}), 200
            else:
                print("wrong confirmation code")
                db.session.delete(user)  # Remove the user's record
                db.session.commit()
                return jsonify({'status': 'confirmation_failed'}), 200
        else:
            # User doesn't exist
            return jsonify({'status': 'user_not_found'}), 200
    except Exception as e:
        print("Error in confirm:", e)
        return jsonify({'status': 'internal_error', 'message': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Start summarization in a background thread
        threading.Thread(target=summarize_background, args=(file_path, filename)).start()
        return jsonify({'status': 'uploaded', 'filename': filename}), 200

@app.route('/status/<filename>', methods=['GET'])
def get_status(filename):
    status = summary_status.get(filename, {'status': 'unknown'})
    return jsonify(status)

if __name__ == "__main__":
    app.run(debug=True)
