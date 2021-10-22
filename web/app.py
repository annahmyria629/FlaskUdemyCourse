"""
User registration - free
Each user has 10 tokes
User can store a sentence in db for 1 token
User can retrieve a sentence from db for 1 token

+ Password hashing and storing
Resource    Address     Request     Params      StatusCode
----------------------------------------------------------
Register a  /register   POST        username    200 OK
user                                password
                                    (both strings)
----------------------------------------------------------
Store a     /store      POST        sentence    200 OK
sentence                            username    301 Out of tokens
                                    password    302 Invalid creds


----------------------------------------------------------
Retrieve a  /get        GET         username    200 OK
sentence                            password    301 Out of tokens
                                                302 Invalid creds
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import sys
import pathlib

sys.path.insert(1, str(pathlib.Path(__file__).parent.parent.resolve()))
from db.mongo_class import Mongo
from functools import wraps
import bcrypt


app = Flask(__name__)
api = Api(app)

client = Mongo()
db = client.create_database()
users = db['Users']


def input_json_validation_factory(check_sentence=False):
    def input_json_validation(fn):
        @wraps(fn)
        def wrapper(*args):
            try:
                assert 'username' in request.json and 'password' in request.json, \
                    'Input json must contains username and password'
                assert 'username' in request.json, 'Input json must contains username'
                assert 'password' in request.json, 'Input json must contains password'
                assert len(request.json['username']) > 0, 'Username can`t be empty'
                assert len(request.json['password']) > 0, 'Password can`t be empty'
                if check_sentence:
                    assert 'sentence' in request.json, 'Input json must contains sentence'
                return fn(*args)
            except Exception as e:
                return jsonify(
                    {
                        'Message': str(e),
                        'Status': 400
                    }
                )

        return wrapper
    return input_json_validation


class Register(Resource):

    @input_json_validation_factory(check_sentence=False)
    def post(self):
        try:
            username = request.json['username']
            password = request.json['password'].encode('UTF-8')
            # password hashing
            # hash(password + salt) = rtyujkhgfdserty
            # no rollback - if you know hash, you cant count pass
            # but if you know pass, you can know hash
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            if users.count_documents({"username": username}):
                for doc in users.find({"username": username}):
                    if bcrypt.checkpw(password, doc['password'].encode('UTF-8')):
                        return jsonify(
                            {
                                'Status': 300,
                                'Message': 'You have already been logged',
                                'Current tokens count': doc['tokens']
                            }
                        )
                else:
                    return jsonify(
                        {
                            'Status': 300,
                            'Message': 'User with such username has already exists. Select another username'
                        }
                    )
            users.insert_one({
                "username": username,
                "password": hashed_password,
                "tokens": 10,
                "sentences": []
            })
            return jsonify(
                {
                    'Status': 200,
                    'Message': 'You have successfully signed up to API'
                }
            )
        except Exception as e:
            return jsonify(
                {
                    'Message': str(e),
                    'Status': 400
                }
            )


class StoreSentence(Resource):

    @input_json_validation_factory(check_sentence=True)
    def post(self):
        try:
            username = request.json['username']
            password = request.json['password'].encode('UTF-8')
            sentence = request.json['sentence']
            if users.count_documents({"username": username}) == 1:
                doc = users.find({"username": username})[0]
                if bcrypt.checkpw(password, doc['password'].encode('UTF-8')):
                    if doc['tokens'] > 0:
                        users.update({"username": username}, {"$set": {"tokens": doc['tokens'] - 1},
                                                              "$push": {"sentences": sentence}})
                        return jsonify(
                            {
                                'Status': 200,
                                'Message': 'You successfully added a new sentence',
                                'Current tokens count': doc['tokens'] - 1,
                                'Sentences': users.find({"username": username})[0]['sentences']
                            }
                        )
                    else:
                        return jsonify(
                            {
                                'Status': 301,
                                'Message': 'You haven`t enough tokens',
                            }
                        )
                else:
                    return jsonify(
                        {
                            'Status': 300,
                            'Message': 'Invalid credentials'
                        }
                    )
            else:
                return jsonify(
                    {
                        'Status': 300,
                        'Message': 'No such user'
                    }
                )
        except Exception as e:
            return jsonify(
                {
                    'Message': str(e),
                    'Status': 400
                }
            )


class RetrieveSentence(Resource):

    @input_json_validation_factory(check_sentence=False)
    def get(self):
        try:
            username = request.json['username']
            password = request.json['password'].encode('UTF-8')
            if users.count_documents({"username": username}) == 1:
                doc = users.find({"username": username})[0]
                if bcrypt.checkpw(password, doc['password'].encode('UTF-8')):
                    if doc['tokens'] > 0:
                        users.update({"username": username}, {"$set": {"tokens": doc['tokens'] - 1}})
                        return jsonify(
                            {
                                'Status': 200,
                                'Message': 'Here are your statements',
                                'Current tokens count': doc['tokens'] - 1,
                                'Sentences': users.find({"username": username})[0]['sentences']
                            }
                        )
                    else:
                        return jsonify(
                            {
                                'Status': 301,
                                'Message': 'You haven`t enough tokens',
                            }
                        )
                else:
                    return jsonify(
                        {
                            'Status': 300,
                            'Message': 'Invalid credentials'
                        }
                    )
            else:
                return jsonify(
                    {
                        'Status': 300,
                        'Message': 'No such user'
                    }
                )
        except Exception as e:
            return jsonify(
                {
                    'Message': str(e),
                    'Status': 400
                }
            )


api.add_resource(Register, '/register')
api.add_resource(StoreSentence, '/add')
api.add_resource(RetrieveSentence, '/retrieve')

if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(host='127.0.0.1')
