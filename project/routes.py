
# Standard library
from datetime import datetime as dt

# Third-party libraries
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import login_user, login_required, logout_user, current_user
from markupsafe import Markup

# Classes, forms, helper functions, API key
from .models import User, Watchlist
from .forms import AuthForm
from .helpers import get_graph, update_stock_prices, get_relevant_prices
from . import db, bcrypt, function_mapping # Imports these from __init__.py
from . import AV_KEY

# Create a blueprint
bp = Blueprint('routes', __name__)

# Flask's route decorator maps URLs to a specific function
@bp.route('/', methods=['GET', 'POST'])
def index():
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
                return redirect(url_for('routes.dashboard'))
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
                return redirect(url_for('routes.dashboard')) 
        
    return render_template("index.html", form=form, error=error)

@bp.route('/info', methods=['GET', 'POST'])
@login_required
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
    if "Information" in company_overview or "Note" in company_overview and "API key" in company_overview:
        flash("You've hit your Alpha Vantage API call limit. Please try again tomorrow.", "danger")
        return redirect(url_for('routes.dashboard'))
    if 'Name' not in company_overview:
        flash("Invalid ticker", "danger")
        return redirect(url_for('routes.dashboard'))
    
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
    

# Route for the dashboard with watchlist displayed, which is only available if logged in
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    # ADD STOCK LOGIC (POST request)
    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'delete':
            stock_id = request.form.get('stock_id')

            if(stock_id):
                stock_to_delete = Watchlist.query.filter_by(
                    id = stock_id,
                    user_id = current_user.id
                ).first()

            if(stock_to_delete):
                db.session.delete(stock_to_delete)
                db.session.commit()
                return redirect(url_for('routes.dashboard'))
        else:
            symbol = request.form['symbol'].upper()

            # 1. Check if watchlist is full (max 5 since this is just a simple project)
            if current_user.watchlist.count() >= 5:
                flash("Sorry, we only allow 5 stocks in your watchlist.", "danger")
            # 2. Check if stock is already in the watchlist
            elif any(stock.symbol == symbol for stock in current_user.watchlist):
                flash(f"{symbol} is already in your watchlist.", "danger")
            else:
                # 3. Validate ticker by checking if the API returns a company name
                overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}"
                overview_data = requests.get(overview_url).json()
                
                # User might encounter an error where they've hit an API call limit
                if "Information" in overview_data or "Note" in overview_data and "API key" in overview_data:
                    flash("You've hit your Alpha Vantage API call limit. Please try again tomorrow.", "danger")
                elif 'Name' not in overview_data or overview_data['Name'] is None:
                    flash(f"'{symbol}' is not a valid stock symbol.", "danger")
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
                        return redirect(url_for('routes.dashboard')) # Redirect to clear form
                    else:
                        # Adding check for API call limit error
                        if "Information" in response or "Note" in response and "API key" in response:
                            flash("You've hit your Alpha Vantage API call limit. Please try again tomorrow.", "danger")
                        else:
                            flash(f"Could not retrieve price data for {symbol}.", "danger")

    # DISPLAY WATCHLIST LOGIC (GET request)
    # Always update prices before displaying the dashboard
    update_stock_prices(current_user)
    
    # Retrieve the (now updated) watchlist from the database
    user_watchlist = current_user.watchlist.all()

    return render_template("dashboard.html", watchlist=user_watchlist)

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))