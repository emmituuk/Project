from flask import Flask
from flask import render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy.sql import text #for making queries
from livereload import Server

app = Flask(__name__)
app.debug = True
app.config.update(
    TEMPLATES_AUTO_RELOAD=True
)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# this function can move a list element to the end of the list, required in the drop-down/select menu
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

@app.route('/check_email_availability', methods=['POST'])
def check_email_availability():
    email = request.json.get('email')
    sql = text("SELECT email FROM person WHERE email = :email")
    result = db.session.execute(sql, {"email":email}).fetchone()

    is_email_available = not bool(result) # True if email not found, False if email found

    return jsonify({'available': is_email_available})

@app.route("/")
def index():
    sql = text("SELECT person_id FROM favorite_animals")
    result = db.session.execute(sql).fetchall()
    return render_template("index.html", count = len(result))

@app.route("/add")
def add():
    # next making the drop-down menu values for own_country_id and favorite_country_id
    sql = text("SELECT country_id, country FROM countries")
    original_countries = db.session.execute(sql).fetchall()
    # sorts countries by alphabetically
    sorted_countries = sorted(original_countries, key=lambda x:x[1])

    # next making the drop-down menu values for favorite_animals_id
    sql = text("SELECT animal_id, animal FROM animals")
    original_animals = db.session.execute(sql).fetchall()
    alph_animals = sorted(original_animals, key=lambda x:x[1])
    # fetches the row of the query result and returns a row as a list of tuples
    sql = text("SELECT animal_id, animal FROM animals WHERE animal = 'Other'")
    other_elem = db.session.execute(sql).fetchall()[0]
    # moves other_elem to the end of the list
    sorted_animals = move_to_end(alph_animals, other_elem)

    # finds the 'Other' value's id from the animals table
    sql = text("SELECT animal_id FROM animals WHERE animal = 'Other'")
    other_id_animals = db.session.execute(sql).fetchone()[0]

    return render_template("add.html", sorted_countries = sorted_countries, sorted_animals = sorted_animals, 
                           other_id_animals = other_id_animals)

@app.route("/send", methods=["POST"])
def send():
    # values to the person table
    email = request.form["email"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    own_country_id = request.form["own_country_id"]
    sql = text("INSERT INTO person (first_name, last_name, email, own_country_id, created_on)" \
               "VALUES (:first_name, :last_name, :email, :own_country_id, CURRENT_TIMESTAMP)" \
                "RETURNING person_id")
    result = db.session.execute(sql, {"first_name":first_name, "last_name":last_name, "email":email, "own_country_id":own_country_id})
    # Get the person_id of the newly inserted person
    last_id = result.fetchone()[0]

    # values to the favorite_animals table
    other_id_animals = db.session.execute(text("SELECT animal_id FROM animals WHERE animal = 'Other'")).fetchone()[0]
    favorite_animal_id = request.form["favorite_animal_id"]
    other_animal = request.form['other_animal'] if favorite_animal_id == str(other_id_animals) else None
    sql = text("INSERT INTO favorite_animals(person_id, favorite_animal_id, other_animal, created_on)" \
               "VALUES (:last_id, :favorite_animal_id, :other_animal , CURRENT_TIMESTAMP)")
    db.session.execute(sql, {"last_id":last_id, "favorite_animal_id":favorite_animal_id, "other_animal":other_animal})
    db.session.commit()

    # values to the favorite_countries table
    favorite_country_id = request.form['favorite_country_id']
    sql = text("INSERT INTO favorite_countries(person_id, favorite_country_id, created_on)" \
               "VALUES (:last_id, :favorite_country_id, CURRENT_TIMESTAMP)")
    db.session.execute(sql, {"last_id":last_id, "favorite_country_id":favorite_country_id})
    db.session.commit()

    return redirect("/")

@app.route("/result")
def result():
    return "here you can see some results"

if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve(port=5000)