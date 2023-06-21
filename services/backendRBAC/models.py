import sqlalchemy as db
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import Select

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'password' }

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns if c.name != 'password' ]

    def get_column_names(self) :
        return self.__table__.columns.keys()
    

class OrganizationRole(Base):
    __tablename__ = 'user_organization_roles'

    user_id = db.Column(db.Integer, primary_key=True)

    organization_id = db.Column(db.Integer, primary_key=True)

    role = db.Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]

    def get_column_names(self) :
        return self.__table__.columns.keys()

class Organization(Base):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns }
    
    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns ]
    
    def get_column_names(self) :
        return self.__table__.columns.keys()

class Staff(Base):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    designation = db.Column(db.String(100), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns }
    
    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns ]

    def get_column_names(self) :
        return self.__table__.columns.keys()


class Student(Base):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    course_grade = db.Column(db.String(100), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns }
    
    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns ]
    
    def get_column_names(self) :
        return self.__table__.columns.keys()

