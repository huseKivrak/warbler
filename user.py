
from app import app
from flask import render_template, request, flash, redirect, g
from forms import EditUser
from models import db, User, Message, DEFAULT_IMAGE_URL, DEFAULT_HEADER_IMAGE_URL
from helpers import do_logout


@app.get('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.get('/users/<int:user_id>')
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    # format?
    messages = Message.query.filter_by(
        user_id=user.id).order_by(Message.timestamp.desc()).all()

    return render_template('users/show.html', user=user, messages=messages)


@app.get('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.get('/users/<int:user_id>/followers')
def show_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.post('/users/follow/<int:follow_id>')
def start_following(follow_id):
    """Add a follow for the currently-logged-in user.

    Redirect to following page for the current for the current user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.post('/users/stop-following/<int:follow_id>')
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user.

    Redirect to following page for the current for the current user.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """
    Update profile for current user.

    Forms.py methods authenticate password
    and validate unique username and/or email
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = EditUser(obj=g.user)
    if form.validate_on_submit():

        g.user.username = form.username.data
        g.user.email = form.email.data
        g.user.image_url = (form.image_url.data or DEFAULT_IMAGE_URL)
        g.user.header_image_url = (
            form.header_image_url.data or DEFAULT_HEADER_IMAGE_URL) #format?
        g.user.bio = form.bio.data
        g.user.location = form.location.data

        db.session.commit()
        return redirect(f'/users/{g.user.id}')

    return render_template('/users/edit.html', form=form)

#missing csrf protection, check elswhere too
@app.post('/users/delete')
def delete_user():
    """Delete user.

    Redirect to signup page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form
    if form.validate_on_submit():

        user = g.user
        do_logout()

        Message.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()

    return redirect("/signup")

@app.get('/users/<int:user_id>/likes')
def show_likes(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    liked_messages = user.liked_messages

    return render_template(
        'users/show.html', user=user, messages=liked_messages)
