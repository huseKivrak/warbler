from flask import render_template, flash, redirect, g, request

from forms import MessageForm
from models import db, Message, Like
from app import app

#############################################################################
# GET ROUTES


@app.get('/messages/<int:message_id>')
def show_message(message_id):
    """Show a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg, form=form)

#############################################################################
# POST ROUTES


@app.route('/messages/new', methods=["GET", "POST"])
def add_message():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/create.html', form=form)


@app.post('/messages/<int:message_id>/delete')
def delete_message(message_id):
    """Delete a message.

    Check that this message was written by the current user.
    Redirect to user page on success.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    if form.validate_on_submit():
        msg = Message.query.get_or_404(message_id)
        db.session.delete(msg)
        db.session.commit()

    return redirect(f"/users/{g.user.id}")

#############################################################################
# LIKES AND DISLIKES


@app.post('/messages/<int:message_id>/like')
def like_message(message_id):
    """Likes a message"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    if form.validate_on_submit():
        like = Like(user_id=g.user.id, message_id=message_id)

        db.session.add(like)
        db.session.commit()

        url = request.form['url']
        return redirect(url)

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")


@app.post('/messages/<int:message_id>/unlike')
def unlike_message(message_id):
    """Unlikes a message"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = g.csrf_form

    if form.validate_on_submit():
        likes = g.user.likes
        like = [l for l in likes if l.message_id == message_id][0]

        db.session.delete(like)
        db.session.commit()

        url = request.form['url']

        return redirect(url)

    else:
        flash("Access unauthorized.", "danger")
        return redirect("/")
