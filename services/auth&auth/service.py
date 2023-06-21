from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, get_jwt_identity, get_jwt,
    set_access_cookies, get_jwt_header,
    set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.security import check_password_hash
import redis
from redis.sentinel import Sentinel
from models import User
import os

from session import session

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with your secret key

jwt = JWTManager(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

redisHost = os.getenv("REDIS_HOST") or "cache-redis"
redisReadPort = os.getenv("REDIS_PORT") or 6379
redisWritePort = os.getenv("REDIS_WRITE_PORT") or 26379

redis_store = redis.StrictRedis(host=redisHost, port=redisReadPort, db=0)
sentinel = Sentinel([(redisHost, 26379)], socket_timeout=0.1)
master= sentinel.discover_master('mymaster')



redis_write_store = redis.StrictRedis(host=master[0], port=master[1], db=0)




@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = session.query(User).filter_by(email=email).first()
    # Check if user exists and password matches
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        return jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }), 200

    else:
        return jsonify({'success': False}), 401

@app.route('/check_jwt_integrity', methods=['POST'])
@jwt_required()
def check_jwt_integrity():

    current_user = get_jwt_identity()
    if check_token_blacklist(get_jwt_header(), get_jwt()) or not current_user :
        return jsonify({'success': False}), 401
    else :
        return jsonify({'success': True, 'user': current_user}), 200


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    redis_write_store.setex(get_jwt()['jti'], app.config['JWT_ACCESS_TOKEN_EXPIRES'], 'true')
    return jsonify(ret), 200

@app.route('/logout', methods=['DELETE'])
@jwt_required(refresh=True)
def logout():
    jti = get_jwt()['jti']
    redis_write_store.setex(jti, app.config['JWT_REFRESH_TOKEN_EXPIRES'], 'true')
    return jsonify({'success': True}), 200

@jwt.token_in_blocklist_loader
def check_token_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    entry = redis_store.get(jti)
    return entry is not None

if __name__ == '__main__':
    app.run()