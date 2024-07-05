from flask import request
from utils.jwt import verify
from repositories.UserRepository import UserRepository
from repositories.SessionRepository import SessionRepository


class AuthMiddleware:

    def authenticate(self):
        auth_token = request.headers.get('Authorization', None)
        if auth_token is None:
            raise Exception("Unauthorized")
        token = auth_token.split(" ")[1]
        if token is None:
            raise Exception("Unauthorized")
        payload = verify(token)
        if payload["session"] is None:
            raise Exception("Unauthorized")
        try:
            session = SessionRepository.find_one_by_id(payload["session"]["id"])
        except IndexError:
            raise Exception("Session expired")

        if session["expired"] == True:
            raise Exception("Session expired")
        user = UserRepository.find_one_by_id(session["user_id"])

        #attach the user object to the request object
        request.user = user

        


def require_authentication():
    def decorator(func):
        def wrapper(*args, **kwargs):
            AuthMiddleware().authenticate()
            return func(*args, **kwargs)
        
        # had to do this cos flask would throw an assertion error if I don't rename it to the
        # function name cos basicaly the wrapper function name would repeat for every route 
        # I try to add the decorator on
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator