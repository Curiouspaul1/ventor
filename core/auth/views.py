from flask import (
    current_app,  url_for, redirect, request,
    make_response
)
from core.extensions import (
    bcrypt, cors
)
import jwt
import datetime as d
from . import auth


@auth.route('/', methods=['POST'])
def login():
    db = current_app.config['DB']
    data = request.get_json(force=True)
    # find user by email or username
    user = db.search_by_value(
        "platform_db", "User",
        search_attribute="email",
        search_value=data['email'],
        get_attributes=['*']
    )[0]
    # if user is found compare hashses
    if bcrypt.check_password_hash(
        user['password'], data['password']
    ):
    # if hashes match generate tokens for the user
        access_token = jwt.encode(
            {
                "uid":user['user_id'],
                "exp":d.datetime.utcnow() + d.timedelta(minutes=60)
            },
            current_app.config['SECRET_KEY']
        )
        refresh_token = jwt.encode(
            {
                "uid":user['user_id'],
                "exp":d.datetime.utcnow() + d.timedelta(days=2)
            },
            current_app.config['SECRET_KEY']
        )
        resp = make_response(
            {
                "login":True
            }, 200
        )
        resp.set_cookie(
            'access_token',
            value=access_token,
            httponly=False,
            samesite='None',
            secure=False
        )
        resp.set_cookie(
            'refresh_token',
            value=refresh_token,
            httponly=False,
            samesite='None',
            secure=False
        )
        return resp
    else:
        return {
            "status": "error",
            "message": "Incorrect password"
        }, 401