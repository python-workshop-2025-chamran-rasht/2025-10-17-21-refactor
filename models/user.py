from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from extensions import db
from flask_login import UserMixin
from models.followers import followers_table
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    followers: so.WriteOnlyMapped["User"] = so.relationship(
        back_populates="followings",
        secondary=followers_table,
        primaryjoin=followers_table.c.following_id == id,
        secondaryjoin=followers_table.c.follower_id == id,
    )

    followings: so.WriteOnlyMapped["User"] = so.relationship(
        back_populates="followers",
        secondary=followers_table,
        primaryjoin=followers_table.c.follower_id == id,
        secondaryjoin=followers_table.c.following_id == id,
    )

    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def follow(self, user: 'User'):
        if not self.is_following(user):
            self.followings.add(user)

    def unfollow(self, user: 'User'):
        if self.is_following(user):
            self.followings.remove(user)

    def is_following(self, user: 'User'):
        query = self.followings.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

    def followings_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followings.select().subquery()
        )
        return db.session.scalar(query)

    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)

        return (
            sa.select(Post)
                .join(Post.author.of_type(Author))
                .join(Author.followers.of_type(Follower))
                .where(Follower.id == self.id)
                .order_by(Post.timestamp.desc())
        )

from models.post import Post  # noqa: E402
