from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy.sql import text #for making queries
from livereload import Server

app = Flask(__name__)
app.debug = True
app.config.update(
    TEMPLATES_AUTO_RELOAD=True
)
# connection to the database
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# this function can move a list element to the end of the list
# required in drop-down/select menus
def move_to_end(lst, elem):
    new_lst = []
    temp = None
    for i in lst:
        if i != elem:
            new_lst.append(i)
        else:
            temp = i
    new_lst.append(temp)
    return new_lst

@app.route("/")
def index():
    # gets all person_ids and returns all the rows as a list of tuples
    result = db.session.execute(text("SELECT person_id FROM favorite_animals")).fetchall()
    # returns the number of items in result
    return render_template("index.html", count = len(result))

@app.route("/add")
def add():
    # next making the drop-down menu values for own_country_id and favorite_country_id
    original_countries = db.session.execute(text("SELECT country_id, country FROM countries")).fetchall()
    # sorts countries by alphabetically
    alph_countries = sorted(original_countries, key=lambda x:x[1])
    # fetches the row of the query result and returns a row as a list of tuples
    other_elem1 = db.session.execute(text("SELECT country_id, country FROM countries WHERE country = 'Other'")).fetchall()[0]
    # moves other_elem to the end of the list
    sorted_countries = move_to_end(alph_countries, other_elem1)

    # next making the drop-down menu values for favorite_animals_id
    original_animals = db.session.execute(text("SELECT animal_id, animal FROM animals")).fetchall()
    alph_animals = sorted(original_animals, key=lambda x:x[1])
    other_elem2 = db.session.execute(text("SELECT animal_id, animal FROM animals WHERE animal = 'Other'")).fetchall()[0]
    sorted_animals = move_to_end(alph_animals, other_elem2)

    return render_template("add.html", sorted_countries = sorted_countries, sorted_animals = sorted_animals)


# POST-method can change e.g. insert or update the database, but GET can not.
@app.route("/send", methods=["POST"])
def send():
    
    # values to the person table
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    own_country_id = request.form["own_country_id"]
    sql = text("INSERT INTO person (first_name, last_name, email, own_country_id, created_on)" \
               "VALUES (:first_name, :last_name, :email, :own_country_id, CURRENT_TIMESTAMP)" \
                "RETURNING person_id")
    # executes
    result = db.session.execute(sql, {"first_name":first_name, "last_name":last_name, "email":email, "own_country_id":own_country_id})
    # Get the person_id of the newly inserted person
    last_id = result.fetchone()[0]

    # values to the favorite_animals table
    favorite_animal_id = request.form["favorite_animal_id"]
    sql = text("INSERT INTO favorite_animals(person_id, favorite_animal_id, created_on)" \
               "VALUES (:last_id, :favorite_animal_id, CURRENT_TIMESTAMP)")
    db.session.execute(sql, {"last_id":last_id, "favorite_animal_id":favorite_animal_id})
    db.session.commit()

    # values to the favorite_countries table
    favorite_country_id = request.form["favorite_country_id"]
    sql = text("INSERT INTO favorite_countries(person_id, favorite_country_id, created_on)" \
               "VALUES (:last_id, :favorite_country_id, CURRENT_TIMESTAMP)")
    db.session.execute(sql, {"last_id":last_id, "favorite_country_id":favorite_country_id})
    db.session.commit()

    # after back to the front page
    return redirect("/")

@app.route("/result")
def result():
    return "here you can see some results"

if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve(port=5000)
    # server.watch("templates/*.*")