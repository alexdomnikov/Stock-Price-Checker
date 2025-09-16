# Stock-Price-Checker

A simple Flask web app for checking stock prices and generating historical price charts.

## Overview
This originally started as an introductory project where I followed a tutorial. The tutorial tutorial taught me:
- The basics of Flask and web development
- How to work with third-party APIs (Alpha Vantage)
- Generating graphs with Matplotlib
- Using HTML & Jinja2 templates to display dynamic content

Following the tutorial project, I added the following features:
- User creation/authentication and secure password storage using Flask-bcrypt, Flask-login, SQAlchemy, and SQLite

I'm continuing to improve it by adding more styling (CSS) and considering new features like watchlists.

---

## Key Learnings

Building this project was a significant step in my journey as a developer. It taught me invaluable lessons in software development and practical application of new technologies. Some of my key takeaways include:

- **Understanding the MVC Pattern**: I learned how to structure a web application using the Model-View-Controller (MVC) pattern, separating the application's logic (Flask), data handling (SQLAlchemy), and user interface (Jinja2 templates).
- **Working with Third-Party APIs**: This project was my first experience integrating a third-party API. I learned how to make HTTP requests, parse JSON responses, and handle errors (e.g., for an invalid stock ticker).
- **Data Visualization with Matplotlib**: I gained hands-on experience in using Matplotlib to create dynamic charts from raw data. This included preparing the data for plotting and saving the generated chart to be rendered in the web page.
- **User Authentication and Security**: The most challenging and rewarding part was implementing user authentication. I learned the importance of secure password storage using bcrypt and how to manage user sessions and protect routes with Flask-Login.
- **Project Structure and Best Practices**: Beyond the code, I learned how to manage a project by using a requirements.txt file, handling sensitive information with a .env file, and writing a comprehensive README to guide other users.

---

## Features
- Search for any stock ticker symbol  
- Fetch historical data from the Alpha Vantage API  
- Generate and display historical stock price charts  
- Error handling for invalid input  
- User creation & secure password storage
- User authentication

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

2. Create a .env file in your root directory and add your Alpha Vantage API key + secret key:
AV_KEY={{your_API_key_here}}
SECRET_KEY={{a_secret_key_you_create_here}}

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
- Allow users to watchlist stocks

___

## License
This project is open-source and available under the [MIT License](https://opensource.org/license/mit).
