from flask_login import (LoginManager, login_user,
                         logout_user, login_required, current_user)
from flask_bcrypt import check_password_hash
from flask import (Flask, g, render_template, flash,
                   redirect, url_for, abort)
import pdb



import forms
import models


app = Flask(__name__)
app.secret_key = 'asdfsidgjojescjoijsoijcoi233109'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to DB before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close DB connection after each request"""
    g.db.close()
    return response


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash('Thanks', 'success')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash('Completed!', 'success')
        models.User.create_user(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
@login_required
def stream(username=None):
    if current_user.is_authenticated:
        template = 'stream.html'
        if username and username != current_user.username:
            try:
                user = models.User.select().where(models.User.username**username).get()
            except models.DoesNotExist:
                abort(404)
            else:
                stream = user.post.limit(100)
        else:
            user = current_user
            stream = current_user.get_stream().limit(100)
        if username:
            template = 'user_stream.html'
        return render_template(template, stream=stream, user=user)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    return render_template('stream.html', stream=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("You are following {}".format(to_user.username), 'success')
    return redirect(url_for('stream', username=to_user.username))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Success')
                return redirect(url_for('index'))
            else:
                flash('Name or Email does not match', 'error')
        except models.DoesNotExist:
            flash("Name or Email does not match", 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are not logged out", "success")
    return redirect(url_for('login'))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
        else:
            flash("You've unfollowed {}".format(to_user.username), 'success')
    return redirect(url_for('stream', username=to_user.username))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='DouglasNorth',
            email='Douglasnorthca@gmail.com',
            password='dpn1993',
            admin=True
            )
    except ValueError:
        pass

    app.run(debug=True, host='0.0.0.0', port=8000)
