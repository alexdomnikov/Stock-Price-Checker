import os
import requests
from io import StringIO

from flask import Flask, render_template, request, redirect, url_for
from markupsafe import Markup
from dotenv import load_dotenv
from datetime import datetime as dt

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
matplotlib.use('Agg')

# Loads .env file, grabs the API key from the .env file
load_dotenv()
AV_KEY = os.getenv("AV_KEY")

# Dictionary to map URL values to data keys from API response
function_mapping = {
    "TIME_SERIES_DAILY" : "Time Series (Daily)",
    "TIME_SERIES_WEEKLY" : "Weekly Time Series",
    "TIME_SERIES_MONTHLY" : "Monthly Time Series"
}

app = Flask(__name__)

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