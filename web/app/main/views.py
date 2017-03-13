from flask import current_app, flash, redirect, render_template, url_for
from flask_login import login_required, current_user, login_user
from . import main
from .forms import SignupForm, ProfileForm
from .. import db
from ..models import get_current_event, User, Attendance
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    current_event = get_current_event()

    form = SignupForm()
    if form.validate_on_submit():
        if current_event.signup_open() and not current_user.is_anonymous:
            current_app.logger.info('Signing up user {}.'.format(current_user.email))
            attendance = Attendance()
            attendance.event = current_event
            attendance.user = current_user

            chars = 'ABCEFGHJKLMNOPRSTVXZ'
            attendance.seller_id = '{}-{:02}'.format(chars[current_event.next_seller_id % 20], current_event.next_seller_id // 20 % 100 * 2 + 1)
            current_event.next_seller_id = current_event.next_seller_id + 1

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

    return render_template('main/index.html', form=form,
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


@main.route('/personal')
def personal():
    return render_template('main/personal.html')


@main.route('/dashboard')
@login_required
def dashboard():
    current_event = get_current_event()
    users = User.query.all()
    unconfirmed_email_users = User.query.filter_by(confirmed = False).all()
    return render_template('main/dashboard.html', users=users,
                                                  unconfirmed_email_users=unconfirmed_email_users,
                                                  current_event=current_event)


@main.route('/info')
def info():
    return render_template('main/info.html')
