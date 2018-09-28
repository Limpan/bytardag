from flask import current_app, flash, redirect, render_template, url_for, jsonify
from flask_login import fresh_login_required, login_required, current_user, login_user
from . import main
from .forms import EventForm, SignupForm, ProfileForm, BankAccountForm, VolunteerForm
from .. import db
from ..models import get_current_event, User, Attendance, BankAccount, Event
from ..decorators import admin_required, check_confirmed
from ..email import send_email
from datetime import datetime

@main.route('/', methods=['GET', 'POST'])
def index():
    current_event = get_current_event()

    form = SignupForm()
    if form.validate_on_submit():
        current_event = Event.query.filter(Event.start > datetime.utcnow()).order_by(Event.start).with_for_update().first()

        if current_event.signup_open() and not current_user.is_anonymous:
            current_app.logger.info('Signing up user {}.'.format(current_user.email))
            attendance = Attendance()
            attendance.event = current_event
            attendance.user = current_user

            attendance.seller_id = Event.generate_seller_id(current_event.next_seller_id)
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
@check_confirmed
def profile():
    user = current_user
    form = ProfileForm(email=user.email,
                       first_name=user.first_name,
                       last_name=user.last_name,
                       phone=user.phone)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        db.session.commit()
        flash('Din profil har uppdaterats.')
        return redirect(url_for('main.index'))
    return render_template('main/profile.html', form=form, user=user)


@main.route('/profile/bank', methods=['GET', 'POST'])
@login_required
@check_confirmed
def profile_bank():
    form = BankAccountForm()
    if form.validate_on_submit():
        user = current_user
        account = BankAccount(bank = form.bank.data,
                              clearing = ''.join(i for i in form.clearing.data if i.isdigit),
                              number = ''.join(i for i in form.number.data if i.isdigit))
        user.account = account
        db.session.add(account)
        db.session.commit()
        flash('Dina kontouppgifter har uppdaterats.')
        return redirect(url_for('main.profile'))
    return render_template('main/profile_bank.html', form=form)


@main.route('/personal')
def personal():
    return render_template('main/personal.html')


@main.route('/dashboard')
@admin_required
def dashboard():
    current_event = get_current_event()
    users = User.query.all()
    events = Event.query.all()
    unconfirmed_email_users = User.query.filter_by(confirmed = False).all()
    from random import randint
    return render_template('main/dashboard.html', users=users, events=events,
                                                  unconfirmed_email_users=unconfirmed_email_users,
                                                  current_event=current_event)

@main.route('/stats/event')
@admin_required
def event_stats():
    event = get_current_event()
    data = {
        'max_attendees': event.limit,
        'attendees': len(event.attendees),
        'free': event.limit - len(event.attendees)
    }
    return jsonify(data)


@main.route('/stats/users')
@admin_required
def users_stats():
    total_count = User.query.filter_by().count()
    confirmed_count = User.query.filter_by(confirmed=True).count()
    data = {
        'total_count': total_count,
        'confirmed_count': confirmed_count,
        'unconfirmed_count': total_count - confirmed_count
    }
    return jsonify(data)


@main.route('/user/<int:id>')
@admin_required
def user_profile(id):
    user = User.query.get(id)
    return render_template('main/user_profile.html', user=user)


@main.route('/info')
def info():
    return render_template('main/info.html')


@main.route('/volunteer')
def volunteer():
    form = VolunteerForm()
    if form.validate_on_submit():
        pass

    current_event = get_current_event()
    return render_template('main/volunteer.html', current_event=current_event, form=form)


@main.route('/user')
@admin_required
def list_users():
    users = db.session.query(User).order_by(User.last_name, User.first_name).all()
    return render_template('main/list_users.html', users=users)


@main.route('/event', methods=['GET', 'POST'])
@admin_required
def list_events():
    form = EventForm()
    if form.validate_on_submit():
        pass

    events = db.session.query(Event).order_by(Event.start.desc()).all()
    return render_template('main/list_events.html', form=form, events=events)


@main.route('/event/<int:id>', methods=['GET', 'POST'])
@admin_required
def event(id):
    event = Event.query.get(id)
    return render_template('main/event.html', event=event)


@main.route('/event/<int:id>/with_bank')
#@fresh_login_required
@admin_required
def event_with_bank_details(id):
    event = Event.query.get(id)
    return render_template('main/event_with_bank_details.html', event=event)


@main.route('/gdpr')
def gdpr():
    return render_template('main/gdpr.html')
