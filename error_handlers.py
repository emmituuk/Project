from flask import render_template


def bad_request(error):
    return render_template("error.html", error_message="400 Bad Request"), 400


def unauthorized(error):
    return render_template("error.html", error_message="401 Unauthorized"), 401


def forbidden(error):
    return render_template("error.html", error_message="403 Forbidden"), 403


def page_not_found(error):
    return render_template("error.html", error_message="404 Not Found"), 404


def conflict(error):
    return render_template("error.html", error_message="409 Conflict"), 409


def precondition_failed(error):
    return render_template("error.html", error_message="412 Precondition Failed"), 412


def too_many_requests(error):
    return render_template("error.html", error_message="429 Too Many Requests"), 429


def internal_server_error(error):
    return render_template("error.html", error_message="500 Internal Server Error"), 500


def bad_gateway(error):
    return render_template("error.html", error_message="502 Bad Gateway"), 502


def service_unavailable(error):
    return render_template("error.html", error_message="503 Service Unavailable"), 503


def gateway_timeout(error):
    return render_template("error.html", error_message="504 Gateway Timeout"), 504
