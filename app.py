from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://" + os.environ.get("DATABASE_URL").partition("://")[2]

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

# SQLAlchemy Tables
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String, nullable=False, unique=False)
    start_date = db.Column(db.Integer, nullable=False, unique=False)
    year = db.Column(db.Integer, nullable=False, unique=False)
    lecture_time = db.Column(db.String, nullable=False, unique=False)
    clinical_time = db.Column(db.String, nullable=False, unique=False)
    signups = db.Column(db.Integer, nullable=False, unique=False)
    
    def __init__(self, month, start_date, year, lecture_time, clinical_time):
        self.month = month
        self.start_date = start_date
        self.year = year
        self.lecture_time = lecture_time
        self.clinical_time = clinical_time
        self.signups = 0

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=False)
    source = db.Column(db.String, nullable=False, unique=False)
    text = db.Column(db.String, nullable=False, unique=False)
    
    def __init__(self, name, source, text):
        self.name = name,
        self.source = source,
        self.text = text
        

# Marshmallow Schemas
class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "month", "start_date", "year", "lecture_time", "clinical_time", "signups")

event_schema = EventSchema()
multiple_event_schema = EventSchema(many=True)

class TestimonialSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "source", "text")

testimonial_schema = TestimonialSchema()
multiple_testimonial_schema = TestimonialSchema(many=True)


# Flask Endpoints
@app.route("/event/get", methods=["GET"])
def get_all_events():
    data = db.session.query(Event).all()
    return jsonify(multiple_event_schema.dump(data))

@app.route("/event/add", methods=["POST"])
def add_event():
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })

    data = request.get_json()
    month = data.get("month")
    start_date = data.get("start_date")
    year = data.get("year")
    lecture_time = data.get("lecture_time")
    clinical_time = data.get("clinical_time")

    record = Event(month, start_date, year, lecture_time, clinical_time)
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Event Added",
        "data": event_schema.dump(record)
    })

@app.route("/event/update/<id>", methods=["PUT"])
def update_event(id):
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })
        
    data = request.get_json()
    month = data.get("month")
    start_date = data.get("start_date")
    year = data.get("year")
    lecture_time = data.get("lecture_time")
    clinical_time = data.get("clinical_time")
    signups = data.get("signups")

    record = db.session.query(Event).filter(Event.id == id).first()
    if month is not None:
        record.month = month
    if start_date is not None:
        record.start_date = start_date
    if year is not None:
        record.year = year
    if lecture_time is not None:
        record.lecture_time = lecture_time
    if clinical_time is not None:
        record.clinical_time = clinical_time
    if signups is not None:
        record.signups = signups
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Event Updated",
        "data": event_schema.dump(record)
    })

@app.route("/event/delete/<id>", methods=["DELETE"])
def delete_event(id):
    record = db.session.query(Event).filter(Event.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify({
        "status": 200,
        "message": "Event Deleted",
        "data": event_schema.dump(record)
    })


@app.route("/testimonial/get", methods=["GET"])
def get_all_testimonials():
    data = db.session.query(Testimonial).all()
    return jsonify(multiple_testimonial_schema.dump(data))

@app.route("/testimonial/add", methods=["POST"])
def add_testimonial():
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })

    data = request.get_json()
    name = data.get("name")
    source = data.get("source")
    text = data.get("text")

    record = Testimonial(name, source, text)
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Testimonial Added",
        "data": testimonial_schema.dump(record)
    })

@app.route("/testimonial/update/<id>", methods=["PUT"])
def update_testimonial(id):
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })
        
    data = request.get_json()
    name = data.get("name")
    source = data.get("source")
    text = data.get("text")

    record = db.session.query(Testimonial).filter(Testimonial.id == id).first()
    if name is not None:
        record.name = name
    if source is not None:
        record.source = source
    if text is not None:
        record.text = text
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Testimonial Updated",
        "data": testimonial_schema.dump(record)
    })

@app.route("/testimonial/delete/<id>", methods=["DELETE"])
def delete_testimonial(id):
    record = db.session.query(Testimonial).filter(Testimonial.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify({
        "status": 200,
        "message": "Testimonial Deleted",
        "data": testimonial_schema.dump(record)
    })


if __name__ == "__main__":
    app.run(debug=True)