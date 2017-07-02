from flask import render_template


def index():
    return render_template('index.html')
