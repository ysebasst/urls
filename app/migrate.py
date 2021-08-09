from .models import *


def create_db():
    # db.drop_all()
    db.create_all()


def init_db():
    create_db()
