import os
import json
from datetime import datetime
from flask import Flask, request, abort
from flask_restful import Api
from flask_pymongo import PyMongo
from flask_restful import (Resource, reqparse, fields, marshal)
from bson import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("DB")
MONGO = PyMongo(app)

channel_parser = reqparse.RequestParser()
channel_parser.add_argument("channel", required=True)

channel_fields = {"_id": fields.String, "name": fields.String,
                  "description": fields.String, "updated_at": fields.DateTime,
                  "uri": fields.Url('channel'), "created_at": fields.DateTime,
                  "users_id": fields.List(fields.String)}


def get_user_id():
    try:
        json_obj = json.loads(request.headers.get('current-user')[17:])
        return json_obj["user"]["_id"]
    except Exception as e:
        return None


class ChannelListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("name", type=str, required=True,
                                   help="No channel name provided",
                                   location="json")
        self.reqparse.add_argument("description", type=str, required=True,
                                   help="No channel description provided",
                                   location="json")
        self.reqparse.add_argument("current-user", required=True,
                                   help="No user provided", location="headers")
        super(ChannelListAPI, self).__init__()

    def get(self):
        _data = MONGO.db.channels.find()
        channels_found = [channel for channel in _data]
        return {'channels': [marshal(channel, channel_fields)
                             for channel in channels_found]}

    def post(self):
        args = self.reqparse.parse_args()
        user_id = get_user_id()
        new_channel = {"name": args["name"],
                       "description": args["description"],
                       "created_at": datetime.now(),
                       "updated_at": datetime.now(),
                       "users_id": [user_id]}
        MONGO.db.channels.insert_one(new_channel)
        _last_added = MONGO.db.channels.find().sort([("$natural", -1)]).limit(1)
        last_added = [channel for channel in _last_added]
        return {'channel': [marshal(channel, channel_fields)
                            for channel in last_added]}, 201


class ChannelAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "name",
            type=str,
            required=True,
            help="No channel name provided",
            location="json",
        )
        self.reqparse.add_argument(
            "description",
            type=str,
            required=True,
            help="No channel description provided",
            location="json",
        )
        self.reqparse.add_argument("current-user", required=True,
                                   help="No user provided", location="headers")

        super(ChannelAPI, self).__init__()

    def get(self, _id):
        obj_id = ObjectId(_id)
        channel = MONGO.db.channels.find_one_or_404({"_id": obj_id})
        if get_user_id() not in channel["users_id"]:
            abort(401)
        channel = MONGO.db.channels.find_one_or_404({"_id": obj_id})
        return {"channel": marshal(channel, channel_fields)}

    def put(self, _id):
        obj_id = ObjectId(_id)
        args = self.reqparse.parse_args()
        channel = MONGO.db.channels.find_one_or_404({"_id": obj_id})
        if get_user_id() not in channel["users_id"]:
            abort(401)
        MONGO.db.channels.update({"_id": obj_id},
                                 {"$set": {"name": args["name"],
                                           "description": args["description"],
                                           "updated_at": datetime.now()}})
        channel = MONGO.db.channels.find_one_or_404({"_id": obj_id})
        return {'channel': marshal(channel, channel_fields)}


api = Api(app)

# add api resources
api.add_resource(ChannelListAPI, "/api/v1.0/channels", endpoint="channels")
api.add_resource(ChannelAPI, "/api/v1.0/channels/<string:_id>", endpoint="channel")

if __name__ == "__main__":
    app.run(debug=True)
