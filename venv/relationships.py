from datetime import datetime

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'adfpu31kljhs'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/relationships.db'

db = SQLAlchemy(app)

class NewPostForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
    body = TextAreaField(validators=[DataRequired()])
    
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    posts = db.relationship('Post', backref=db.backref('Author'))
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(Author.id))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    body = db.Column(db.Text)

@app.route('/post', methods=['GET','POST'])
def post():
    form = NewPostForm()
    if form.validate_on_submit():
        new_post = Post(body=form.body.data)
        author = Author.query.filter(Author.email == form.email.data).one_or_none()
        print(author)
        if author is None:
            author = Author(name=form.name.data, email=form.email.data)
        author.posts.append(new_post)
        
        db.session.add(author)
        
        db.session.commit()
        print('redirecting')
        return redirect(url_for('post'), 303)
    return render_template('index.html', form=form)

@app.route('/post/<id>')
def get_post(id):
    requested_post = Post.query.get_or_404(id)
    return render_template('showpost.html', body=requested_post.body, author=requested_post.Author.name)

@app.route('/author/<email>')
def get_posts(email):
    author = Author.query.filter(Author.email == email).first_or_404()
    posts = [p.body for p in author.posts]
    return render_template('posts.html', name=author.name, posts=posts)

if __name__ == '__main__':
    db.create_all(app=app)
    app.run(host='0.0.0.0')
    
   