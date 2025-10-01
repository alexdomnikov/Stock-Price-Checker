
# Third-party libraries
from flask_login import UserMixin

# Instances
from . import db # Import db instance from __init__.py package

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
