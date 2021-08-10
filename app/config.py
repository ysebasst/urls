import os


class Config:
    SECRET_KEY = "mysec"
    MONGO_URI = os.environ.get("MONGO_URI")
