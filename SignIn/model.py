from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
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

    def getall(self, classID):
        return self.query.filter(and_(JoinTable.classID == classID, JoinTable.stuID == User.stuID)).all()

    def add(self, user):
        db.session.add(user)
        return session_commit()

    # def update(self, user):
    #     db.session.update(user)
    #     return session_commit()

    def delete(self, phonenum):
        self.query.filter_by(phonenum=phonenum).delete()
        return session_commit()

    def out(self, user):
        return {
            'phonenum': user.phonenum,
            'password': user.password,
            'nickname': user.nickname,
            'college': user.college,
            'major': user.major,
            'sex': user.sex,
            'stuID': user.stuID,
            'srealname': user.srealname,
            'jobID': user.jobID,
            'trealname': user.trealname
        }


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

    def getall(self):
        return self.query.all()

    def stugetclass(self, stuID):
        return self.query.filter(and_(Class.classID == JoinTable.classID, JoinTable.stuID == stuID)).all()

    def teagetclass(self, jobID):
        return self.query.filter(and_(Class.classID == TeachTable.classID, TeachTable.jobID == jobID)).all()

    def add(self, cls):
        db.session.add(cls)
        return session_commit()

    # def update(self, cls):
    #     db.session.update(cls)
    #     return session_commit()

    def delete(self, classID):
        self.query.filter_by(classID=classID).delete()
        return session_commit()

    def out(self, clas):
        return {
            'classID': clas.classID,
            'classname': clas.classname
        }


class JoinTable(db.Model):
    __tablename__ = 'jointable'
    jid = db.Column(db.INTEGER, primary_key=True, nullable=False)
    classID = db.Column(db.String(20), primary_key=True, nullable=False)
    stuID = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<%r : %r join %r>' % self.jid, self.stuID, self.classID

    def __init__(self, jid, classID, stuID):
        self.jid = jid
        self.classID = classID
        self.stuID = stuID

    def get(self, classID, stuID):
        return self.query.filter(and_(JoinTable.classID == classID, JoinTable.stuID == stuID)).first()

    def getid(self):
        return len(self.query.all())

    def add(self, cls):
        db.session.add(cls)
        return session_commit()

    # def update(self, cls):
    #     db.session.update(cls)
    #     return session_commit()

    def delete(self, classID, stuID):
        self.query.filter(and_(JoinTable.classID == classID, JoinTable.stuID == stuID)).delete()
        return session_commit()

class TeachTable(db.Model):
    __tablename__ = 'teachtable'
    tid = db.Column(db.INTEGER, primary_key=True, nullable=False)
    classID = db.Column(db.String(20), nullable=False)
    jobID = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<%r : %r teach %r>' % self.tid, self.jobID, self.classID

    def __init__(self, tid, classID, jobID):
        self.tid = tid
        self.classID = classID
        self.jobID = jobID

    def get(self, classID, jobID):
        return self.query.filter(and_(TeachTable.classID == classID, TeachTable.jobID == jobID)).first()

    def getid(self):
        return len(self.query.all())

    def add(self, cls):
        db.session.add(cls)
        return session_commit()

    # def update(self, cls):
    #     db.session.update(cls)
    #     return session_commit()

    def delete(self, classID, jobID):
        self.query.filter(and_(TeachTable.classID == classID, TeachTable.jobID == jobID)).delete()
        return session_commit()

class Attendtable(db.Model):
    __tablename__ = 'attendtable'
    aid = db.Column(db.INTEGER, primary_key=True, nullable=False)
    classID = db.Column(db.String(20), nullable=False)
    stuID = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    result = db.Column(db.INTEGER, nullable=True, default=0)

    def __repr__(self):
        return '<%r : %r signin %r>' % self.aid, self.stuID, self.classID

    def __init__(self, aid, classID, stuID, time, result):
        self.aid = aid
        self.classID = classID
        self.stuID = stuID
        self.time = time
        self.result = result

    def getall(self, classID):
        return self.query.filter_by(classID=classID).all()

    def get(self, classID, stuID):
        return self.query.filter(and_(Attendtable.classID == classID, Attendtable.stuID == stuID)).all()

    def getid(self):
        return len(self.query.all())

    def add(self, att):
        db.session.add(att)
        return session_commit()

    def update(self, classID, stuID):
        att = self.query.filter(and_(Attendtable.classID == classID, Attendtable.stuID == stuID)).last()
        att.result = 1
        return session_commit()

    def out(self, att):
        return {
            'aid': att.aid,
            'classID': att.classID,
            'stuID': att.stuID,
            'time': att.time,
            'result': att.result
        }

class Message(db.Model):
    __tablename__ = 'message'
    mid = db.Column(db.INTEGER, primary_key=True, nullable=False)
    classID = db.Column(db.String(20), nullable=False)
    stuID = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    sender = db.Column(db.INTEGER, nullable=False)
    isleave = db.Column(db.INTEGER, nullable=False, default=0)

    def __repr__(self):
        return '<%r : %r message %r>' % self.mid, self.stuID, self.classID

    def __init__(self, mid, classID, stuID, time, content, sender, isleave):
        self.mid = mid
        self.classID = classID
        self.stuID = stuID
        self.time = time
        self.content = content
        self.sender = sender
        self.isleave = isleave

    def getall(self, classID):
        return self.query.filter_by(classID=classID).all()

    def get(self, classID, stuID):
        return self.query.filter(and_(Message.classID == classID, Message.stuID == stuID)).all()

    def getid(self):
        return len(self.query.all())

    def add(self, mess):
        db.session.add(mess)
        return session_commit()

    def out(self, mess):
        return {
            'mid': mess.mid,
            'classID': mess.classID,
            'stuID': mess.stuID,
            'time': mess.time,
            'content': mess.content,
            'sender': mess.sender,
            'isleave': mess.isleave
        }

class Bulletin(db.Model):
    __tablename__ = 'bulletin'
    bid = db.Column(db.INTEGER, primary_key=True, nullable=False)
    classID = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<%r : %r bulletin >' % self.bid, self.classID

    def __init__(self, bid, classID, time, content):
        self.bid = bid
        self.classID = classID
        self.time = time
        self.content = content

    def getall(self, classID):
        return self.query.filter_by(classID=classID).all()

    def getid(self):
        return len(self.query.all())

    def add(self, mess):
        db.session.add(mess)
        return session_commit()

    def out(self, mess):
        return {
            'bid': mess.bid,
            'classID': mess.classID,
            'time': mess.time,
            'content': mess.content
        }

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason