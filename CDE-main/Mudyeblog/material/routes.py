import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from material import app, db, bcrypt
from material.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from material.models import *
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/enter")
def enter():
    return render_template('enter.html', title='Welcome')


@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/aboutpage")
def aboutpage():
    return render_template('aboutpage.html', title='About Us')


@app.route("/login1", methods=['GET', 'POST'])
def login1():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Welcome to Mud Ye Blog!', 'warning')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Wrong email or password! Please type again!', 'danger')
    return render_template('login1.html', title='Login', form=form)


@app.route("/register1", methods=['GET', 'POST'])
def register1():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Lets login!', 'primary')
        return redirect(url_for('login1'))
    return render_template('register1.html', title='Register Account', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('enter'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated!', 'primary')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='account_pics/' + current_user.image_file)
    return render_template('account.html', title='Your Account', image_file=image_file, form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/account_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@app.route("/post/newpost", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Done! Post has been created.', 'primary')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='Create Post', form=form, legend="Creating Post Here~")


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.all()
    if request.method == "POST":
        comment = request.form.get("comment")
        dbcomment = Comment(text=comment, user_id=current_user.id, post_id=post_id)
        db.session.add(dbcomment)
        db.session.commit()
    return render_template('user_post.html', post=post, comments=comments)


@app.route("/post/<int:post_id>/updatepost", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!', 'primary')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title='Update', form=form, legend="Update Your Post Here~")

@app.route("/post/<int:post_id>/deletepost", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'primary')
    return redirect(url_for('home'))

