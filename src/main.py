import os
from datetime import datetime
from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo
from flask_restful import (Resource, reqparse, fields, marshal)

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("DB")
MONGO = PyMongo(app)

channel_parser = reqparse.RequestParser()
channel_parser.add_argument("channel", required=True)

channel_fields = {"_id": fields.String, "name": fields.String,
                  "description": fields.String, "users_sub": fields.List,
                  "uri": fields.Url('channel'), "date": fields.DateTime}


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
        channels_found = [channel for channel in _data]
        return {'channels': [marshal(channel, channel_fields)
                             for channel in channels_found]}

    def post(self):
        args = self.reqparse.parse_args()
        new_channel = {"name": args["name"], "description": args["description"],
                   "date": datetime.now()}
        MONGO.db.channels.insert_one(new_channel)
        _last_added = MONGO.db.channels.find().sort([("$natural", -1)]).limit(1)
        last_added = [channel for channel in _last_added]
        return {'channels': [marshal(channel, channel_fields)
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

        super(ChannelAPI, self).__init__()

    def get(self, id):
        channel = MONGO.db.channels.find_one_or_404({"_id": id})
        if len(channel) == 0:
            abort(404)
        return {"channel": marshal(channel, channel_fields)}

    def put(self, id):
        channel = MONGO.db.channels.find_one_or_404({"_id": id})
        if len(channel) == 0:
            abort(404)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                channel[k] = v
        return {'channel': marshal(channel, channel_fields)}


api = Api(app)

# add api resources
api.add_resource(ChannelListAPI, "/api/v1.0/channels", endpoint="channels")
api.add_resource(ChannelAPI, "/api/v1.0/channels/<int:id>", endpoint="<int:id>")

if __name__ == "__main__":
    app.run(debug=True)
