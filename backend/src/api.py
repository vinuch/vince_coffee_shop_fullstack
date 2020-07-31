import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)
setup_db(app)
CORS(app)
# '''
# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# '''
db_drop_and_create_all()


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



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drink_selection = Drink.query.all()
        all_drinks = [drink.long() for drink in drink_selection]

    
        return jsonify({
            'success': True,
            'drinks': all_drinks
        }), 200
    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    res = request.get_json()
    if res is None: 
        abort(401)

    if not (res['title'] or res['recipe']):
        abort(400)
    if Drink.query.filter_by(title=res['title']).first():
        abort(400)

    new_title = res['title']
    if isinstance(res['recipe'], str) :
        new_recipe = res['recipe']
    else:
        new_recipe =  '[' + json.dumps(res['recipe']) + ']'
    
    try:
        Drink(title=new_title, recipe=new_recipe).insert()
        
        drink = Drink.query.filter_by(
            title=res['title']).first()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except:
        abort(401)

    
    

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    res = request.get_json()
    
    if not res:
        abort(401)
    updated_title = res.get('title', None)
    updated_recipe = res.get('recipe', None)

    selected_drink = Drink.query.get(drink_id)
    if selected_drink:
    
        if updated_title:
            selected_drink.title = updated_title
        if updated_recipe:
            selected_drink.recipe =  json.dumps(res['recipe'])
        selected_drink.update()
        return jsonify({
            'success': True,
            'drinks': [Drink.long(selected_drink)]
        }), 200

    




@app.route('/drinks/<int:drink_id>',  methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    """Deletes 1 drink with given id"""
    try:
        if 'delete:drinks' in payload['permissions']:
            drink_to_delete = Drink.query.get(drink_id)
            drink_to_delete.delete()

            return jsonify({
                'success': True,
                'delete': drink_id
            })

        else:
            return abort(401)
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



@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code