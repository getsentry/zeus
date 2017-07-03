from flask import render_template


def index(path=None):
    return render_template('index.html')
