import os
import secrets
from flask import current_app
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


def save_video(video):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(video.filename)
    video_fn = random_hex + f_ext
    video_path = os.path.join(current_app.root_path, 'static/videos', video_fn)
    video.save(video_path)
    print(f"Saved video to {video_path}")
    return video_fn

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        video_file = None
        if form.video.data:
            video_file = save_video(form.video.data)
            print(f"Video file saved: {video_file}")
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.video.data:
            video_file = save_video(form.video.data)
            print(f"Video file updated: {video_file}")
            post.video_file = video_file
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if post.video_file:
        video_path = os.path.join(current_app.root_path, 'static/videos', post.video_file)
        if os.path.exists(video_path):
            os.remove(video_path)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))
