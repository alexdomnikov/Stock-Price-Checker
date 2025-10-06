
# Standard library
from io import StringIO
from datetime import timedelta, date

# Importing dt from routes
from .routes import dt
from . import AV_KEY, db

# Third-party libraries
import requests
import plotly.express as px
import plotly.io as pio
import pandas as pd

def get_graph(dates, prices, company_name):
    data = {'Date' : dates,
            'Price' : prices}
    df = pd.DataFrame(data)

    # x and y match the keys in data
    # Using pio so we can get an actual rendered chart in html rather than a plotly string
    fig = px.line(df, x = 'Date', y = 'Price', title = f"Stock Price of {company_name}")
    return pio.to_html(fig, full_html=False)

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
        # Outputsize=full gives us all daily data as far back as possible. In a future iteration, I'd prefer to restructure
        # the db schema to be many-to-many and create a stock class with a watchlist relationship to reduce API calls (and just
        # cache the JSON response we get from this full output). We'd then need to switch to daily updates rather than updating on users
        # logging in (e.g., user watchlists won't trigger the updates anymore), and we could use the full daily data to make any charts we'd like.
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