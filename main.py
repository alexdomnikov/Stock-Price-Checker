# TODO: Create interactive chart with plotly. Remove anything related to matplotlib. 
#       Update the readme (screenshot successful graph tomorrow). Freeze requirements.
#
# Optional changes:
#       2. Change db from a one-to-many relationship (users have a watchlist, we update watchlists)
#          to a many-to-many relationship (we have a stock class, watchlists are a relationship). This helps limit API calls.
#       2. (contd.) If I do this, I need to instead update the watched stocks daily.
#       3. Allow users to change their password.
#       4. Allow users to delete their account.
#       5. Deploy for convenience.

from project import create_app
from project import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)