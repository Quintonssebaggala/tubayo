import os

from app.auth import auth
from werkzeug.urls import url_parse


from app import app, blueprint, facebook_blueprint
from sqlalchemy.orm.exc import NoResultFound
from app.data.models import db, User, OAuth
from app.form.forms import LoginForm, RegistrationForm

from flask import render_template, abort, request, redirect, flash, url_for, send_from_directory, json
from flask_login import logout_user, current_user, login_user, login_required
from app.email import send_email
from flask_dance.consumer import oauth_authorized, oauth_error



@auth.route('/send/', methods=['GET', 'POST'])
def send():
    send_email('quinton.ssebaggala@gmail.com', 'Confirm Your Account', 'mail/new_user')
    return 'sentt'



@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.password_hash is None:
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        else:
            if user is None or not user.check_password(form.password.data):
                flash('Invalid email or password')
                return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from google."
        flash(msg, category="error")
        return False

    google_info = resp.json()
    google_user_id = str(google_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=google_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with GitHub.")

    else:
        # Create a new local user account for this user
        user = User(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on GitHub!
            email=google_info["email"],
            username=google_info["name"],
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with GitHub.")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(facebook_blueprint, token):
    if not token:
        flash("Failed to log in with facebook.", category="error")
        return False

    resp = facebook_blueprint.session.get("me?fields=id,name,email,gender,picture,locale")
    if not resp.ok:
        msg = "Failed to fetch user info from facebook."
        flash(msg, category="error")
        return False

    facebook_info = resp.json()
    facebook_user_id = str(facebook_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=facebook_blueprint.name,
        provider_user_id=facebook_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=facebook_blueprint.name,
            provider_user_id=facebook_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with GitHub.")

    else:
        # Create a new local user account for this user
        user = User(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on GitHub!
            email=facebook_info["email"],
            username=facebook_info["name"],
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with GitHub.")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False

# notify on OAuth provider error
@oauth_error.connect_via(facebook_blueprint)
def facebook_error(facebook_blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=facebook_blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")

@oauth_authorized.connect
def logged_in(blueprint, token):
    return 'yooo'


@auth.route('/logout/')
# @login_required
def logout():
    logout_user()
    return redirect(url_for('main.shop'))

