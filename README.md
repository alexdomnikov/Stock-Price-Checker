# Stock-Price-Checker

A simple Flask web app for creating watchlists, checking stock prices, and generating historical price charts.

## Overview
This originally started as an introductory project where I followed a tutorial. The tutorial tutorial taught me:
- The basics of Flask and web development
- How to work with third-party APIs (Alpha Vantage)
- Generating graphs with Matplotlib
- Using HTML & Jinja2 templates to display dynamic content

Following the tutorial project, I added the following features:
- User creation/authentication and secure password storage using Flask-bcrypt, Flask-login, SQAlchemy, and SQLite
- CRUD functionality where users can add/delete up to 5 stocks in their watchlist (limited because of the strict API call limit)
- Interactive charts using Plotly (and Plotly IO to render from a Plotly string to an HTML-rendered graph)
- Attractive and intuitive UI/UX using Bootstrap

---

## Key Learnings

Building this project was a significant step in my journey as a developer. It taught me invaluable lessons in software development and practical application of new technologies. Some of my key takeaways include:

- **Understanding the MVC Pattern**: I learned how to structure a web application using the Model-View-Controller (MVC) pattern, separating the application's logic (Flask), data handling (SQLAlchemy), and user interface (Jinja2 templates).
- **Working with Databases**: This was my first project working with databases. I learned how to use SQLite, and how to use an ORM like SQLAlchemy to "glue" together OOP languages (Python) with relational databases.
- **The Inner Workings of the Web**: I learned how 1. computers send requests to an HTTP server (e.g., nginx), 2. how these servers act as reverse proxies and how they forward the requests to the appropriate backend server, 3. how Python Web Server Gateway Interfaces (WSGIs) like Gunicorn implement the WSGI specification and hand a WSGI compliant requests to a Python web frameworks like Flask, 4. how Flask apps use routes to map URL patterns to specific Python functions, and 5. how the Python responses are sent back through the WSGI -> the HTTP server -> the browser and rendered.
- **Working with Third-Party APIs**: This project was my first experience integrating a third-party API. I learned how to make HTTP requests, parse JSON responses, and handle errors (e.g., for an invalid stock ticker or an API call limit).
- **Data Visualization with Matplotlib and Plotly**: I gained hands-on experience in using Matplotlib to create charts from raw data. This included preparing the data for plotting and saving the generated chart to be rendered in the web page. I then branched out and used Plotly to create more interactive charts.
- **User Authentication and Security**: The most challenging and rewarding part was implementing user authentication. I learned the importance of secure password storage using bcrypt and how to manage user sessions and protect routes with Flask-Login.
- **Project Structure and Best Practices**: Beyond the code, I learned how to manage a project by using a requirements.txt file, handling sensitive information with a .env file, and writing a comprehensive README to guide other users.

---

## Features
- Log in to create watchlists
- Search for any stock ticker symbol to see stock price charts
- Fetch historical data from the Alpha Vantage API  
- Generate and display historical stock price charts  
- Error handling for invalid input  
- User creation & secure password storage
- User authentication

---

## Tech Stack
- Backend: Python, Flask, Flask-Login
- Database: SQLite, SQLAlchemy
- Frontend: HTML, CSS, Bootstrap, Jinja2
- Data & Visualization: Plotly, Alpha Vantage API
- Security: Flask-Bcrypt (for password hashing)

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

6. I've uploaded the database instance I created for simplicity. You can create a user when running the app or, optionally, you can use the demo user to see functionality (username: demo, password: password)

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
I've stopped working on this project because I feel I've learned what I set out to learn. If I were to make any further changes to this project, they'd be changes that would allow for deployment and real users:
- Change the database schema to be many-to-many with stocks stored and watchlists having a stock relationship, so that users don't "own" the updates on login.
- I'd instead pull daily updates for the stocks that users are actually watching. These first two updates would limit API calls significantly. 
- Allow user password changes, account deletion. 
___

## License
This project is open-source and available under the [MIT License](https://opensource.org/license/mit).
