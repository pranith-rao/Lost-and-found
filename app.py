from flask import Flask,redirect,render_template,url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
#from . import db
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost&found.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login_form'
login_manager.login_message = "Please log in to access this page"
login_manager.login_message_category = "error"

@login_manager.user_loader
def load_user(user_id):
  return Station.query.filter_by(id=user_id).first()


class Station(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    contact_no = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return '<Station {}>'.format(self.name)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    place_found = db.Column(db.String(50), nullable=False)
    date_found = db.Column(db.String(10), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    station = db.relationship('Station')

db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login_form")
def login_form():
    return render_template("login.html")

@app.route("/signup_form")
def signup_form():
    return render_template("signup.html")

@app.route("/enteritem_form")
@login_required
def enteritem_form():
    return render_template("enteritem.html")

@app.route("/viewitem")
def viewitem():
    items = Item.query.all()
    search = request.args.get('search')
    if search:
        items = Item.query.filter_by(name=search)
    return render_template('viewitem.html', items=items)

@app.route("/signup", methods=['POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        phno = request.form['phno']
        address = request.form['address']
        if pass1 == pass2:
            name_check = Station.query.filter_by(name=name).first()
            if not name_check:
                hash_pass = generate_password_hash(pass1, method='sha256')
                station = Station(name=name,address=address,contact_no=phno,email=email,password_hash=hash_pass)
                db.session.add(station)
                db.session.commit()
                flash("Station Registration successful","success")
                return redirect(url_for("login_form"))
            else:
                flash("Station Name already taken","error")
                return redirect(url_for("signup_form"))
        else:
            flash("Passwords dont match","error")
            return redirect(url_for("signup_form"))

@app.route("/login", methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass1']
        station = Station.query.filter_by(email=email).first()
        if not station:
            flash("Station not registered",'error')
            return redirect(url_for("login_form"))
        else:
            checkpass = check_password_hash(station.password_hash,password)
            if checkpass == True:
                login_user(station)
                flash("Login Successful",'success')
                return redirect(url_for("enteritem_form"))
            else:
                flash("Invalid Password",'error')
                return redirect(url_for("login_form"))

@app.route("/enteritem",methods=["POST"])
@login_required
def enteritem():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['desc']
        place_found = request.form['place']
        date_found = request.form['date']
        item = Item(name=name,description=description,place_found=place_found,date_found=str(date_found),station_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash("Item Added Successfully",'success')
        return redirect(url_for("enteritem_form"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
