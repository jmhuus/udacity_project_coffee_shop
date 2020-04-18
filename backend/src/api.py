import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

import pdb

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
[COMPLETE] @TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def get_drinks():
    print()
    print()
    print("route GET /drinks")


    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        [COMPLETE] it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=["GET"])
@requires_auth(permission="get:drinks-detail")
def get_drinks_detail(payload):
    print()
    print()
    print("route GET /drinks-detail")

    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        [COMPLETE] it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        [COMPLETE] it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
def create_new_drink():
    print()
    print()
    print("running POST /drinks")

    # TODO(jordanhuus): require the 'post:drinks' permission

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


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        [COMPLETE] it should respond with a 404 error if <id> is not found
        [COMPLETE] it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        [COMPLETE] it should contain the drink.long() data representation
    [COMPLETE] returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["PATCH"])
def update_drink(id):
    print()
    print()
    print("route PATCH /drinks/<int:id>")

    # TODO(jordanhuus): require the 'patch:drinks' permission

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


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        [COMPLETE] it should respond with a 404 error if <id> is not found
        [COMPLETE] it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    [COMPLETE] returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["DELETE"])
def delete_drink(id):
    print()
    print()
    print("route DELETE /drinks/<int:id>")

    # TODO(jordanhuus): require the 'delete:drinks' permission

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
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    print("running unprocessable")
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }, 422)

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    print("running not_found")
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }, 404)


@app.errorhandler(400)
def not_found(error):
    print("running not_found")
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }, 400)


@app.errorhandler(401)
def unauthorized(error):
    print("running unauthorized")
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }, 401)


@app.errorhandler(422)
def unprocessable(error):
    print("running unprocessable")
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }, 422)


@app.errorhandler(500)
def not_found(error):
    print("running not_found")
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "server error"
                    }, 500)


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def not_authorized(error):
    print("running not_authorized")
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response




# Personal test route for inserting new rows manually
# TODO(jordanhuus): remove before pushing to prod
@app.route("/test", methods=["GET"])
def test_route():

    new_drink = Drink()
    new_drink.title = "test drink"
    new_drink.recipe = json.dumps([
        {
            "color": "light",
            "name": "light for the night",
            "parts": 9
        }
    ])
    new_drink.insert()

    return "None"
