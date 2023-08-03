from flask import Flask
from models import db
from flask import render_template, request, jsonify
from os import getenv
from sqlalchemy.sql import text
from livereload import Server

from send import send_bp
from add import add_bp
from result import result_bp
from updated_bar_charts import updated_bar_charts_bp

from error_handlers import (
    bad_request,
    unauthorized,
    forbidden,
    page_not_found,
    conflict,
    precondition_failed,
    too_many_requests,
    internal_server_error,
    bad_gateway,
    service_unavailable,
    gateway_timeout,
)

app = Flask(__name__)
app.debug = True
app.config.update(TEMPLATES_AUTO_RELOAD=True)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db.init_app(app)

app.register_error_handler(400, bad_request)
app.register_error_handler(401, unauthorized)
app.register_error_handler(403, forbidden)
app.register_error_handler(404, page_not_found)
app.register_error_handler(409, conflict)
app.register_error_handler(412, precondition_failed)
app.register_error_handler(429, too_many_requests)
app.register_error_handler(500, internal_server_error)
app.register_error_handler(502, bad_gateway)
app.register_error_handler(503, service_unavailable)
app.register_error_handler(504, gateway_timeout)

# register the Blueprints
app.register_blueprint(send_bp)
app.register_blueprint(add_bp)
app.register_blueprint(result_bp)
app.register_blueprint(updated_bar_charts_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check_email_availability", methods=["POST"])
def check_email_availability():
    email = request.json.get("email")
    sql = text("SELECT email FROM person WHERE email = :email")
    result = db.session.execute(sql, {"email": email}).fetchone()

    # true if email not found, false if email found
    is_email_available = not bool(result)

    return jsonify({"available": is_email_available})


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve(port=5000)
