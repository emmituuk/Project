from flask import render_template


error_messages = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    412: "Precondition Failed",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


def render_error(error):
    status_code = getattr(
        error, "code", 500
    )  # default to 500 if status code is not available
    error_message = error_messages.get(status_code, "Unknown Error")
    return (
        render_template("error.html", error_message=f"{status_code} {error_message}"),
        status_code,
    )
