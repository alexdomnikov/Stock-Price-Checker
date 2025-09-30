# TODO: Check if user hit API rate limits when they access info, check for other possible API errors, add button/function to delete name from watchlist

# Standard library
import os
from io import StringIO
from datetime import timedelta, datetime as dt

# Third-party libraries
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
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

# Initialize bcrypt to enable password hashing and verification
bcrypt = Bcrypt(app)

# login_manager allows our app to work with flask to handle logging in
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create user class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    # Password length set to 80 because we don't know how long the hash will be
    password = db.Column(db.String(80), nullable=False)

    # Creates a relationship with the watchlist model to easily access a user's watchlist
    watchlist = db.relationship('Watchlist', backref='owner', lazy='dynamic')

# Create watchlist class. Could've stored info as a JSON, but this allows users to add/delete a stock without 
# having to read the entire dictionary from the database, modify it, then add the modified dictionary back.
class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key will link the watchlist to the user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)

    date_retrieved = db.Column(db.DateTime, nullable=True)
    price_today = db.Column(db.Float)
    price_yesterday = db.Column(db.Float)
    price_year_ago = db.Column(db.Float)

# Create an authentication form - we're going to use this for both registering and logging in
class AuthForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    
    login_submit = SubmitField("Login")
    register_submit = SubmitField("Register")

    def validate_username(self, username):
        # We'll use this during a registration attempt
        # We'll handle the login directly in the login route
        pass

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
    form = AuthForm()
    error = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # ***LOGIN LOGIC***
        if form.login_submit.data:
            # First check if user is in database
            user = User.query.filter_by(username=username).first()
            
            # If user is in the database, check password hash
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                error = "Failed login attempt. Username or password incorrect."

        # ***REGISTRATION LOGIC***
        elif form.register_submit.data:
            # Check if username is taken
            existing_user = User.query.filter_by(username=username).first()
        
            if existing_user:
                error = "Username taken. Please choose a different one."
            else:
                hashed_password = bcrypt.generate_password_hash(form.password.data)
                new_user = User(username = username, password = hashed_password)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user) # Log user in automatically, direct to dashboard.
                return redirect(url_for('dashboard')) 
        
    return render_template("login.html", form=form, error=error)

# Creating a route for the dashboard, which is only available if logged in
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    error = None
    # ADD STOCK LOGIC (POST request)
    if request.method == 'POST':
        symbol = request.form['symbol'].upper()

        # 1. Check if watchlist is full (max 5 since this is just a simple project)
        if current_user.watchlist.count() >= 5:
            error = "Watchlist is full. You can only have up to 5 stocks."
        # 2. Check if stock is already in the watchlist
        elif any(stock.symbol == symbol for stock in current_user.watchlist):
            error = f"{symbol} is already in your watchlist."
        else:
            # 3. Validate ticker by checking if the API returns a company name
            overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}"
            overview_data = requests.get(overview_url).json()
            
            # User might encounter an error where they've hit an API call limit
            if "Information" in overview_data or "Note" in overview_data:
                error = overview_data.get("Note") or overview_data.get("Information")
            elif 'Name' not in overview_data or overview_data['Name'] is None:
                error = f"'{symbol}' is not a valid stock symbol."
            else:
                # 4. Fetch historical data for the new stock
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={AV_KEY}"
                response = requests.get(url).json()
                time_series = response.get("Time Series (Daily)")
                
                prices = get_relevant_prices(time_series) if time_series else None
                
                if prices:
                    # 5. Create new Watchlist entry and add to DB
                    new_stock = Watchlist(
                        user_id=current_user.id,
                        symbol=symbol,
                        date_retrieved=dt.utcnow(),
                        price_today=prices["today"],
                        price_yesterday=prices["yesterday"],
                        price_year_ago=prices["year_ago"]
                    )
                    db.session.add(new_stock)
                    db.session.commit()
                    return redirect(url_for('dashboard')) # Redirect to clear form
                else:
                    # Adding check for API call limit error
                    if "Information" in response or "Note" in response:
                        error = overview_data.get("Note") or overview_data.get("Information")
                    else:
                        error = f"Could not retrieve price data for {symbol}."

    # DISPLAY WATCHLIST LOGIC (GET request)
    # Always update prices before displaying the dashboard
    update_stock_prices(current_user)
    
    # Retrieve the (now updated) watchlist from the database
    user_watchlist = current_user.watchlist.all()

    return render_template("dashboard.html", watchlist=user_watchlist, error=error)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Helper function to create graph for when users look up a single name on the homepage
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

# Helper function to find the closest available trading day in the past. 
# This will be used when we add names to watchlists and when we update them on login.
def get_closest_date(time_series, target_date):
    while target_date.strftime('%Y-%m-%d') not in time_series:
        target_date -= timedelta(days=1)
    return target_date.strftime('%Y-%m-%d')

# Helper function to parse API data and retrieve relevant prices
def get_relevant_prices(time_series):
    try:
        # Get the 2 most recent dates in the time series
        latest_date_str = sorted(time_series.keys(), reverse=True)[0]
        previous_date_str = sorted(time_series.keys(), reverse=True)[1]

        # Define target dates
        today = dt.now().date()
        year_ago_target = today - timedelta(days=365)

        # Find the closest actual trading days in the dataset
        year_ago_date_str = get_closest_date(time_series, year_ago_target)

        # Extract closing prices for those dates
        prices = {
            "today": float(time_series[latest_date_str]['4. close']),
            "yesterday": float(time_series[previous_date_str]['4. close']),
            "year_ago": float(time_series[year_ago_date_str]['4. close'])
        }
        return prices
    except (KeyError, IndexError):
        # Return None if the data is incomplete or in an unexpected format
        return None

# Function to update prices for all stocks in a user's watchlist
def update_stock_prices(user):
    today = dt.now().date()
    stocks_to_update = [stock for stock in user.watchlist if stock.date_retrieved.date() != today]

    for stock in stocks_to_update:
        # We use outputsize=full to ensure we have data for a year ago and YTD
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock.symbol}&outputsize=full&apikey={AV_KEY}"
        response = requests.get(url).json()
        
        time_series = response.get("Time Series (Daily)")
        if not time_series:
            # Skip if API fails or returns no data for this stock
            continue
        
        prices = get_relevant_prices(time_series)
        if prices:
            stock.date_retrieved = dt.utcnow()
            stock.price_today = prices["today"]
            stock.price_yesterday = prices["yesterday"]
            stock.price_year_ago = prices["year_ago"]

    # Commit all changes to the database at once after the loop
    if stocks_to_update:
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)