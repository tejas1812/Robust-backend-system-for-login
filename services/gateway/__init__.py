from flask import Flask,  request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import psycopg2
from flask_login import LoginManager
from flask_cors import CORS
#from flask_cors import CORS
import os 
import redis
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt, jwt_required, verify_jwt_in_request

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
host = os.getenv('DB_HOST', "postgres-db-postgresql")
port = os.getenv('DB_PORT', "5432")
user = os.getenv('DB_USER', "root")
passWd = os.getenv('DB_PASS', "Portal2023")
pqdb = os.getenv('DB_NAME', "driftnet_db")




redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redis_db = redis.StrictRedis(host=redisHost, port=redisPort, db=0) 


 
def create_app():
    global app
    app = Flask(__name__)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    # Session(app)
    CORS(app)
    url = f'postgresql://{user}:{passWd}@{host}:{port}/{pqdb}'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "your-secret-key")

    jwt = JWTManager()
    jwt.init_app(app)
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"
    app.config["JWT_TOKEN_LOCATION"]=["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    app.config['GATEWAY_URL'] =  os.getenv('GATEWAY_URL', "http://10.1.0.163:5000")
    app.config['PORTAL_URL'] =  os.getenv('PORTAL_URL', "https://portal:8080")

    app.config['SQLALCHEMY_DATABASE_URI'] = url
    db.init_app(app)
    try:
        conn = psycopg2.connect(
            database=pqdb, user=user, password=passWd, host=host, port=port)
    except Exception as e:
        print(e)
        exit(0) 

    cur = conn.cursor()
    try:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Users (id serial PRIMARY KEY, name varchar NOT NULL, email varchar NOT NULL UNIQUE, password varchar NOT NULL);")
        cur.execute(    
            "CREATE TABLE IF NOT EXISTS user_organization_roles (user_id INTEGER, organization_id INTEGER, role TEXT, PRIMARY KEY (user_id, organization_id));")
        cur.execute(    
            "CREATE TABLE IF NOT EXISTS organizations (id INTEGER PRIMARY KEY, name VARCHAR);")
        cur.execute(    
            "CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY, name VARCHAR(100) NOT NULL, salary INTEGER NOT NULL, designation VARCHAR(100) NOT NULL);")
        cur.execute(    
            "CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name VARCHAR(100) NOT NULL, course_name VARCHAR(100) NOT NULL, course_grade VARCHAR(100) NOT NULL);")
    
        # Database-seeding

        cur.execute(
            "INSERT INTO organizations (id, name) VALUES (1, 'Organization 1'), (2, 'Organization 2');")
        cur.execute(    
            "INSERT INTO user_organization_roles (user_id, organization_id, role) VALUES (6, 1, 'Admin'), (6, 2, 'Staff'), (5, 2, 'Admin'), (4, 2, 'Super-Admin'), (1, 1, 'Staff'),(2, 1, 'Staff');")
        cur.execute(    
            "INSERT INTO staff (id, name, salary, designation) VALUES (1, 'John Doe', 5000, 'Manager'),\
                (2, 'Jane Smith', 4000, 'Assistant Manager'), \
                (3, 'Michael Johnson', 3500, 'Supervisor'), \
                (4, 'Emily Wilson', 3000, 'Clerk'), \
                (5, 'David Brown', 2500, 'Receptionist'), \
                (6, 'Sarah Davis', 2000, 'BOSS');")
        cur.execute(    
            "INSERT INTO students (id, name, course_name, course_grade) VALUES \
                (1, 'Alex Johnson', 'Mathematics', 'A'), \
                (2, 'Emma Thompson', 'Science', 'B'), \
                (3, 'Oliver Wilson', 'English', 'C');")
    
    
    
    except Exception as e:
        print(e)
        exit(0) 

    conn.commit()  # <--- makes sure the change is shown in the database
    conn.close()
    cur.close()

    login_manager = LoginManager()
    login_manager.login_view = 'gateway.login'
    login_manager.init_app(app)

    #csrf = CSRFProtect(app)
    #csrf.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .gateway import gateway as gateway_blueprint
    app.register_blueprint(gateway_blueprint)

    return app