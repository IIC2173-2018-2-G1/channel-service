import os
from datetime import datetime
from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from flask_restful import (Resource, reqparse, fields, marshal)

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("DB")
MONGO = PyMongo(app)

hashtag_parser = reqparse.RequestParser()
hashtag_parser.add_argument("hashtag", required=True)

hashtag_fields = {"_id": fields.String, "name": fields.String,
                  "user_id": fields.Integer, "date": fields.DateTime}


class HashtagListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "name",
            type=str,
            required=True,
            help="No hashtag name provided",
            location="json",
        )
        self.reqparse.add_argument("description", type=str, default="",
                                   location="json")
        self.user_id = 1
        super(HashtagListAPI, self).__init__()

    def get(self):
        _data = MONGO.db.hashtags.find()
        hashtags = [hashtag for hashtag in _data]
        return {'hashtags': [marshal(hashtag, hashtag_fields)
                             for hashtag in hashtags]}

    def post(self):
        args = self.reqparse.parse_args()
        hashtag = {"name": args["name"], "user_id": self.user_id,
                   "date": datetime.now()}
        MONGO.db.hashtags.insert_one(hashtag)
        _last_added = MONGO.db.hashtags.find().sort([("$natural", -1)]).limit(1)
        last_added = [hashtag for hashtag in _last_added]
        return {'hashtags': [marshal(hashtag, hashtag_fields)
                             for hashtag in last_added]}, 201


# class HashtagAPI(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument("name", type=str, location="json")
#         super(HashtagAPI, self).__init__()

#     def get(self, id):
#         hashtag = MONGO.db.hashtags.find_one_or_404({"_id": id})
#         if len(hashtag) == 0:
#             abort(404)
#         return {"hashtag": marshal(hashtag, hashtag_fields)}


api = Api(app)

# add api resources
api.add_resource(HashtagListAPI, "/api/v1.0/hashtags", endpoint="hashtags")
# api.add_resource(HashtagAPI, "/api/v1.0/hashtags/<int:id>", endpoint="hashtag")

if __name__ == "__main__":
    app.run(debug=True)
