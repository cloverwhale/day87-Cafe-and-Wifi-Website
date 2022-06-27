from functools import wraps

from flask import Flask, render_template, flash, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from forms import LoginForm, RegisterForm, CreateCafeForm
from datetime import datetime as dt
import os

app = Flask(__name__)

# Database support
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///cafes.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User session related
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)

# Forms and template
Bootstrap(app)


# Database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    cafes = relationship("Cafe", back_populates="updated_by")


class Cafe(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    location = db.Column(db.String(250), unique=False)
    map_url = db.Column(db.String(500), unique=False)
    img_url = db.Column(db.String(500), unique=False)
    has_wifi = db.Column(db.Boolean, unique=False)
    has_sockets = db.Column(db.Boolean, unique=False)
    has_toilet = db.Column(db.Boolean, unique=False)
    can_take_calls = db.Column(db.Boolean, unique=False)
    seats = db.Column(db.String(250), unique=False, nullable=True)
    coffee_price = db.Column(db.String(250), unique=False, nullable=True)
    creation_time = db.Column(db.DateTime, nullable=False)
    modification_time = db.Column(db.DateTime, nullable=False)
    updated_by_id = db.Column(db.Integer, ForeignKey('users.id'))
    updated_by = relationship("User", back_populates="cafes")


# db.create_all()

# User session ------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


# -------------------------------------------------------------------------

@app.route("/")
def list_all_cafes():
    cafes = Cafe.query.all()
    return render_template("index.html", all_cafes=cafes)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        salted_pass = generate_password_hash(
            password=register_form.password.data, method='pbkdf2:sha256', salt_length=8
        )
        user_to_add = User(
            email=register_form.email.data,
            name=register_form.name.data,
            password=salted_pass
        )
        try:
            db.session.add(user_to_add)
            db.session.commit()
            login_user(user_to_add)
        except IntegrityError:
            flash('User already exists, Please try with another email or name.')
            return redirect(url_for('register'))
        return redirect(url_for("list_all_cafes"))
    return render_template("register.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        request_email = login_form.email.data
        request_password = login_form.password.data
        get_user = User.query.filter_by(email=request_email).first()
        if not get_user:
            flash('User not found or password incorrect.')
            return redirect(url_for('login'))
        elif not check_password_hash(get_user.password, request_password):
            flash('User not found or password incorrect.')
            return redirect(url_for('login'))
        else:
            login_user(get_user)
        return redirect(url_for("list_all_cafes"))
    return render_template("login.html", form=login_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("list_all_cafes"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def create_cafe_data():
    create_form = CreateCafeForm()
    if create_form.validate_on_submit():
        cafe_to_add = Cafe(
            name=create_form.name.data,
            location=create_form.location.data,
            map_url=create_form.map_url.data,
            img_url=create_form.img_url.data,
            has_wifi=to_boolean(create_form.has_wifi.data),
            has_sockets=to_boolean(create_form.has_sockets.data),
            has_toilet=to_boolean(create_form.has_toilet.data),
            can_take_calls=to_boolean(create_form.can_take_calls.data),
            seats=create_form.seats.data,
            coffee_price=create_form.coffee_price.data,
            creation_time=dt.now(),
            modification_time=dt.now(),
            updated_by=current_user
        )
        print(create_form.has_wifi.data)
        print(to_boolean(create_form.has_wifi.data))
        try:
            db.session.add(cafe_to_add)
            db.session.commit()
        except IntegrityError:
            flash('Error add cafe, Please try again.')
            return redirect(url_for('add'))
        return redirect(url_for("list_all_cafes"))
    return render_template("edit.html", form=create_form)


@app.route("/edit/<int:cafe_id>", methods=["GET", "POST"])
@login_required
def edit_cafe_data(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    edit_form = CreateCafeForm(
        name=cafe.name,
        location=cafe.location,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        has_wifi=to_text(cafe.has_wifi),
        has_sockets=to_text(cafe.has_sockets),
        has_toilet=to_text(cafe.has_toilet),
        can_take_calls=to_text(cafe.can_take_calls),
        seats=cafe.seats,
        coffee_price=cafe.coffee_price,
    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.location = edit_form.location.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.has_wifi = to_boolean(edit_form.has_wifi.data)
        cafe.has_sockets = to_boolean(edit_form.has_sockets.data)
        cafe.has_toilet = to_boolean(edit_form.has_toilet.data)
        cafe.can_take_calls = to_boolean(edit_form.can_take_calls.data)
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee_price.data
        cafe.modification_time = dt.now()
        cafe.updated_by = current_user
        db.session.commit()
        return redirect(url_for("list_all_cafes"))
    return render_template("edit.html", form=edit_form)


@app.route("/delete/<int:cafe_id>")
@login_required
@admin_only
def delete_cafe_data(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('list_all_cafes'))


def to_boolean(arg):
    if arg.upper() == "YES" or arg.upper() == "Y":
        return True
    else:
        return False


def to_text(arg):
    if arg:
        return "Y"
    else:
        return "N"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5301, debug=True)
