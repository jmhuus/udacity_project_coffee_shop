import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
- Uncomment the following line to initialize the datbase.
- This will drop all records and start the db from scratch.
'''
# db_drop_and_create_all()


# Flask Routes
@app.route("/drinks", methods=["GET"])
def get_drinks():
    """Returns a list of short drink details to any user.
    """
    
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route("/drinks-detail", methods=["GET"])
@requires_auth(permission="get:drinks-detail")
def get_drinks_detail():
    """Returns a list of long drink details to authorized users.
    """

    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def create_new_drink():
    """Adds a new drink for authorized users.
    """

    try:
        # Read request data
        data = json.loads(request.data)
        title = data["title"]
        recipe = json.dumps(data["recipe"])

        # Init new Drink obj
        new_drink = Drink()
        new_drink.title = title
        new_drink.recipe = recipe
        new_drink.insert()

    except Exception as e:
        abort(400)

    drink = [new_drink.long()]
    return jsonify({
        "success": True,
        "drinks": drink
    })


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth(permission="patch:drinks")
def update_drink(id):
    """Updates an existing drink's details for authorized users.
    """

    try:
        # Read request data
        data = json.loads(request.data)
        new_title = data["title"]
        new_recipe = json.dumps(data["recipe"])

        # Init new Drink obj
        drink = Drink.query.get(id)
        drink.title = new_title
        drink.recipe = new_recipe
        drink.update()

    except Exception as e: # Catch all
        abort(400)

    except AttributeError as ae: # Drink ID not found
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth(permission="delete:drinks")
def delete_drink(id):
    """Removes an existing drink for authorized users.
    """

    try:
        # Init new Drink obj
        drink = Drink.query.get(id)
        drink.delete()

    except Exception as e: # Catch all
        abort(400)

    except AttributeError as ae: # Drink ID not found
        abort(404)

    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "delete": id
    })


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    print("running unprocessable")
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }, 422)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }, 404)


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }, 400)


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }, 401)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }, 422)


@app.errorhandler(500)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "server error"
                    }, 500)


@app.errorhandler(AuthError)
def not_authorized(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }, error.status_code)
