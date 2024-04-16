from flask import Flask, request, jsonify, session, flash, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Issue
from extensions import db  # Import db from extensions
from datetime import datetime
# from sqlalchemy import func


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)


@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/passError')
def passError():
    flash("Passwords don't match!") 
    return render_template('error/passError.html')

@app.route('/userError')
def userError():
    flash("Username doesn't exist, register user!!") 
    return render_template('error/passError.html')


""" USER MANAGEMENTS ENDPOINTS """
##########################################################################################
"""USER REGISTER ENDPOINT """
@app.route('/register', methods=['POST'])
def register():
    print(request.form)
    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    roles = data.get('role')
    print(roles)

    confirm_password = data.get('confPass')



    #validate that the password is equal to confirmed pass!
    if password != confirm_password:
        return redirect(url_for('passError'))
    
    # Validate the received data
    if not data or not name or not email or not password:
        return jsonify(message="Name, email, and password are required!"), 400

    # Check if the email is already in use
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify(message="Email is already in use!"), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create a new user
    new_user = User(name=name, email=email, password=hashed_password, zip_code=95120, role=roles)

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    session['user_name'] = name  # Store user name in session
    session['email'] = email

    return redirect(url_for('dashboard', email=email))


""" USER LOGIN ENPOINT """
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    #print(data)

    if not email or not password:
        return jsonify(message="Email and password are required!"), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return redirect(url_for('userError'))

    if not check_password_hash(user.password, password):
        return jsonify(message="Incorrect password!"), 401

    session['user_id'] = user.user_id # Replace with actual data retrieval logic
    session['user_name'] = user.name  # Store user name in session
    session['email'] = email
    return redirect(url_for('dashboard', email=email))




"""USER PROFILE ENDPOINT """
@app.route('/profile', methods=['GET'])
def get_profile():
    # Ensure the user is logged in
    if 'user_id' not in session:
        return jsonify(message="Please log in to view profile."), 401

    user = User.query.get(session['user_id'])

    # Check if the user exists in the database (this should always be true, but it's good to check)
    if not user:
        return jsonify(message="User not found!"), 404

    user_data = {
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'zip_code': user.zip_code,
        'registration_date': user.registration_date.strftime('%Y-%m-%d %H:%M:%S') if user.registration_date else None,
        'total_points': user.total_points
    }

    return jsonify(profile=user_data)

##########################################################################################

"""ISSUE REPORTING ENDPOINTS"""
##########################################################################################

@app.route('/request-money', methods=['GET'])
def request_money():
    return render_template('request-money.html')


@app.route('/submit-request', methods=['POST'])
def submit_request():
    amount = request.form.get('amount')
    reason = request.form.get('reason', '')
    # Add logic to handle the request, e.g., store in database, send email, etc.
    # For now, let's just print it to the console
    print(f"Request submitted for: ${amount}. Reason: {reason}")

    # Optionally, flash a message to the user
    flash('Your request has been submitted to HR for review.', 'success')

    # Redirect the user to another page, such as the dashboard
    return redirect(url_for('emp_dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    email = session.get('email')
    print(email)
    user = User.query.filter_by(email=email).first()
    role = user.role
    if role == 'hr':
        return redirect(url_for('hr_dashboard', email=email))
    else:
        return redirect(url_for('emp_dashboard', email=email))

@app.route('/hr_dashboard', methods=['GET'])
def hr_dashboard():
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    requests = [
        {'employee_email': 'yash1@berkeley.edu', 'amount': '1000', 'reason': 'Investments', 'status': 'Pending'},
        {'employee_email': 'darren1@babson.com', 'amount': '100', 'reason': 'Advance for rent', 'status': 'Approved'}
    ]
    
    return render_template('hr_dashboard.html', user_name=user.name, requests=requests)

@app.route('/emp_dashboard', methods=['GET'])
def emp_dashboard():
    
    email = session.get('email')
    print(email)
    user = User.query.filter_by(email=email).first()
    return render_template('emp_dashboard.html', user_name=user.name)


@app.route('/report', methods=['GET', 'POST'])
def report_form():
    if request.method == 'POST':
        # Handle the form submission logic here
        pass
    return render_template('issue_reporting.html')

@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    if request.method == 'POST':
        return jsonify(message="Logged out successfully!")
    return render_template('logout.html')


if __name__ == "__main__":
    app.run(debug=True)
