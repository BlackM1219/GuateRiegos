import os

class Config:
    SECRET_KEY = "guateriegos_secret"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
