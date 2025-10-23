import sqlalchemy as sa
from extensions import db

followers_table = sa.Table(
    "followers",
    db.metadata,
    sa.Column("follower_id", sa.Integer, sa.ForeignKey("user.id"), primary_key=True),
    sa.Column("following_id", sa.Integer, sa.ForeignKey("user.id"), primary_key=True),
)
