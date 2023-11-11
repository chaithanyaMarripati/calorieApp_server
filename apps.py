from flask import Flask
from pymongo import MongoClient
from flask_mail import Mail


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "secret"
        self.app.config[
            "MONGO_URI"
        ] = "mongodb+srv://bsuryad:7aQKwjmb6DwcXmWM@se18fall2023.fjqyxoi.mongodb.net/"
        self.mongoClient = MongoClient(
            "mongodb+srv://bsuryad:7aQKwjmb6DwcXmWM@se18fall2023.fjqyxoi.mongodb.net/"
        )

        self.app.config["MAIL_SERVER"] = "smtp.gmail.com"
        self.app.config["MAIL_PORT"] = 465
        self.app.config["MAIL_USE_SSL"] = True
        self.app.config["MAIL_USERNAME"] = "bogusdummy123@gmail.com"
        self.app.config["MAIL_PASSWORD"] = "helloworld123!"
        self.mail = Mail(self.app)


# creating a singleton class for db client
class Mongo:
    def __init__(self):
        self.mongoClient = MongoClient(
            "mongodb+srv://bsuryad:7aQKwjmb6DwcXmWM@se18fall2023.fjqyxoi.mongodb.net/"
        )["test"]
