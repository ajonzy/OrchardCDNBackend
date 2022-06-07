from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ""

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

# SQLAlchemy Tables
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Integer, nullable=False, unique=False)
    
    def __init__(self, start_date):
        self.start_date = start_date
        

# Marshmallow Schemas
class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "start_date")

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
        return "Error: Data must be sent as JSON."

    data = request.get_json()
    start_date = data.get("start_date")

    record = Event(start_date)
    db.session.add(record)
    db.session.commit()

    return ["Event Added", jsonify(event_schema.dump(record))]

@app.route("/event/update/<id>", methods=["PUT"])
def update_event(id):
    if request.content_type != "application/json":
        return "Error: Data must be sent as JSON."
        
    data = request.get_json()
    start_date = data.get("start_date")

    record = db.session.query(Event).filter(Event.id == id).first()
    record.start_date = start_date
    db.session.commit()

    return ["Event Updated", jsonify(event_schema.dump(record))]

@app.route("/event/delete/<id>", methods=["DELETE"])
def delete_event(id):
    record = db.session.query(Event).filter(Event.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return ["Event Deleted", jsonify(event_schema.dump(record))]


if __name__ == "__main__":
    app.run(debug=True)