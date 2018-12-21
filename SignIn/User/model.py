from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

from SignIn import db

class User(db.Model):
    __tablename__ = 'user'
    phonenum = db.Column(db.INTEGER, primary_key=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    nickname = db.Column(db.String(20), nullable=True)
    college = db.Column(db.String(20), nullable=True)
    major = db.Column(db.String(20), nullable=True)
    # assume sex = 1 -> man | 0 -> woman
    sex = db.Column(db.INTEGER, nullable=True)
    # must be one of {student, teacher}
    # student  can be null
    stuID = db.Column(db.String(20), nullable=True)
    srealname = db.Column(db.String(20), nullable=True)
    # teacher  can be null
    jobID = db.Column(db.String(20), nullable=True)
    trealname = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.phoneNum

    def __init__(self, phonenum, password, nickname, college, major, sex, stuID, srealname, jobID, trealname):
        self.phonenum = phonenum
        self.password = password
        self.nickname = nickname
        self.college = college
        self.major = major
        self.sex = sex
        self.stuID = stuID
        self.srealname = srealname
        self.jobID = jobID
        self.trealname = trealname

    def get(self, phonenum):
        return self.query.filter_by(phonenum=phonenum).first()

    def add(self, user):
        db.session.add(user)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, phonenum):
        self.query.filter_by(phonenum=phonenum).delete()
        return session_commit()

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason