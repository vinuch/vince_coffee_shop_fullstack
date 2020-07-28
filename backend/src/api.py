import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# '''
# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# '''
# db_drop_and_create_all()

## ROUTES
# '''
# @TODO implement endpoint
#     GET /drinks
#         it should be a public endpoint
#         it should contain only the drink.short() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks')
def get_drinks():
    drink_selection = Drink.query.all()
    all_drinks = [drink.short() for drink in drink_selection]

    if not all_drinks:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': all_drinks
    }), 200



# '''
# @TODO implement endpoint
#     GET /drinks-detail
#         it should require the 'get:drinks-detail' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drink_selection = Drink.query.all()
    all_drinks = [drink.long() for drink in drink_selection]

    if not all_drinks:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': all_drinks
    }), 200


# '''
# @TODO implement endpoint
#     POST /drinks
#         it should create a new row in the drinks table
#         it should require the 'post:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    res = request.get_json()
    new_title = res.get('title', None)
    new_recipe =json.dumps(res['recipe']) 
    

    drink = Drink(title=new_title, recipe=new_recipe)
    drink.insert()

    return jsonify({
        'success': True,
        'drinks': drink.long()
    }), 200
    


# '''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    res = request.get_json()
    updated_title = res.get('title', None)
    updated_recipe = res.get('recipe', None)

    selected_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not selected_drink:
        abort(404)
    try:
        if updated_title:
            selected_drink.title = updated_title
        if updated_recipe:
            selected_drink.recipe = json.dumps(res['recipe'])

        selected_drink.update()
        

        return jsonify({
            'success': True,
            'drinks': Drink.long(selected_drink)
        }), 200
    except:
        abort(422)

# '''
# @TODO implement endpoint
#     DELETE /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should delete the corresponding row for <id>
#         it should require the 'delete:drinks' permission
#     returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
#         or appropriate status code indicating reason for failure
# '''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    selected_drink = Drink.query.filter(Drink.id == id).one_or_none()
    print(selected_drink)
    
    if not selected_drink:
        abort(404)

    try:
        selected_drink.delete()
    
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except:
        abort(401)


## Error Handling
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
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Not Found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
