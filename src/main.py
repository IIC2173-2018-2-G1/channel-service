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

channel_fields = {"id": fields.String, "name": fields.String,
                  "description": fields.String}


def marshal_channel(channel):
    return {"id": str(channel["_id"]), "name": channel["name"], "description": channel["description"]}


class ChannelListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("name", type=str, required=True,
                                   help="No channel name provided",
                                   location="json")
        self.reqparse.add_argument("description", type=str, required=True,
                                   help="No channel description provided",
                                   location="json")
        super(ChannelListAPI, self).__init__()

    def get(self):
        _data = MONGO.db.channels.find()
        return [marshal_channel(channel) for channel in _data]

    def post(self):
        args = self.reqparse.parse_args()
        if (MONGO.db.channels.find({"name": args["name"]}).count()) == 0:
            new_channel = {"name": args["name"],
                           "description": args["description"],
                           "created_at": datetime.now(),
                           "updated_at": datetime.now()}
            MONGO.db.channels.insert_one(new_channel)
            _last_added = list(MONGO.db.channels.find().sort(
                [("$natural", -1)]).limit(1))[0]
            return marshal_channel(_last_added), 201
        else:
            abort(403, 'Channel name already in use')


class ChannelAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "action",
            type=str,
            required=True,
            help="No action provided",
            location="json",
        )
        super(ChannelAPI, self).__init__()

    def get(self, _id):
        obj_id = ObjectId(_id)
        channel = MONGO.db.channels.find_one_or_404({"_id": obj_id})
        return marshal_channel(channel)

    def put(self, _id):
        obj_id = ObjectId(_id)
        MONGO.db.channels.find_one_or_404({"_id": obj_id})
        
        user_id = request.headers.get("X-User-ID")
        action = self.reqparse.parse_args()["action"]
        data = {"channel_id": _id, "user_id": user_id}
        if action == "subscribe":
            MONGO.db.subscriptions.update(data, data, upsert=True)
            return "", 204
        elif action == "unsubscribe":
            MONGO.db.subscriptions.delete_one(data)
            return "", 204            
        else:
            return abort(400, 'Invalid action')


api = Api(app)

# add api resources
api.add_resource(ChannelListAPI, "/", endpoint="channels")
api.add_resource(ChannelAPI, "/<string:_id>",
                 endpoint="channel")

if __name__ == "__main__":
    app.run(debug=True)
