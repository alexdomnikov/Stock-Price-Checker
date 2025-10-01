# TODO: Check if user hit API rate limits when they access info, check for other possible errors, add better CSS styling, split main python file up accordingly

from project import create_app
from project import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)