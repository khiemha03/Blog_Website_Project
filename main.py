from flask import Flask, render_template, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, EmailField, TelField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_required, LoginManager, logout_user, current_user, login_user
from flask_ckeditor import CKEditor, CKEditorField

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# SQLite URI DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///account.db"

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    # author = db.Column(db.String(50), nullable=False)
    date_post = db.Column(db.DateTime, default= datetime.utcnow)
    slug = db.Column(db.String(500))
    id_poster = db.Column(db.Integer, db.ForeignKey('account.id'))
    comments = db.relationship('Comment', backref='post')
class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable= False)
    password = db.Column(db.String(25), unique= False, nullable = False)
    posts = db.relationship('Post', backref='poster')
    comments = db.relationship('Comment', backref='poster')
    date_create = db.Column(db.DateTime, default=datetime.utcnow)
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    id_author = db.Column(db.Integer, db.ForeignKey('account.id'))
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'))
    date_comment = db.Column(db.DateTime, default=datetime.utcnow)
class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")
class PostForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    name = StringField("Full Name",validators=[DataRequired()])
    birth = DateField("Date of Birth",validators=[DataRequired()])
    email = EmailField("Email",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField("Confirm your password",validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email",validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add-blog", methods=["GET", "POST"])
@login_required
def add_blog():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Post(
            title= form.title.data,
            content = form.content.data,
            slug= form.slug.data,
            id_poster =poster
        )
        form.title.data =''
        form.content.data =''
        form.author.data =''
        form.slug.data =''

        db.session.add(post)
        db.session.commit()
        flash("Your Blog is submitted successfully !")

    return render_template("add_blog.html",form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Account.query.filter_by(email=email).first()
        if user is None:
            flash("Your email or password is incorrect")
        elif check_password_hash(user.password, password):
            login_user(user)
            return Flask.redirect(app, url_for("index"))
        else:
            flash("Your email or password is incorrect")
    return render_template("login.html", form=form)
        # email_account = request.form["email"]
        # password_account = request.form["password"]
        # user = Account.query.filter_by(email=email_account).first()
        #
        #
        # if check_password_hash(user.password, password_account):
        #     login_user(user)
        #     return Flask.redirect(app,url_for("index"))
        # if email_account == "" or password_account == "":
        #     flash("Your email or password is incorrect")
        #     return Flask.redirect(app,url_for("login_page"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Flask.redirect(app,url_for("index"))


@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password = form.password.data
        confirm_password = form.confirm_password.data

        user = Account.query.filter_by(email=form.email.data).first()
        if password != confirm_password:
            flash("Please confirm your password correctly!")
        elif user is None:
            user = Account(
                name= form.name.data,
                birth = form.birth.data,
                email = form.email.data,
                password = generate_password_hash(form.password.data,"pbkdf2:sha256",8)

            )
            form.name.data =''
            form.birth.data ='%Y-%m-%d'
            form.email.data =''
            form.password.data =""
            form.confirm_password.data =""

            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully!")
        else:
            flash("The email is already existed !")
            form.email.data = ''
    # register_password = request.form["register_password"]
    # register_confirm_password = request.form["register_confirm_password"]
    # checkbox = request.form.getlist('register_checkbox')
    # if register_password != register_confirm_password:
    #     flash("Please confirm your password correctly!")
    # elif checkbox == []:
    #     flash("Please fill in the checkbox")
    # else:
    #     register_name = request.form["name"]
    #     register_email = request.form["register_email"]
    #     salted_password = generate_password_hash(register_password,"pbkdf2:sha256",8)
    #
    #     new_user = Account(
    #         name = register_name,
    #         email = register_email,
    #         password=salted_password
    #     )
    #     db.session.add(new_user)
    #     db.session.commit()
    #     # login_user(new_user)
    #     return Flask.redirect(app, url_for("login_page"))
    return render_template("register.html",form = form)

@app.route("/reset")
def change_page():
    return render_template("change.html")

@app.route("/reset", methods=["POST"])
def change():
    email_change_section = request.form["email"]
    password_change_section = request.form["password"]
    email_finding = Account.query.filter_by(email=email_change_section).first()
    if email_change_section == '' or password_change_section == "":
        flash("Please type in your email and password")
        return Flask.redirect(app,url_for("change_page"))
    elif email_finding == None :
        flash("Your password or email is incorrect")
        return Flask.redirect(app,url_for("change_page"))

    elif email_finding != None :
        if check_password_hash(email_finding.password, password_change_section):
            return render_template("edit_user.html",
                       account= email_finding)
        else:
            flash("Your password or email is incorrect")
            return Flask.redirect(app,url_for("change_page"))

@app.route("/edit-user/<user_id>", methods=["POST"])
def edit_user(user_id):
    new_password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    account_finding = Account.query.filter_by(id=user_id).first()
    if new_password != confirm_password:
        flash("Your confirm password is not correct!")
        return render_template("edit_user.html", account=account_finding)
    else:
        salted_password = generate_password_hash(new_password, "pbkdf2:sha256", 8)
        account_finding.password = salted_password
        db.session.commit()
        return Flask.redirect(app, url_for("login_page"))

@app.route("/blog/<id_post>", methods= ["GET","POST"])
def individual_blog(id_post):
    comments = Comment.query.order_by(Comment.date_comment)
    form = CommentForm()
    if form.validate_on_submit():
        print(123)
        poster = current_user.id
        comment = Comment(
            text = form.comment.data,
            id_author= poster,
            id_post = id_post
        )
        form.comment.data = ""
        db.session.add(comment)
        db.session.commit()
        return Flask.redirect(app, url_for("individual_blog", id_post=id_post))
    post = Post.query.filter_by(id=id_post).first()
    return render_template("blog.html",post=post, form=form, comments=comments)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    post = Post.query.order_by(Post.date_post)
    return render_template("dashboard.html", posts=post)

@app.route("/{{current_user.id}}/blog")
def user_blog():
    post = Post.query.order_by(Post.date_post)
    return render_template("user_blog.html", posts=post)

@app.route("/search", methods= ["GET", "POST"])
def search():
    search_input = request.args.get('search')
    posts = Post.query.order_by(Post.date_post)
    search_post = []
    for post in posts:
        if search_input in post.title:
            search_post.append(post)
    return render_template("dashboard.html", posts=search_post)

@app.route("/delete/<id_post>", methods= ["GET", "POST"])
def delete(id_post):
    delete_post = Post.query.filter_by(id=id_post).first()
    db.session.delete(delete_post)
    db.session.commit()
    post = Post.query.order_by(Post.date_post)
    return render_template("user_blog.html", posts=post)

@app.route("/edit-post/<id_post>", methods=["GET", "POST"] )
@login_required
def edit(id_post):
    edit_post = Post.query.filter_by(id=id_post).first()
    form = PostForm()
    if form.validate_on_submit():
        edit_post.title = form.title.data
        edit_post.slug = form.slug.data
        edit_post.content = form.content.data
        db.session.add(edit_post)
        db.session.commit()
        return Flask.redirect(app, url_for("individual_blog", id_post=id_post))
    form.title.data = edit_post.title
    form.slug.data = edit_post.slug
    form.content.data = edit_post.content
    return render_template("edit_post.html",form=form, id= id_post)

@app.route("/profile_view")
def profile_view():
    count = 0
    posts = Post.query.order_by(Post.date_post)
    for post in posts:
        if post.id_poster == current_user.id:
            count +=1
    return render_template("profile_view.html", count= count)

if __name__ == "__main__":
    app.run(debug=True)
