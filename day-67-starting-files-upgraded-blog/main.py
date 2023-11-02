from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)

# Initializing CKEditer
ckeditor = CKEditor(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class AddForm(FlaskForm):
    title = StringField('The blog post title', validators=[DataRequired()])
    subtitle = StringField('The subtitle', validators=[DataRequired()])
    body = CKEditorField('The body (the main content) of the post', validators=[DataRequired()])
    author = StringField("The author's name", validators=[DataRequired()])
    img_url = StringField('A URL for the background image', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit Post')

with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = []
    results = db.session.execute(db.select(BlogPost).order_by(BlogPost.id))
    posts = results.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route("/post")
def show_post():
    post_id = request.args.get('post_id')
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id==int(post_id))).scalar()
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route("/add", methods=['POST', 'GET'])
def add_post():
    form = AddForm()
    if request.method == 'POST':
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: edit_post() to change an existing blog post
@app.route("/edit/<int:post_id>", methods=['POST', 'GET'])
def edit_post(post_id):
    blog_to_edit = db.session.execute(db.select(BlogPost).where(BlogPost.id==int(post_id))).scalar()
    blog_form = AddForm(
                        title=blog_to_edit.title,
                        subtitle=blog_to_edit.subtitle,
                        img_url=blog_to_edit.img_url,
                        author=blog_to_edit.author,
                        body=blog_to_edit.body
                        )
    if blog_form.validate_on_submit():
        blog_to_edit.title = blog_form.title.data
        blog_to_edit.subtitle = blog_form.subtitle.data
        blog_to_edit.img_url = blog_form.img_url.data
        blog_to_edit.author = blog_form.title.data
        blog_to_edit.body = blog_form.body.data
        blog_to_edit.date = date.today().strftime("%B %d, %Y")
        db.session.commit()
        return redirect(url_for("show_post", post_id=blog_to_edit.id))
    return render_template("make-post.html", form=blog_form, is_edit=True)


# TODO: delete_post() to remove a blog post from the database
@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
    blog_to_delete = db.session.execute(db.select(BlogPost).where(BlogPost.id==int(post_id))).scalar()
    db.session.delete(blog_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003, host='127.0.0.1')