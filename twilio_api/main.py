import os
from flask import Flask, session, request, flash, redirect, url_for, render_template
from dotenv import load_dotenv
from twilio.rest import Client
import requests
load_dotenv()
app = Flask(__name__)
app.secret_key = 'secret'
twilio_client = Client()
otp_generate_url = 'https://api.generateotp.com/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('generate.html')
    phone_number = request.form['phone_number']
    
    formatted_phone_number = phone_number[1:]
    session['phone_number'] = formatted_phone_number
    response = make_otp_request(formatted_phone_number)
    data = response.json()
    otp_code = str(data["code"])
    send_otp_code(phone_number, otp_code)
    flash('Otp has been generated successfully', 'success')
    
    return redirect(url_for('validate'))


@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'GET':
        return render_template('validate.html')
    otp_code = request.form['otp_code']
    response = verify_otp_code(otp_code, session["phone_number"])
    session.pop('phone_number', None)
    data = response.json()
    if data['status']:
        flash(data['message'], 'success')
    else:
        flash(data['message'],'danger')
    return redirect(url_for('index'))

def verify_otp_code(otp_code, phone_number):
    response = requests.post(f"{otp_generate_url}/validate/{otp_code}/{phone_number}")
    return response


def make_otp_request(phone_number):
    response = requests.post(f"{otp_generate_url}/generate", data={'initiator_id': phone_number})
    return response


def send_otp_code(phone_number, otp_code):
    return send_otp_via_sms(phone_number, otp_code)


def send_otp_via_sms(number, code):
    twilio_client.messages.create(to=f"{number}", from_=os.getenv('TWILIO_NUMBER'), body=f"Your one time password is {code}")



if __name__ == '__main__':
    app.run(debug=True)
