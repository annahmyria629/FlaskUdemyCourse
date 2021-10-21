from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)
mongoClient = MongoClient('mongodb://db:27017')
db = mongoClient.aNewDB
UserNum = db['UserNum']
UserNum.insert_one({
    'num_of_users': 0
})


class Add(Resource):
    def post(self):
        try:
            assert 'x' in request.json, 'Input json must contains x value'
            assert 'y' in request.json, 'Input json must contains y value'
            return jsonify(
                {
                    'Message': int(request.json['x']) + int(request.json['y']),
                    'Status': 200
                 }
            )
        except Exception as e:
            return jsonify(
                {
                    'Message': str(e),
                    'Status': 400
                 }
            )


class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        UserNum.update({'num_of_users': prev_num}, {"$set": {'num_of_users': prev_num + 1}})
        return jsonify(
                {
                    'Message': str(prev_num + 1),
                    'Status': 200
                 }
            )



class Subtract(Resource):
    pass


class Multiply(Resource):
    pass


class Divide(Resource):
    pass


api.add_resource(Add, '/add')
api.add_resource(Visit, '/visit')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
