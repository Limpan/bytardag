from flask import current_app, flash, redirect, render_template, url_for
from flask_login import login_required, request, current_user, login_user
from . import main
from .forms import RegisterForm, SignupForm, ProfileForm
from .. import db
from ..models import get_current_event, User, Attendance
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    current_event = get_current_event()

    register_form = RegisterForm(prefix='register')
    if register_form.validate_on_submit() and register_form.submit.data:
        user = User(email=register_form.email.data, password=register_form.password.data)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info('New user added, {email} ({id}).'.format(id=user.id, email=user.email))
        token = user.generate_confirmation_token()
        send_email.delay(user.email, 'Bekräfta din epostadress', 'main/email/confirm', token=token)
        login_user(user, True)
        flash('Ett bekräftelsemail har skickats till din epostadress.')

    signup_form = SignupForm(prefix='signup')
    if signup_form.validate_on_submit() and signup_form.submit.data:
        if current_event.signup_open():
            current_app.logger.info('Signing up user {}.'.format(current_user.email))
            attendance = Attendance()
            attendance.event = current_event
            attendance.user = current_user

            chars = 'ABCEFGHJKLMNOPRSTVXZ'
            attendance.seller_id = '{}-{:02}'.format(chars[current_event.next_seller_id % 20], current_event.next_seller_id // 20 % 100 * 2 + 1)
            current_event.next_seller_id += 1

            db.session.add(attendance)
            db.session.commit()
            send_email.delay(current_user.email, 'Välkommen som säljare', 'main/email/seller', seller_id=attendance.seller_id)
            flash('Grattis! Du är nu anmäld. Ett mail har skickats till din epostadress med instruktioner.')
        else:
            flash('Anmälan kunde inte göras.')

    if not current_user.is_anonymous:
        attending = current_event in [attendance.event for attendance in current_user.events]
    else:
        attending = None

    return render_template('main/index.html', register_form=register_form,
                                              signup_form=signup_form,
                                              current_event=current_event,
                                              attending=attending)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    form = ProfileForm(email=user.email, first_name=user.first_name, last_name=user.last_name, phone=user.phone)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        db.session.commit()
        flash('Din profil har uppdaterats.')
        return redirect(url_for('main.index'))
    return render_template('main/profile.html', form=form)


@main.route('/dashboard')
@login_required
def dashboard():
    current_event = get_current_event()
    return render_template('main/dashboard.html', current_event=current_event)


@main.route('/event/add', methods=['GET', 'POST'])
@login_required
def add_event():
    return
