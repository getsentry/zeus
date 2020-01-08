from flask import current_app


def absolute_url(path: str) -> str:
    return (
        "{proto}://{domain}/{path}".format(
            proto="https" if current_app.config["SSL"] else "http",
            domain=current_app.config["DOMAIN"],
            path=path.lstrip("/"),
        ),
    )
