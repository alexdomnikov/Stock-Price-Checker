# Stock-Price-Checker

A simple Flask web app for checking stock prices and generating historical price charts.

## Overview
This project was my first foray into building a "real" software project outside the classroom.  
It started as a tutorial project and taught me:
- The basics of Flask and web development
- How to work with third-party APIs (Alpha Vantage)
- Generating graphs with Matplotlib
- Using HTML & Jinja2 templates to display dynamic content

I'm continuing to improve it by adding more styling (CSS) and considering new features like user authentication and watchlists.

---

## Features
- Search for any stock ticker symbol  
- Fetch historical data from the Alpha Vantage API  
- Generate and display historical stock price charts  
- Error handling for invalid input  

---

## Tech Stack
- Python (Flask)
- Matplotlib for chart generation
- Alpha Vantage API for stock data
- HTML + Jinja2 templates for rendering results

---

## Installation & Usage

1. Clone this repo
   ```bash
   git clone https://github.com/alexdomnikov/Stock-Price-Checker.git
   cd Stock-Price-Checker

2. Create a .env file in your root directory and add your Alpha Vantage API key:
AV_KEY={{your_API_key_here}}

3. Install dependencies
pip install -r requirements.txt

4. Run the app
python main.py

5. Open your browser and go to http://127.0.0.1:5000

---

## Screenshots

Index
<img width="1431" height="780" alt="image" src="https://github.com/user-attachments/assets/898e79dd-a3cb-419a-9f13-9b9582e5379a" />

Invalid ticker
<img width="1432" height="783" alt="image" src="https://github.com/user-attachments/assets/151a564f-9f50-4280-9cc1-562f9a41964f" />

Valid ticker
<img width="1436" height="783" alt="image" src="https://github.com/user-attachments/assets/299c695e-f718-4f5f-bee2-dfdfb65b07e2" />

___

## Future Plans
- Add CSS styling for a better UI/UX
- Implement user login & signup
- Allow users to watchlist stocks

___

## License
This project is open-source and available under the [MIT License](https://opensource.org/license/mit).
