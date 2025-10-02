# TODO: Check if user hit API rate limits when they access info. 
#       Create user-friendly API rate limit message.
#       Cache API responses for charts so we don't burn through rate limits. 
#       Allow users to click on a stock name from dashboard and get the chart.
#       Add more interactive chart rather than what you've got now. 
#       Allow users to change their password.
#       Allow users to delete their account. 

from project import create_app
from project import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)