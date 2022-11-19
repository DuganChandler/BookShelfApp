import flask
import os
import json
from flask_sqlalchemy import SQLAlchemy
from requests import request
from books import get_books

titles = []
images = []

queries = [
    "SYLO",
    "The Hobbit",
    "Dune", 
    "Percy Jackson", 
    "Harry Potter"
]

for element in queries:
    response = get_books(element)
    titles.append(response["items"][0]['volumeInfo']['title'])
    images.append(response["items"][0]['volumeInfo']["imageLinks"]['thumbnail'])

# creates flask app
app = flask.Flask(__name__)

# gets base directry filepath for the database
basedir = os.path.abspath(os.path.dirname(__file__))

# configures the path of the db so the app can see it
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# creates db class of favorite books th columns
class FavoriteBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    subtitle = db.Column(db.String(80))
    author = db.Column(db.String(80))
    image = db.Column(db.String(120))

# scans every class created and creates db if db does not exist
with app.app_context():
    db.create_all()

@app.route("/add", methods=["GET", "POST"])
def add():
    if flask.request.method == "POST":
        # gets the dict object from the index.html file that was sent via js script
        book_to_add = json.loads(flask.request.data.decode())
        # creates the new db object instance from the data of book_to_add
        new_book = FavoriteBooks(
            title = book_to_add["title"],
            subtitle = book_to_add["subtitle"],
            author = book_to_add["author"],
            image = book_to_add["image"]
        )
        # adds the object to the db and commits it to the db
        db.session.add(new_book)
        db.session.commit()
    
    return flask.redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    if flask.request.method == "POST":
        # gets the dict object from the index.html file that was sent via js script
        book_to_delete = json.loads(flask.request.data.decode())
        # queries the db for the object with title of the book_to_delete dict
        to_delete = FavoriteBooks.query.filter_by(title = book_to_delete).first()
        # deletes the object and officially commits that change
        db.session.delete(to_delete)
        db.session.commit()
        return flask.redirect("/")


@app.route('/', methods=["POST", "GET"])
def index():
    query = flask.request.args.get("query")
    # gets the initial favorite books of mine and stores them in the db
    for element in queries:
        response = get_books(element)
        exists = db.session.query(db.session.query(FavoriteBooks).filter_by(title=response["items"][0]['volumeInfo']['title']).exists()).scalar()
        if exists == False:
            my_fav_books = FavoriteBooks(
                title=response["items"][0]['volumeInfo']['title'],
                subtitle=response["items"][0]['volumeInfo'].get('subtitle'),
                author=", ".join(response["items"][0]['volumeInfo'].get('authors', [])),
                image=response["items"][0]['volumeInfo']["imageLinks"]['thumbnail'] 
            )
        
            db.session.add(my_fav_books)
            db.session.commit()

    fav_books = FavoriteBooks.query.all()
    num_books = len(fav_books)
    
    # gets the json response of books from books.py
    # stores the books in a list of dicts
    search_results = []
    if query is not None:
        response = get_books(query)
        for item in response["items"][:5]:
            res = {}

            res["title"] = item['volumeInfo']['title']
            res["subtitle"] = item['volumeInfo'].get('subtitle')
            res["author"] = ", ".join(item['volumeInfo'].get('authors', []))
            res["image"] = item['volumeInfo']["imageLinks"]['thumbnail'] if "imageLinks" in item["volumeInfo"] else None

            search_results.append(res)

    return flask.render_template(
        "index.html",
        titles = titles,
        images = images,
        search_results = search_results,
        num_books = num_books,
        fav_books = fav_books
        
    )

app.run(
    debug=True
)