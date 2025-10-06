# TODO: Update the readme (screenshot successful graph tomorrow). Freeze requirements.
#
# Optional TODO:
#       1. Change db from a one-to-many relationship (users have a watchlist, we update watchlists)
#          to a many-to-many relationship (we have a stock class, watchlists are a relationship). This helps limit API calls.
#       1. (contd.) If I do this, I need to instead update the watched stocks daily.
#       2. Allow users to change their password.
#       3. Allow users to delete their account.
#       4. Deploy for convenience (only do this if you've changed the db schema and pay to do more than 25 API calls/day).

from project import create_app
from project import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)