from flask import Flask
from models import db
from flask import render_template, request, jsonify
from os import getenv
from sqlalchemy.sql import text
from livereload import Server

from blueprints.send import send_bp
from blueprints.add import add_bp
from blueprints.result import result_bp
from blueprints.updated_graphs import updated_graphs_bp

from error_handlers import render_error

app = Flask(__name__)
app.debug = True
app.config.update(TEMPLATES_AUTO_RELOAD=True)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db.init_app(app)

app.register_error_handler(400, render_error)
app.register_error_handler(401, render_error)
app.register_error_handler(403, render_error)
app.register_error_handler(404, render_error)
app.register_error_handler(409, render_error)
app.register_error_handler(412, render_error)
app.register_error_handler(429, render_error)
app.register_error_handler(500, render_error)
app.register_error_handler(502, render_error)
app.register_error_handler(503, render_error)
app.register_error_handler(504, render_error)

# register the Blueprints
app.register_blueprint(send_bp)
app.register_blueprint(add_bp)
app.register_blueprint(result_bp)
app.register_blueprint(updated_graphs_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check_email_availability", methods=["GET"])
def check_email_availability():
    email = request.args.get("email")
    sql = text("SELECT email FROM person WHERE email = :email")
    result = db.session.execute(sql, {"email": email}).fetchone()

    # true if email not found, false if email found
    is_email_available = not bool(result)

    return jsonify({"available": is_email_available})


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve(port=5000)
