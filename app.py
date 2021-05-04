from flask import Flask,redirect,render_template,url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost&found.db'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)




if __name__ == '__main__':
    app.run(debug=True)
