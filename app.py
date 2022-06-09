from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, base_fields
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import os
import uuid

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
    archived = db.Column(db.Boolean, nullable=False, unique=False)
    registrations = db.relationship("Registration", backref="event", cascade='all, delete, delete-orphan')
    
    def __init__(self, month, start_date, year, lecture_time, clinical_time):
        self.month = month
        self.start_date = start_date
        self.year = year
        self.lecture_time = lecture_time
        self.clinical_time = clinical_time
        self.archived = False


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=False)
    source = db.Column(db.String, nullable=False, unique=False)
    text = db.Column(db.String, nullable=False, unique=False)
    
    def __init__(self, name, source, text):
        self.name = name,
        self.source = source,
        self.text = text


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False, unique=False)
    last_name = db.Column(db.String, nullable=False, unique=False)
    email = db.Column(db.String, nullable=False, unique=False)
    phone = db.Column(db.String, nullable=False, unique=False)
    message = db.Column(db.String, nullable=False, unique=False)
    
    def __init__(self, first_name, last_name, email, phone, message):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.message = message


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False, unique=False)
    last_name = db.Column(db.String, nullable=False, unique=False)
    email = db.Column(db.String, nullable=False, unique=False)
    phone = db.Column(db.String, nullable=False, unique=False)
    amount_paid = db.Column(db.Float, nullable=False, unique=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False, unique=False)
    
    def __init__(self, first_name, last_name, email, phone, amount_paid, event_id):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.amount_paid = amount_paid
        self.event_id = event_id
        

# Marshmallow Schemas
class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "month", "start_date", "year", "lecture_time", "clinical_time", "archived", "registrations_count")
    registrations_count = base_fields.Function(lambda fields: len(fields.registrations))

event_schema = EventSchema()
multiple_event_schema = EventSchema(many=True)


class TestimonialSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "source", "text")

testimonial_schema = TestimonialSchema()
multiple_testimonial_schema = TestimonialSchema(many=True)


class MessageSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "phone", "message")

message_schema = MessageSchema()
multiple_message_schema = MessageSchema(many=True)


class RegistrationSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "phone", "amount_paid", "event_id")

registration_schema = RegistrationSchema()
multiple_registration_schema = RegistrationSchema(many=True)


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
    archived = data.get("archived")

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
    if archived is not None:
        record.archived = archived
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


@app.route("/message/get", methods=["GET"])
def get_all_messages():
    data = db.session.query(Message).all()
    return jsonify(multiple_message_schema.dump(data))

@app.route("/message/add", methods=["POST"])
def add_message():
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })

    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    record = Message(first_name, last_name, email, phone, message)
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Message Added",
        "data": message_schema.dump(record)
    })

@app.route("/message/update/<id>", methods=["PUT"])
def update_message(id):
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })
        
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    record = db.session.query(Message).filter(Message.id == id).first()
    if first_name is not None:
        record.first_name = first_name
    if last_name is not None:
        record.last_name = last_name
    if email is not None:
        record.email = email
    if phone is not None:
        record.phone = phone
    if message is not None:
        record.message = message
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Message Updated",
        "data": message_schema.dump(record)
    })

@app.route("/message/delete/<id>", methods=["DELETE"])
def delete_message(id):
    record = db.session.query(Message).filter(Message.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify({
        "status": 200,
        "message": "Message Deleted",
        "data": message_schema.dump(record)
    })


@app.route("/registration/get", methods=["GET"])
def get_all_registrations():
    data = db.session.query(Registration).all()
    return jsonify(multiple_registration_schema.dump(data))

@app.route("/registration/add", methods=["POST"])
def add_registration():
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })

    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    amount_paid = data.get("amount_paid")
    event_id = data.get("event_id")

    record = Registration(first_name, last_name, email, phone, amount_paid, event_id)
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Registration Added",
        "data": registration_schema.dump(record)
    })

@app.route("/registration/update/<id>", methods=["PUT"])
def update_registration(id):
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })
        
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    amount_paid = data.get("amount_paid")
    event_id = data.get("event_id")

    record = db.session.query(Registration).filter(Registration.id == id).first()
    if first_name is not None:
        record.first_name = first_name
    if last_name is not None:
        record.last_name = last_name
    if email is not None:
        record.email = email
    if phone is not None:
        record.phone = phone
    if amount_paid is not None:
        record.amount_paid = amount_paid
    if event_id is not None:
        record.event_id = event_id
    db.session.commit()

    return jsonify({
        "status": 200,
        "message": "Registration Updated",
        "data": registration_schema.dump(record)
    })

@app.route("/registration/delete/<id>", methods=["DELETE"])
def delete_registration(id):
    record = db.session.query(Registration).filter(Registration.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify({
        "status": 200,
        "message": "Registration Deleted",
        "data": registration_schema.dump(record)
    })


@app.route("/payment", methods=["POST"])
def handle_payment():
    if request.content_type != "application/json":
        return jsonify({
            "status": 400,
            "message": "Error: Data must be sent as JSON.",
            "data": {}
        })
        
    data = request.get_json()
    source_id = data.get("nonce")
    verification_token = data.get("token")
    amount = data.get("amount")
    if amount is not None:
        amount *= 100

    payload = {
        "source_id": source_id,
        "verification_token": verification_token,
        "autocomplete": True,
        "location_id": os.environ.get("SQUARE_LOCATION_ID"),
        "amount_money": {
            "amount": amount,
            "currency": "USD"
        },
        "idempotency_key": str(uuid.uuid4())
    }

    url = "https://connect.squareupsandbox.com/v2/payments" #TODO: Update url from snadbox url to production url
    r = requests.post(url, json=payload, headers={"Authorization": f"Bearer {os.environ.get('SQUARE_ACCESS_TOKEN')}"})
    return r.json()


@app.route("/data", methods=["GET"])
def get_all_data():
    event_data = db.session.query(Event).filter(Event.archived == False).all()
    testimonial_data = db.session.query(Testimonial).all()
    return jsonify({
        "events": multiple_event_schema.dump(event_data),
        "testimonials": multiple_testimonial_schema.dump(testimonial_data)
    })


if __name__ == "__main__":
    app.run(debug=True)