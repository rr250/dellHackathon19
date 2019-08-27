import bcrypt
import requests
import jwt
from flask_cors import CORS
from flask import Flask, jsonify, abort, request
from pymongo import MongoClient
from bson import ObjectId, json_util
from datetime import datetime, timedelta

from Constants import MONGODB_URL, DB_NAME
from Model import getPredictions
from History import getChromeHistory


# Connect to the database
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route("/", methods=["GET"])
def home():
    return jsonify('Improved Recommendation RESTful API for DELL Hackathon')

# Register the user
@app.route("/register", methods=["POST"])
def register():
    # print(request.json)
    if not request.json or 'email' not in request.json.keys() or 'password' not in request.json.keys() or 'email' not in request.json.keys():
        return jsonify("Incorrect form submission"), 400
    if db['users'].find_one({'email': request.json['email']}) is not None:
        return jsonify({'success': False, 'status': 'Email Already Exists'}), 400
    if db['users'].find_one({'username': request.json['username']}) is not None:
        return jsonify({'success': False, 'status': 'Username Already Exists'}), 400

    hashed = bcrypt.hashpw(
        request.json['password'].encode('utf-8'), bcrypt.gensalt())

    # get latest user ID
    latestId = db['users'].find_one({}, sort=[("userId", -1)])['userId']
    names = request.json['name'].split(" ")
    first = names[0].capitalize()
    last = names[0].capitalize()
    # print(latestId)
    # insert

    user = db['users'].insert_one(
        {
            'email': request.json['email'],
            'username': names[0].lower()+"_"+names[-1].lower(),
            'password': hashed.decode('utf-8'),
            'firstName': first,
            'lastName': last,
            'userId': latestId+1,
            'createdOn': int(datetime.timestamp(datetime.now()) * 1000),
            'updatedOn': None,
            'orders': []
        })
    token = jwt.encode({'uid': str(user.inserted_id), 'exp': datetime.utcnow(
        ) + timedelta(days=30)}, 'qwr48fv4df25gbt45vqer5544vre44d4v5e55vqer')
    return jsonify({'success': True, '_id': str(user.inserted_id), 'token': token, "email": request.json['email'], "name": first}), 200


# Hash the password and compare. return jwt
@app.route("/signin", methods=["POST"])
def login():
    if not request.json or 'email' not in request.json.keys() or 'password' not in request.json.keys():
        return jsonify("Incorrect form submission"), 400
    user = db['users'].find_one({'email': request.json['email']})
    if user is None:
        return jsonify("Unauthorized"), 401
    if bcrypt.checkpw(request.json['password'].encode('utf-8'), user['password'].encode('utf-8')):
        # print(str(user['_id']))
        token = jwt.encode({'uid': str(user['_id']), 'exp': datetime.utcnow(
        ) + timedelta(days=30)}, 'qwr48fv4df25gbt45vqer5544vre44d4v5e55vqer')
        db['users'].update_one({"email": request.json['email']}, {
              "$set": {"isAuthenticated": True}})
        return jsonify({'_id': str(user['_id']), 'name': user['firstName'] + " " + user['lastName'], 'token': token.decode('utf-8'), "email": user["email"]}), 200
    return jsonify("Unauthorized"), 401

# Get inventory
@app.route("/items", methods=["GET"])
def get_items():
    items = db['items'].find({})
    if items is None:
        return jsonify("No items found in db"), 500
    return jsonify([i for i in items]), 200

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    try:
        item = db['items'].find_one({"itemId": item_id})
    except KeyError as err:
        return jsonify(err), 400
    except Exception as err:
        return jsonify(err), err.code
    else:
        print(item)
        return jsonify({k:v for k,v in item.items() if k != "_id"}), 200
# Place an order for the user
@app.route("/order", methods=['POST'])
def placeOrders():
    """This function executes when user clicks on the order items button. It takes data from url and updates the database."""
    data = request.json  # address,pincode,item,seller
    try:
        token = request.headers['Authorization']
    except KeyError:
        abort(401)
    # print(token)
    payload = jwt.decode(token, 'qwr48fv4df25gbt45vqer5544vre44d4v5e55vqer')
    # print(payload)
    userId, itemId = payload['uid'], data['item']

    # get item price
    try:
        itemAmount = db['items'].find_one({"itemId": itemId})['price']
    except KeyError:
        return jsonify("incorrect itemId"), 400

    # get latest orderId
    latestId = db['orders'].find_one({}, sort=[("orderId", -1)])['orderId']

    # create new order
    yes = db['orders'].insert_one({
        "orderId": latestId+1,
        "item": itemId,
        "userId": userId,
        "amount": itemAmount,
        "address": request.json['address'],
        "isCompleted": False,
        "createdOn": int(datetime.timestamp(datetime.now()) * 1000)
    })
    # print(yes.inserted_id)

    # update users document
    userOrders = db['users'].find_one({"_id": ObjectId(userId)})['orders']
    # print(userOrders)
    userOrders.append(itemId)
    # print(userOrders)
    db['users'].update_one({"_id": ObjectId(userId)}, {
                           "$set": {"orders": userOrders}})

    return jsonify({"orderId": str(yes.inserted_id)}), 200

@app.route("/user/orderHistory/", methods=["GET"])
def orderHistory():
    try:
        token = request.headers['Authorization']
    except KeyError:
        abort(401)
    # print(token)
    payload = jwt.decode(token, 'qwr48fv4df25gbt45vqer5544vre44d4v5e55vqer')
    print(payload)
    userId = payload['uid']

    try:
        userOrderList = db['users'].find_one({"_id": ObjectId(userId)})['orders']
    except KeyError as e:
        return 500
    except Exception as e:
        print(e)
    else:
        if not userOrderList:
            hasOrderedBefore = False
            orders = []
        else:
            hasOrderedBefore = True
            collection = db['items'].find({"itemId":{"$in": userOrderList}})
            orders = [{k:v for k,v in document.items() if k != "_id"} for document in collection]
        print(hasOrderedBefore, orders)
        return jsonify({"success":True, "hasOrdered":hasOrderedBefore, "orders": orders}), 200

@app.route("/history/", methods=["GET"])
def getBrowserHistory():
    result = getChromeHistory()
    return jsonify({"status":"yes", "endpoint":"history"}), 200

@app.route("/predict/", methods=["POST"])
def predict():
    # get OrderHistory if user is loggedIn otherwise don't
    data = request.json
    if data['isLoggedIn']:
        try:
            token = request.headers['Authorization']
        except KeyError:
            abort(401)
        else:
            payload = jwt.decode(token, 'qwr48fv4df25gbt45vqer5544vre44d4v5e55vqer')
        # print(payload)
            userId = payload['uid']
            print(userId)
            # get order history of user
            pastOrders = requests.get(url="http://localhost:5000/user/orderHistory/", headers=request.headers)
            # get browser history of session
            browsingHistory = requests.get(url="http://localhost:5000/history/")
            print("Orders",pastOrders.text)
            print("Browsing history",browsingHistory.text)
            modelOutput = getPredictions(orderHistory, getBrowserHistory)
            return jsonify(modelOutput),200



    result = predict()

        
if(__name__ == '__main__'):
    app.run(debug=True)
