import sys
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt, jwt_required, verify_jwt_in_request

from session import session
from models import User, Organization, OrganizationRole, Staff, Student

import redis
import pickle
from redis.sentinel import Sentinel

import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key' 

jwt = JWTManager()
jwt.init_app(app)


redisHost = os.getenv("REDIS_HOST") or "cache-redis"
redisReadPort = os.getenv("REDIS_READ_PORT") or 6379
redisWritePort = os.getenv("REDIS_WRITE_PORT") or 26379

redis_store = redis.StrictRedis(host=redisHost, port=redisReadPort, db=0)
sentinel = Sentinel([(redisHost, 26379)], socket_timeout=0.1)
master= sentinel.discover_master('mymaster')



redis_write_store = redis.StrictRedis(host=master[0], port=master[1], db=0)

# ...
# Callbacks for different roles
callbacks = {
    'Super-Admin': ['get_users', 'manage_permissions'],
    'Admin': ['get_staff', 'update_staff'],
    'Staff': ['get_students', 'update_student_grades'],
}

"""
# Add the callbacks to the Redis cache for future use
if callbacks_list:
    redis_client.sadd(role_key, *callbacks_list)
"""

def get_user_id(email):

    # Retrieve the user ID from the models.py based on the email
    user = session.query(User).filter_by(email=email).first()
    if user:
        return user.id

    return None

# Helper function to retrieve the user's role for the organization
def get_user_role(user_id, org_id):
    # Check if the role exists in the Redis cache
    role_key = f'role:{user_id}:{org_id}'
    if redis_store.exists(role_key):
        role = redis_store.get(role_key).decode('utf-8')
    else:
        # Retrieve the role from the OrganizationRole table using SQLAlchemy
        organization_role = session.query(OrganizationRole).filter_by(user_id=int(user_id), organization_id=int(org_id)).first()
        role = organization_role.role if organization_role else None

        # If the role exists, add it to the Redis cache
        if role:
            redis_write_store.set(role_key, role)

    return role


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Retrieve the current user's ID from the session or token
            user_id = get_user_id(get_jwt_identity())

            # Retrieve the user's role for the organization
            org_id = request.json.get('organization_id')
            user_role = get_user_role(user_id, org_id)

            # Check if the user has the required role
            if user_role and user_role == role:
                return f(*args, **kwargs)
            else:
                # User does not have the required role, abort with 403 Forbidden
                abort(403)

        return decorated_function
    return decorator


@app.route('/get_staff', methods=['POST'])
@jwt_required()
@role_required('Admin')
def get_staff():
    staff = session.query(Staff).all()
    # Process staff data and return response

    if staff :
        return jsonify([])

    # Convert the staff members to a list of records
    staff_list = [staff[0].get_column_names()]+[member.as_list() for member in staff]

    # Return the staff members as JSON
    return jsonify(staff_list)


@app.route('/get_students', methods=['POST'])
@jwt_required()
@role_required('Staff')
def get_students():
    students = session.query(Student).all()
    # Process students data and return response
    
    if not students :
        return jsonify([])
    
    # Convert the students to a list of records
    students_list = [students[0].get_column_names()]+[student.as_list() for student in students]

    # Return the students as JSON
    return jsonify(students_list)

@app.route('/get_users', methods=['POST'])
@jwt_required()
@role_required('Super-Admin')
def get_users():
    users = session.query(User).all()
    # Process users data and return response
    
    if not users :
        return jsonify([])

    # Convert the users to a list of records
    users_list = [[col for col in users[0].get_column_names() if col !="password"]]+[user.as_list() for user in users]
    #users_list = [user.as_list() for user in users]

    # Return the users as JSON
    return jsonify(users_list)


@app.route('/permissions', methods=['POST'])
@jwt_required()
@role_required('Super-Admin')
def manage_permissions():
    # Update permissions
    data = request.json
    # Process and update permissions
    # ...

    return jsonify({'message': 'Permissions updated successfully'})

@app.route('/staff', methods=['POST'])
@jwt_required()
@role_required('Admin')
def update_staff(staff_id):
    staff_id = request.json.get('staff_id')
    staff = session.query(Staff).get(staff_id)
    if not staff:
        abort(404)

    # Update staff member information
    data = request.json
    staff.update({
        'name': data['name'],
        'salary' : data['salary'],
        'designation' : data['designation']
    })
    session.commit()

    # Return success message
    return jsonify({'message': 'Staff member updated successfully'})


@app.route('/students', methods=['POST'])
@jwt_required()
@role_required('Staff')
def update_student_grades(student_id):
    student_id = request.json.get('student_id')
    student = session.query(Student).get(student_id)
    if not student:
        abort(404)

    # Update student grade
    data = request.json
    student.update({
        'name': data['name'],
        'course_name' : data['course_name'],
        'course_grade' : data['course_grade']
    })

    session.commit()

    # Return success message
    return jsonify({'message': 'Student grade updated successfully'})

@app.route('/populate_portal', methods=['POST'])
def populate_portal():
    try :
        # Get the user_id from the decoded JWT cookie
        if verify_jwt_in_request() :
            user_id = get_user_id(get_jwt_identity())

        # Check if the organizations are cached in Redis
        orgs_key = f"orgs:{user_id}"

        # get org ids from redis and convert it into Integer
        orgs = redis_store.smembers(orgs_key)
        orgs = [int(org) for org in orgs]
        
        if not orgs:

            # Fetch the organizations from the database
            organizations = session.query(OrganizationRole).filter_by(user_id=user_id).all()
            orgs = [int(org.organization_id) for org in organizations]
            #print('Hello world!', type(orgs), type(orgs[0]), file=sys.stderr)

            # Store the organizations in Redis for future access
            redis_write_store.sadd(orgs_key, *orgs)

        # Retrieve the organization names from the database
        org_names = session.query(Organization).filter(Organization.id.in_(orgs)).all()
        org_names = {org.id: org.name for org in org_names}

        # Create a dictionary mapping organization names to user roles
        portal_data = []
        for org_id in orgs:
            org_name = org_names.get(org_id)
            role = get_user_role(user_id, org_id)
            callbacks_list = callbacks.get(role, [])
            
            # Create a dictionary with the organization details and append it to the portal data list
            org_data = {
                'org_id': org_id,
                'org_name': org_name,
                'role': role,
                'callbacks': callbacks_list
            }
            portal_data.append(org_data)
        
        # Return the portal data as JSON
        return jsonify({"data" : portal_data})
    
    except Exception as e:
        # Return a 403 status code and an error message
        return jsonify({'error': str(e) }), 403



    

if __name__ == '__main__':
    app.run()