from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

API_KEY = "TopSecretAPIKey"

app = Flask(__name__)

#Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#Cafe TABLE Configuration
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

#Create the routes of the API

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe={"name": random_cafe.name,
                         "map_url": random_cafe.map_url,
                         "img_url": random_cafe.img_url,
                         "location": random_cafe.location,
                         "seats": random_cafe.seats,
                         "has_toilet": random_cafe.has_toilet,
                         "has_wifi": random_cafe.has_wifi,
                         "has_sockets": random_cafe.has_sockets,
                         "can_take_calls": random_cafe.can_take_calls,
                         "coffee_price": random_cafe.coffee_price,
                         }
                   )

@app.route("/all")
def return_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search_cafe_for_location():
    location = request.args.get('loc')
    all_cafes = db.session.query(Cafe).all()
    cafe_list = [cafe.to_dict() for cafe in all_cafes if cafe.location == location]
    if cafe_list:
        return jsonify(cafe=cafe_list)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at this location"})


@app.route("/add", methods=["GET", "POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<cafe_id>", methods=["GET", "PATCH"])
def update_price(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = request.args.get("price")
        db.session.commit()
        return jsonify(response={"success": "Successfully edit the price"})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id doesn't exist in the database"})


@app.route("/report-closed/<cafe_id>", methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == API_KEY:
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."})
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id doesn't exist in the database."})
    else:
        return jsonify(error={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."})


if __name__ == '__main__':
    app.run(debug=True)
