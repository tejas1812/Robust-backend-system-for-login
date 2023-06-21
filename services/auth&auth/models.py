import sqlalchemy as db
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class OrganizationRole(Base):
    __tablename__ = 'user_organization_roles'

    user_id = db.Column(db.Integer, primary_key=True)

    organization_id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.String)

class Organization(Base):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class Staff(Base):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    designation = db.Column(db.String(100), nullable=False)


class Student(Base):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    course_grade = db.Column(db.String(100), nullable=False)


