#imports
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, RadioField
from wtforms.validators import DataRequired, EqualTo
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


MONGO_URI = "mongodb+srv://laylashihab60:z2UArTlgodej8UPq@helphive.avdab.mongodb.net/?retryWrites=true&w=majority&appName=HelpHive"


client = MongoClient(MONGO_URI)
db = client["HelpHive"]
users_collection = db.loginInfo
reports_collection = db.reports

loggedInUser = ""

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
class UpdateProfileForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
class IncidentReportForm(FlaskForm):
    category = SelectField("Category", choices=[('1', 'Snowstorm'),
                                                ('2', 'Fire'), 
                                                ('3', 'Drought'), 
                                                ('4', 'Accident'), 
                                                ('5', 'Tornado'), 
                                                ('6', 'Icy'), 
                                                ('7', 'Available Resources')
                                                ])
    resources = RadioField("Resources Needed", choices=[('1', 'Yes'), ('2', 'No')])
    severity = RadioField("Severity", choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()


    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data


        # Check if the user exists and verify password
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):


            #if the login is successful, stores username as a global variage
            global loggedInUser
            loggedInUser = username


            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')


    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()


    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password)


        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        # Insert the new user into the database
        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })
        global loggedInUser
        loggedInUser = username

        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))


    return render_template('register.html', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UpdateProfileForm()
    session.pop('_flashes', None)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # finds user document
        global loggedInUser
        document = users_collection.find_one({"username": loggedInUser})

        if document:
            stored_password = document["password"]

            if form.password.data == "":
                hashed_password = stored_password
            else:
                hashed_password = generate_password_hash(password)

        oldvalues = {"username":loggedInUser, "password":document["password"]}
        newvalues = { "$set": { "username": username, "password":hashed_password } }

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            flash('Username already exists', 'danger')
            return redirect(url_for('profile'))
        else:
            # updates the new values
            users_collection.update_one(oldvalues,newvalues)

        flash('Changes Saved!', 'success')
        loggedInUser = username


    return render_template('profile.html', form=form)

@app.route('/incidentReport', methods=['GET', 'POST'])
def incidentReport():
    form = IncidentReportForm()

    global loggedInUser

    currentUser = users_collection.find_one({"username": loggedInUser})

    print(currentUser['_id'])

    if form.validate_on_submit():
        category = request.form['category']
        resources = request.form['resources']
        severity = request.form['severity']

        report = {
            "user-id": ObjectId(currentUser['_id']),
            "category": category,
            "resources": resources,
            "severity": severity,
            "timestamp": datetime.utcnow()
        }

        reports_collection.insert_one(report)
        flash("success!", 'success')

    return render_template('incidentReport.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)