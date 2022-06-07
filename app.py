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
    
    def __init__(self, month, start_date):
        self.month = month
        self.start_date = start_date
        

# Marshmallow Schemas
class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "month", "start_date")

event_schema = EventSchema()
multiple_event_schema = EventSchema(many=True)


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

    record = Event(month, start_date)
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

    record = db.session.query(Event).filter(Event.id == id).first()
    if month is not None:
        record.month = month
    if start_date is not None:
        record.start_date = start_date
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


if __name__ == "__main__":
    app.run(debug=True)