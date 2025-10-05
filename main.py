# TODO: Go through everything line by line and make sure you have robust error checking.
#
# Optional changes:
#       1. Change db from a one-to-many relationship (users have a watchlist, we update watchlists)
#          to a many-to-many relationship (we have a stock class, watchlists are a relationship). This helps limit API calls.
#       1. (contd.) If we do this, we need to instead update the watched stocks daily.
#       2. Allow users to change their password.
#       3. Allow users to delete their account.
#       4. Deploy for convenience.
#       5. Add more interactive chart rather than what you've got now. 

from project import create_app
from project import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)