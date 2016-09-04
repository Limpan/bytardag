from flask import render_template, redirect, request, url_for, flash, current_app, abort, Markup
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, ChangePasswordForm, PasswordResetRequestForm, ChangeEmailForm, PasswordResetForm
from . import auth
from .. import db
from ..models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
#from ..email import send_email


@auth.before_app_request
def before_request():
    """Used to register the users activity, when a request is sent."""
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Route for signing in.

    Checks if user  doeshave a password, and gives a notice if
    he or she does not have a password-protected account (the alternative is email sign in).
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        flash(Markup('Fel användarnamn eller lösenord. <a href="{}">Återställ lösenord.</a>'.format(url_for('auth.password_reset_request'))))
    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('Du har bekräftat ditt kontos epostadress.')
    else:
        flash('Bekräftelselänken är felaktig eller för gammal.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    from ..email import send_email
    send_email.delay(current_user.email, 'Bekräfta din epostadress', 'main/email/confirm', token=token)
    flash('Ett nytt bekräftelsemail har skickats.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Route for changing a user password.

    Can only be accessed when user is already authenticated.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.commit()
            flash('Ditt lösenord är uppdaterat.')
            return redirect(url_for('main.index'))
        else:
            flash('Fel lösenord.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """Route for requesting a password reset."""
    # Checks if user is not already authenticated.
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        current_app.logger.info('User with email adress {email} is trying to recover password.'.format(email=form.email.data))
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            # Sends an email to the user, which contains a reset-token.
            from ..email import send_email
            send_email.delay(user.email,
                             'Reset password',
                             'auth/email/password_reset',
                             name=user.first_name,
                             token=token)
        flash('Ett mail med instruktioner för att återställa ditt lösenord har skickats till dig.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Route for reset a password with a given token."""
    # Checks if user is not already authenticated.
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Checks if user does not exist.
        if user is None:
            return redirect(url_for('main.index'))
        # Checks if token is valid.
        if user.reset_password(token, form.password.data):
            flash('Ditt lösenord är uppdaterat.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Route to request an email change."""
    form = ChangeEmailForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            # Sends an email to the new email adress for verification.
            from ..email import send_email
            send_email(new_email, 'Verfiera epostadress', 'auth/email/change_email', user=current_user, token=token)
            flash('Ett epostmeddelande med instruktioner för att verfiera din nya epostadress har skickats till den.')
            return redirect(url_for('main.index'))
        else:
            flash('Fel epost eller lösenord.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    """Used to verify the new email adress, using a token."""
    # Checks if token is valid.
    if current_user.change_email(token):
        flash('Din epostadress har uppdaterats.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
