from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()


# Modelos do Database
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password = db.Column(db.String, nullable=False, unique=False)
    name = db.Column(db.String, nullable=False, unique=False)
    email = db.Column(db.String, nullable=False, unique=True)
    followers = db.Column(db.String, nullable=True, unique=False)
    following = db.Column(db.String, nullable=True, unique=False)
    # Relationship
    # variable can be anything so as arg = "backref"
    # "backref" will be used to instantiate a Post object
    # The table's name must be the ORM name
    posts = db.relationship("Post", backref="owner")

    def __init__(self, username, password, name, email):
        self.username = username
        self._password = generate_password_hash(password)
        self.name = name
        self.email = email
        self.followers = ";"
        self.following = ";"

    def get_id(self):
        return self.id

    def verify_password(self, pwd):
        return check_password_hash(self._password, pwd)

    def get_password(self):
        return self._password

    def set_password(self, new_pwd):
        self._password = generate_password_hash(new_pwd)
        return self._password

    def follow(self, to_follow):
        self.following += ";" + to_follow.username
        to_follow.followers += ";" + self.username
        return self.following, to_follow.followers

    def unfollow(self, to_follow):
        following = self.following.split(" ")
        following.remove(to_follow)
        return self.following

    def create_post(self, content):
        Post(content=content, user_id=self.id)
        post = Post.query.filter_by(content=content).first()
        self.posts_id += ";" + post.id
        post.user_id += ";" + self.id
        return post


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False, unique=False)
    # Relationship
    # Attribute of the column owner_id but as said before
    # when create an object we will use owner =]
    # here the <user> in 'user.id' must be the tablename
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# Usado para criar as tabelas
db.create_all()
