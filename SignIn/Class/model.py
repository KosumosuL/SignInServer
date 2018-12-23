from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

from SignIn import db

class Class(db.Model):
    __tablename__ = 'class'
    classID = db.Column(db.String(20), primary_key=True, nullable=False)
    classname = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Class %r>' % self.classID

    def __init__(self, classID, classname):
        self.classID = classID
        self.classname = classname

    def get(self, classID):
        return self.query.filter_by(classID=classID).first()

    def add(self, cls):
        db.session.add(cls)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, classID):
        self.query.filter_by(classID=classID).delete()
        return session_commit()


class JoinTable(db.Model):
    __tablename__ = 'jointable'
    classID = db.Column(db.String(20), nullable=False)
    stuID = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<%r join %r>' % self.stuID, self.classID

    def __init__(self, classID, classname):
        self.classID = classID
        self.classname = classname

    def get(self, classID):
        return self.query.filter_by(classID=classID).first()

    def add(self, cls):
        db.session.add(cls)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, classID):
        self.query.filter_by(classID=classID).delete()
        return session_commit()

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason