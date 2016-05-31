from flask import render_template, url_for, redirect
from flask_login import login_required, request
from . import main
from .. import db


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')
