#imports
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, RadioField
from wtforms.validators import DataRequired, EqualTo
from bson.objectid import ObjectId
from datetime import datetime, timezone
import requests

import sys


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


MONGO_URI = "mongodb+srv://laylashihab60:z2UArTlgodej8UPq@helphive.avdab.mongodb.net/?retryWrites=true&w=majority&appName=HelpHive"


client = MongoClient(MONGO_URI)
db = client["HelpHive"]
users_collection = db.loginInfo
reports_collection = db.reports

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
                                                ], 
                                                validators=[DataRequired()])
    resources = RadioField("Resources Needed", choices=[('1', 'Yes'), ('2', 'No')], validators=[DataRequired()])
    severity = RadioField("Severity", choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], validators=[DataRequired()])
    streetAddress = StringField('Street Address', validators=[DataRequired()])
class DeleteReport(FlaskForm):
    report = SelectField("Report",validators=[DataRequired()])
    

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data


        # Check if the user exists and verify password
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):


            #if the login is successful, stores username 
            session['loggedInUser'] = username


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

        session['loggedInUser'] = username

        # Insert the new user into the database
        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })

        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))


    return render_template('register.html', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/userReports', methods=["GET", "POST"])
def userReports():
    form = DeleteReport()

    loggedInUser = session.get('loggedInUser')

    if loggedInUser:

        # finds user's report documents
        loggedInUser = session.get('loggedInUser')
        reports_docs = reports_collection.find({"username":loggedInUser}) 

        docs_list = []
        #iterates through report documents
        for doc in reports_docs: 
            docs_list.append(doc)
        
        reports = docs_list

        CATEGORY_MAPPING = {
            '1': 'Snowstorm',
            '2': 'Fire',
            '3': 'Drought',
            '4': 'Accident',
            '5': 'Tornado',
            '6': 'Icy',
            '7': 'Available Resources'
        }

        choiceList = {}

        # translates all categories into words 
        count = 1
        for report in reports:
            report['category'] = CATEGORY_MAPPING[report['category']]
            choiceList[report["_id"]] = str(count) + ":\t" + str(report["category"]) + ":\t" + str(report["address"]) 
            count += 1
        
        form.report.choices = [(key, value) for key, value in choiceList.items()]

        if form.validate_on_submit():
            toDeleteValue = request.form['report']  # Get the selected report
            reports_collection.delete_one({"_id": ObjectId(toDeleteValue)})  # Use `toDelete` to delete
            flash('Report Deleted!', 'success')
            return redirect(url_for('userReports'))

                
    return render_template('userReports.html', form =form)

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

    loggedInUser = session.get('loggedInUser')

    if loggedInUser:
        if form.validate_on_submit():
            category = request.form['category']
            resources = request.form['resources']
            severity = request.form['severity']
            timestamp = datetime.now(timezone.utc)

            result = is_valid_address(request.form['streetAddress'])
            check = result[0]
            lat = result[1]
            lng = result[2]
            if check:
                address = request.form['streetAddress']
            elif not check:
                flash('Invalid Address', 'danger')
                return redirect(url_for('incidentReport'))
            
            report = {
                "username":loggedInUser,
                "category": category,
                "resources": resources,
                "severity": severity,
                "timestamp": timestamp,
                "address": address,
                "lat":lat,
                "lng":lng
            }

            reports_collection.insert_one(report)
            flash("Report Submitted!", 'success')
            return redirect(url_for('incidentReport'))

    return render_template('incidentReport.html', form=form)

def is_valid_address(address):
    api_key = "8757fcae3af24a7e88298e5841a4ddaf"  
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    # Check if the API returned results
    if data['results']:
        # Get the first result
        result = data['results'][0]

        # Check confidence level (e.g., minimum threshold of 8)
        confidence = result.get('confidence', 0)
        components = result.get('components', {})

        if confidence >= 3.5 and 'road' in components:
            fulladdress = address + ", West Lafayette, IN, 47907"
            lat,lng = get_geocode(fulladdress, api_key)
            if (lng < -86.7014 and lng > -87.0067) and (lat > 40.3008 and lat < 40.5102):
                return (True, lat, lng)
    # No results indicate an invalid address
    res = (False, 1,1)
    return res

def get_geocode(address, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return lat, lng
    else:
        return 1, 1

if __name__ == '__main__':
    app.run(debug=True)