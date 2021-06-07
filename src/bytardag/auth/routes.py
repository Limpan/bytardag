from flask import current_app, redirect, render_template, request
from flask.helpers import url_for
from flask_login import login_user, logout_user, login_required, current_user
from bytardag.auth import bp
from bytardag.auth.forms import LoginForm, RegisterForm
from bytardag.models import User
from bytardag import db


@bp.route("/register", methods=["GET", "POST"])
def register():
    """User self-registration."""
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login user."""
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                current_app.logger.info("Logged in user with email %s." % user.email)
                return redirect(request.args.get("next") or url_for("main.index"))
        current_app.logger.info("Failed to login user with email %s." % form.email.data)

    return render_template("auth/login.html", form=form)
