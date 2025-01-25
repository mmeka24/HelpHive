#imports
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

MONGO_URI = "mongodb+srv://laylashihab60:wjTBf97MWxJYKLlo@helphive.avdab.mongodb.net/?retryWrites=true&w=majority&appName=HelpHive"

client = MongoClient(MONGO_URI)
db = client["HelpHive"]  # Replace <dbname> with the name of your database
users_collection = db.loginInfo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the user exists and verify password
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
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
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)