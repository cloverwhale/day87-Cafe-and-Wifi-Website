import json
import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    row_count = Cafe.query.count()
    random_number = random.randint(0, row_count - 1)
    random_cafe = Cafe.query.filter_by(id=random_number).first()
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafe():
    cafes = Cafe.query.all()
    cafes_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=cafes_list)


@app.route("/search")
def search():
    search_location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=search_location).all()
    cafes_list = [cafe.to_dict() for cafe in cafes]
    not_found = {"Not Found": "Sorry, we don't have a cafe at that location."}
    if len(cafes_list) == 0:
        return jsonify(error=not_found), 404
    else:
        return jsonify(cafes=cafes_list)


@app.route("/add", methods=["POST"])
def add():
    cafe_to_add = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=json.loads(request.form.get("has_toilet").lower()),
        has_wifi=json.loads(request.form.get("has_wifi").lower()),
        has_sockets=json.loads(request.form.get("has_sockets").lower()),
        can_take_calls=json.loads(request.form.get("can_take_calls").lower()),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(cafe_to_add)
    db.session.commit()
    success = {"success": "Successfully added the new cafe."}
    return jsonify(response=success), 201


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
    not_found = {"Not Found": "Sorry a cafe with that id was not found in the database."}
    success_update_price = {"success": "Successfully update the price."}
    if cafe_to_update is None:
        return jsonify(error=not_found), 404
    else:
        cafe_to_update.coffee_price = request.form.get("new_price")
        db.session.commit()
        return jsonify(response=success_update_price)


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    cafe_to_delete = Cafe.query.filter_by(id=cafe_id).first()
    key = request.args.get("api-key")
    if key != "MySecretKey":
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key."), 403
    elif cafe_to_delete is None:
        return jsonify(error="Sorry a cafe with that id was not found in the database."), 404
    else:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200


if __name__ == '__main__':
    app.run(debug=True)
