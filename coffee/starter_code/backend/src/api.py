
import os
from turtle import title
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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def Get_AllDrinks():

    try:
        AllDrinks = Drink.query.all()

    except:
        abort(404)

    Drinks = [drink.short() for drink in AllDrinks]

    return jsonify({
        'success': True,
        'drinks': Drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def View_DrinksDetail():
    try:
        AllDrinks = Drink.query.order_by(Drink.id).all()

    except:
        abort(404)
    Drinks = [drink.long() for drink in AllDrinks]

    return jsonify({
        'success': True,
        'drinks': Drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def PostDrinks():
    Requests = request.get_json()
    val = Requests['recipe']
    titleval = Requests['title']
    Dumps = json.dumps(val)
    try:
        Adding = Drink(title=titleval, recipe=Dumps)
        Adding.insert()
        ADD = [Adding.long()]
    except:
        abort(422)
    return jsonify({
        'success': True,
        'drinks': ADD
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:idNum>', methods=['PATCH'])
@requires_auth('patch:drinks')
def PatchDrinks(drinks, idNum):
    ID = Drink.query.get(idNum)

    if not ID:
        abort(404)

    Requests = request.get_json()
    Title = Requests['title']
    Recipe = json.dumps(Requests['recipe'])
    try:
        if Title in Requests:
            drinks.title = Title

        if Recipe in Requests:
            drinks.recipe = Recipe

        drinks.update()
    except:
        abort(500)
    Longs = [drinks.long()]

    return jsonify({
        'success': True,
        'drinks': Longs
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:idNum>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete(drinks, idNum):
    ID = Drink.query.get(idNum)

    if not ID:
        abort(404)

    ID.delete()
    return jsonify({
        "success": True,
        "delete": drinks.id})


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


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
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def AuthErrors(Error):
    return jsonify({
        'success': False,
        'error': Error.status_code,
        'message': Error.error['description']
    }), Error.status_code
