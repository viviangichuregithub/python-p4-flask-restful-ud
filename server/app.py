#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

# Home route
class Index(Resource):
    def get(self):
        return make_response(
            {"message": "Welcome to the Newsletter RESTful API"},
            200
        )

api.add_resource(Index, '/')

# Collection route: GET all, POST new
class Newsletters(Resource):
    def get(self):
        newsletters = [n.to_dict() for n in Newsletter.query.all()]
        return make_response(newsletters, 200)

    def post(self):
        data = request.form
        new_record = Newsletter(
            title=data.get('title'),
            body=data.get('body')
        )
        db.session.add(new_record)
        db.session.commit()
        return make_response(new_record.to_dict(), 201)

api.add_resource(Newsletters, '/newsletters')

# Individual resource route: GET, PATCH, DELETE
class NewsletterByID(Resource):
    def get(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        if record:
            return make_response(record.to_dict(), 200)
        return make_response({"error": "Newsletter not found"}, 404)

    def patch(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        if not record:
            return make_response({"error": "Newsletter not found"}, 404)

        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.commit()
        return make_response(record.to_dict(), 200)

    def delete(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        if not record:
            return make_response({"error": "Newsletter not found"}, 404)

        db.session.delete(record)
        db.session.commit()
        return make_response({"message": "Record successfully deleted"}, 200)

api.add_resource(NewsletterByID, '/newsletters/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
