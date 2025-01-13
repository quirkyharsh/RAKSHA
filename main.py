from flask import Flask, request, redirect, url_for, render_template, flash, Response
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.voice_response import VoiceResponse
import time


# Twilio credentials
account_sid = 'ACCOUNTSIDCODE'
auth_token = 'ACCOUNTTOKEN'
client = Client(account_sid, auth_token)

# Flask app setup
app = Flask(__name__)
app.secret_key = 'harshsangrampatil'

# Function to make a call
def make_call_and_check_status(to_number):
    try:
        call = client.calls.create(
            to=to_number,
            from_='TWILIOPHONENUMBER',
            url='https://NGROKURLLINK-free.app/voice',
            status_callback='https://NGROKURLLINK-free.app/status',
            status_callback_event=['completed']
        )
        print(f"Call initiated. Call SID: {call.sid}")
        return call.sid
    except TwilioRestException as e:
        print(f"Failed to make a call: {e}")
        return None

# Function to send a notification
def send_notification(message, to_number):
    try:
        notification = client.messages.create(
            body=message,
            from_='TWILIOPHONENUMBER',
            to=to_number
        )
        print(f"Notification sent. Message SID: {notification.sid}")
    except TwilioRestException as e:
        print(f"Failed to send notification: {e}")

# Home page
@app.route('/home')
def home():
    return render_template("index.html")

# Root redirect to home
@app.route('/')
def index():
    return redirect(url_for('home'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_phone_no = request.form.get('user_phone_no')
        emergency_no = request.form.get('emergency_no')

        if not user_phone_no:
            flash("User phone number is required.", "danger")
            return redirect(url_for('login'))

        call_sid = make_call_and_check_status(user_phone_no)
        if call_sid:
            flash(f"Call initiated with SID: {call_sid}", 'success')
        else:
            flash("Failed to initiate call. Please try again.", 'danger')

        return redirect(url_for('home'))

    return render_template('login.html')

# Voice response route
@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    response.say(
        "Are you safe? Press 1 for Yes, 9 for No. If you don't want further calls, press 3.",
        voice='alice'
    )
    response.gather(num_digits=1, action='/gather', method='POST')
    return Response(str(response), mimetype='text/xml')

# Delayed action for periodic calls
def periodic_call(to_number):
    while True:
        time.sleep(300)  # Wait 5 minutes
        call_sid = make_call_and_check_status(to_number)
        print(f"Periodic call triggered. Call SID: {call_sid}")

# Gather response
@app.route('/gather', methods=['POST'])
def gather():
    digits = request.form.get('Digits')
    response = VoiceResponse()
    user_phone_no = request.form.get('user_phone_no')

    if digits == '1':
        response.say("Thank you for confirming. Stay safe!")
    elif digits == '9':
        response.say("Help is on the way. Stay calm.")
        emergency_no = request.form.get('emergency_no')
        if emergency_no:
            send_notification("Your relative is in danger!", emergency_no)
    elif digits == '3':
        response.say("Glad to know you are safe. No further calls will be made.")
    else:
        response.say("Invalid input. Please try again.")
        response.redirect('/voice')

    return Response(str(response), mimetype='text/xml')

# Call status route
@app.route('/status', methods=['POST'])
def call_status():
    call_status = request.form.get('CallStatus')
    call_sid = request.form.get('CallSid')
    print(f"Call {call_sid} ended with status: {call_status}")
    return Response("Status received", 200)

# Emergency SOS
@app.route('/sos', methods=['POST'])
def sos():
    emergency_no = request.form.get('emergency_no')

    if not emergency_no:
        flash("Emergency contact number is missing.", "danger")
        return redirect(url_for('home'))

    try:
        call = client.calls.create(
            to=emergency_no,
            from_='+12242930840',
            url='https://NGROKURLLINK-free.app/voice'
        )
        flash(f"Emergency call initiated to {emergency_no}. Call SID: {call.sid}", "success")
    except TwilioRestException as e:
        flash(f"Failed to make SOS call: {e}", "danger")

    return redirect(url_for('home'))

# Additional routes for features
@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
