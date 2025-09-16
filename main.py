# Standard library
import os
from io import StringIO
from datetime import datetime as dt

# Third-party libraries
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from markupsafe import Markup
import matplotlib
# Configures matplotlib backend. 
# Matplotlib recommends calling this before importing pyplot.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates -- Use if we want more granular date formatting

# Loads .env file, grabs the API key from the .env file
load_dotenv()
AV_KEY = os.getenv("AV_KEY")

# Dictionary to map URL values to data keys from API response
function_mapping = {
    "TIME_SERIES_DAILY" : "Time Series (Daily)",
    "TIME_SERIES_WEEKLY" : "Weekly Time Series",
    "TIME_SERIES_MONTHLY" : "Monthly Time Series"
}

# Create Flask instance
app = Flask(__name__)

# Create database instance, connect to the DB file, get secret key from .env
# Making database file path absolute to ensure I create tables in the same file I open with sqlite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)

# Create user class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    # Password length set to 80 because we don't know how long the hash will be
    password = db.Column(db.String(80), nullable=False)

# Create registration form
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
min=4, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        
        if existing_user_username:
            raise ValidationError("Username taken. Please choose a different one.")
    
# Create login form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
min=4, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Login")


# Flask's route decorator maps URLs to a specific function
@app.route('/')
def index():
    if "error" in request.args:
        return render_template('index.html', error=request.args['error'])
    return render_template("index.html") # Render template serves HTML files dynamically

@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method == 'GET':
        return redirect('/') # Redirects user to root page if they don't use the form
    form_data = request.form
    symbol = form_data["symbol"] # Connected via name attribute in html file
    function = form_data["interval"]

    # Gets company name from the overview API
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}"
    company_overview=requests.get(overview_url).json()

    # Error handling, important if user enters invalid ticker
    if 'Name' not in company_overview:
        return redirect(url_for('index', error="Invalid ticker"))
    
    company_name = company_overview["Name"]

    # This URL will return a JSON file with stock data
    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={AV_KEY}"

    # Grabs data from API, converts the data in the response object to JSON
    stock_data = requests.get(url).json()

    # Converts interval to proper format, grabs all data and puts it into time_series
    func_key = function_mapping[function]
    time_series = stock_data[func_key]

    dates = []
    prices = []

    # Accesses dates & prices as tuples using .items(), stores them in relevant lists
    # Converts dates from strings before storing
    for date, price in time_series.items():
        formatted_date = dt.strptime(date, "%Y-%m-%d").date()
        dates.append(formatted_date)
        prices.append(float(price['4. close']))

    dates.reverse()
    prices.reverse()

    graph = get_graph(dates, prices, company_name)

    return render_template("info.html", info={
        "company_name": company_name,
        "symbol": symbol,
        "graph": Markup(graph)
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    logForm = LoginForm()
    return render_template("login.html", form=logForm)

@app.route('/register', methods=['GET', 'POST'])
def register():
    regForm = RegisterForm()
    return render_template("register.html", form=regForm)

# Helper function to create graph
def get_graph(dates, prices, company_name):
    fig, ax = plt.subplots(figsize=(8, 6))
 
    ax.xaxis.set_tick_params(rotation=45)
    ax.set_title(f"Stock Price of {company_name}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Price (USD)")
    ax.plot(dates, prices)
 
    buf = StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
 
    return buf.getvalue()

if __name__ == '__main__':
    app.run(debug=True)