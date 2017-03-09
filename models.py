import datetime

from peewee import *
from flask_login import UserMixin, AnonymousUserMixin
from flask_bcrypt import generate_password_hash, check_password_hash

DATABASE = SqliteDatabase('social.db')


class User(UserMixin, Model):
    username = CharField(max_length=150, unique=True)
    email = CharField(max_length=150, unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_post(self):
        """Returns all posts from the user"""
        return Post.select().where(Post.user == self)

    def get_stream(self):
        """Returns all posts from the user"""
        return Post.select().where(
            (Post.user << self.following()),
            (Post.user == self)
        )

    def following(self):
        """The users we are following"""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """Get users following current user"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user).where(
                Relationship.to_user == self
            )
        )

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        """Alternative method of inputting data"""
        with DATABASE.transaction():
            try:
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
            except IntegrityError:
                raise ValueError("Username is Taken")


class Relationship(Model):
    from_user = ForeignKeyField(rel_model=User, related_name='relationships')
    to_user = ForeignKeyField(rel_model=User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = (
            (('from_user', 'to_user'), True)
        )


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(
        rel_model=User,
        related_name='post'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
