import json
from flask import Flask, request, jsonify, redirect, Blueprint, url_for, flash
from authlib.integrations.flask_client import OAuth
import requests
import os
from flask import render_template
import redis
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt, jwt_required, verify_jwt_in_request


gateway = Blueprint('gateway', __name__)

auth_service_url = os.getenv('AUTH_URL', "http://10.1.1.74:5000")
backend_url = os.getenv('BACKEND_URL', "http://10.1.1.55:5000")


@gateway.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Make a request to the authentication and authorization microservice
        response = requests.post(f'{auth_service_url}/login', json={'email': email, 'password': password})

        if response.status_code != 500:
            data = response.json()
            if data['success']:
                # Authentication successful, redirect back to the API Gateway with the JWT cookie
                # Set the JWT cookie as an HTTP-only cookie
                response = redirect('/')
                response.set_cookie('access_token', data['access_token'], httponly=True)
                response.set_cookie('refresh_token', data['refresh_token'], httponly=True)
                return response
            
            else:
                # Authentication failed, handle the error or redirect to the login form
                flash('Please check your login details and try again.')
                return redirect(url_for('gateway.login'))
        else:
            # Handle other status codes or errors
            return jsonify({'error': 'An error occurred'}), 500
    else :

        return render_template("login.html")
    
@gateway.route('/')
def home():
    jwt_cookie = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    # Proxy code to handle requests with JWT cookie
    if jwt_cookie:

        headers = {'Authorization': f'Bearer {jwt_cookie}'}
        response = requests.post(f'{auth_service_url}/check_jwt_integrity', headers=headers)

        if response.status_code == 200:
            return redirect('/portal')

        else:
            headers = {'Authorization': f'Bearer {refresh_token}'}
            response = requests.post(f'{auth_service_url}/refresh', headers=headers)
            if response.status_code == 200:
                response = redirect('/portal')
                response.set_cookie('access_token', response.json()['access_token'], httponly=True)
                return response
            else :
                return redirect('/login')

    return redirect('/login')

@gateway.route('/portal', methods=['GET', 'POST'])
@jwt_required()
def portal():

    access_token = request.cookies.get('access_token')
    if request.method == 'POST':
        org_id = request.form.get('org_id')
        callback = request.form.get('callback')
        callback_route = callback.replace(" ", "_")
        # Make a POST request to the backend API service to fetch the permissions for the organization
        callback_url = f"{backend_url}/{callback_route}"
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {'organization_id': org_id}
        response = requests.post(callback_url, headers=headers, json=data )

        if response.status_code == 200:
            result = response.json()

            # Render the query_result.html template with the result data
            return render_template('query-result.html', data=result, identity=get_jwt_identity())
        else:
            # Handle the error case
            return render_template('error.html', message='Failed to fetch permissions data')

    else :

        # Make a POST request to the backend API service to populate the portal data
        populate_portal_url = f'{backend_url}/populate_portal'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.post(populate_portal_url, headers=headers)

        if response.status_code == 200:
            #Parse the JSON response into a Python object
            portal_data = json.loads(response.text)["data"]
            
            # Process the portal data and extract the organization details
            organizations = []
            for org_data in portal_data:
                org_id = org_data['org_id']
                org_name = org_data['org_name']
                role = org_data['role']
                callbacks = org_data['callbacks']
                
                # Add the organization details to the list
                organizations.append({'org_id': org_id, 'org_name': org_name, 'role': role, 'callbacks': callbacks})
            

            # Render the portal.html template and pass the portal data to it
            return render_template('portal.html', organizations=organizations, identity=get_jwt_identity())

        else:
            # Handle the error case
            return render_template('error.html', message=json.loads(response.text)['error'])


@gateway.route('/signup')
def signup():
    return render_template('signup.html')


@gateway.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('email exists', 'danger')
        return redirect("/")

    new_user = User(email=email, name=name,
                     password=generate_password_hash(password, method='sha256'))
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        print("failed")

    return redirect(url_for('gateway.login'))


@gateway.route('/logout', methods=['POST'])
@jwt_required(locations=["cookies"], refresh=True)
def logout():
    jwt_cookie = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token')

    headers = {'Authorization': f'Bearer {refresh_token}'}
    # Delete the tokens  and put them in the blocklist
    response = requests.delete(f'{auth_service_url}/logout', headers=headers)

    if response.status_code == 200:
        response = redirect('/')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    
    else :
        return render_template('error.html', message="Failed to logout")
