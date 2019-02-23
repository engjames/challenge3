from functools import wraps
from flask import request, make_response, jsonify, flash
from app.models.user_model import User
from app import conn
import jwt


#create a cursor object for executing our sql statements
cur = conn.cursor()
def token_required(f):
    """
    Decorator function to ensure that a resource is access by only authenticated users`
    provided their auth tokens are valid
    :param f:
    :return:
    """
    #wraps is a together function. it will join our token_required metthod with our endpoint methods
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #lets intialize our token to None 
        token = None

        #check if a key of auth_token exists in the request made by the user
        if 'auth_token' in request.headers:
            #if the key exist, lets get its value and assign it to a variable token 
            token = request.headers['auth_token']
        
        #if our token is still none at this point, it means the user didnt provide it
        if not token:
            return make_response(jsonify({
                'status': 'failed',
                'message': 'Token is missing'
            })), 401

        #let's try to decode our token so that we can use the data encrypted in it
        try:
            #check for a method called decode_auth_token in the User Model. it the one the decrypts our token
            decode_response = User.decode_auth_token(token)
           
           #decode reponse contains the users id, lets use it to get the users email
            sql1 = """
                SELECT email FROM users WHERE user_id=%s
            """
            cur.execute(sql1,(decode_response,))
            user = cur.fetchone()
            #users email is now stored as the current user
            current_user = user[0]

        #if something goes wrong during the decrypting process, lets return the error   
        except:
            message = "Invalid token"
            decode_response = User.decode_auth_token(token)
            if isinstance(decode_response, str):
                message = decode_response
            return make_response(jsonify({
                'status': 'failed',
                'message': message
            })), 401
        #lets return the current user , all with all the predifined arguments of the method 
        return f(current_user,*args, **kwargs)

    return decorated_function

#The following are helper functions that will be used in all our views files

def response(status, message, status_code):
    """
    Helper method to make an Http response
    :param status: Status
    :param message: Message
    :param status_code: Http status code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), status_code


def response_auth(user_object, token, status_code):
    """
    Make a Http response to send the auth token
    :param status: Status
    :param message: Message
    :param token: Authorization Token
    :param status_code: Http status code
    :return: Http Json response
    """
    return make_response(jsonify({
        'status': status_code,
        'data': [{"token":token, "user": user_object}]
    })), status_code

def response_for_user_incidents(status, category, status_code):
    """
    Http response for response with an incident
    :param status: Status Message
    :param category: category
    :param status_code: Http Status Code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'category': category
    })), status_code

def response_for_user_incidents(status, incidents, status_code):
    """
    Http response for response with users incidents.
    :param status: Status Message
    :param status_code: Http Status Code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'incidents': incidents
    })), status_code

