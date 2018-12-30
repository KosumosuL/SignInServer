from flask import jsonify, request
from flask_jwt import JWT, jwt_required, current_identity, JWTError
from SignIn.model import *
from werkzeug.security import safe_str_cmp
from collections import OrderedDict
from datetime import datetime
from voluptuous import Schema, Any, MultipleInvalid, And, Length, All, Range


def init_api(app):

    CLASS_SIGNIN_STATUS = dict()

    # Define Schema
    schema = Schema({
        "phonenum": All(str, Length(min=11, max=11)),
        "password": All(str, Length(min=8, max=20)),
        "nickname": Any(str),
        "college": Any(str),
        "major": Any(str),
        "sex": All(str, Length(min=1, max=1)),
        "ID": All(str, Length(min=10, max=12)),
        "realname": Any(str),
        "ident": Any(str),
        "classID": All(str, Length(min=5, max=7)),
        "classname": Any(str),
        "time": Any(str),
        "content": Any(str),
        "location": Any(str),
        "isleave": All(str, Length(min=1, max=1))
    })


    # for auth
    # @jwt_required() means the route is protected, token is needed
    # "SignInServer\lib\site-packages\flask_jwt\__init__.py"
    # the request to auth api must be in application/json

    def authenticate(phonenum, password):
        print(phonenum)
        print(password)
        userInfo = User.get(User, phonenum)
        if (userInfo is None):
            raise JWTError('Bad credentials',
                           'User not found!',
                           status_code=404)
        else:
            if safe_str_cmp(userInfo.password.encode('utf-8'), password.encode('utf-8')):
                return userInfo
            else:
                raise JWTError('Bad credentials',
                               'Incorrect password!',
                               status_code=404)


    def identity(payload):
        phonenum = payload['identity']
        return User.get(User, phonenum)

    jwt = JWT(app, authenticate, identity)


    @jwt.jwt_payload_handler
    def payload_handler(identity):
        iat = datetime.utcnow()
        exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
        nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
        identity = str(getattr(identity, 'phonenum'))
        return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}

    @jwt.auth_response_handler
    def auth_response_handler(access_token, identity):
        return jsonify({
            'access_token': access_token.decode('utf-8'),
            'phonenum': str(getattr(identity, 'phonenum')),
            'password': str(getattr(identity, 'password')),
            'nickname': str(getattr(identity, 'nickname')),
            'college': str(getattr(identity, 'college')),
            'major': str(getattr(identity, 'major')),
            'sex': str(getattr(identity, 'sex')),
            'stuID': str(getattr(identity, 'stuID')),
            'srealname': str(getattr(identity, 'srealname')),
            'jobID': str(getattr(identity, 'jobID')),
            'trealname': str(getattr(identity, 'trealname'))
        })

    @jwt.jwt_error_handler
    def error_response_handler(error):
        return jsonify(OrderedDict([
            ('status_code', error.status_code),
            ('error', error.error),
            ('message', error.description),
        ])), error.status_code, error.headers



    # for registering
    @app.route('/api/register', methods=['POST'])
    def register():
        required_keys = ['phonenum',
                         'password',
                         'nickname',
                         'college',
                         'major',
                         'sex',
                         'ID',
                         'realname',
                         'ident']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            password = request.form.get('password')
            nickname = request.form.get('nickname')
            college = request.form.get('college')
            major = request.form.get('major')
            sex = request.form.get('sex')
            ID = request.form.get('ID')
            realname = request.form.get('realname')
            ident = request.form.get('ident')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "password": password,
                        "nickname": nickname,
                        "college": college,
                        "major": major,
                        "sex": sex,
                        "ID": ID,
                        "realname": realname,
                        "ident": ident,
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:
                # Check if user already exists
                if User.get(User, phonenum):
                    data['message'] = "A User with that username already exists"
                else:
                    if ident == 'student':
                        userInfo = User(phonenum=phonenum,
                                    password=password,
                                    nickname=nickname,
                                    college=college,
                                    major=major,
                                    sex=sex,
                                    stuID=ID,
                                    srealname=realname,
                                    jobID=None,
                                    trealname=None)
                        _ = User.add(User, userInfo)
                        data['status'] = 200
                        data['message'] = 'Student successfully registered!'
                    elif ident == 'teacher':
                        userInfo = User(phonenum=phonenum,
                                    password=password,
                                    nickname=nickname,
                                    college=college,
                                    major=major,
                                    sex=sex,
                                    stuID=None,
                                    srealname=None,
                                    jobID=ID,
                                    trealname=realname)
                        _ = User.add(User, userInfo)
                        data['status'] = 200
                        data['message'] = 'Teacher successfully registered!'
                    else:
                        data['status'] = 406
                        data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # for updating info
    @app.route('/api/updatauser', methods=['POST'])
    def updatauser():
        pass

################################################################
    # about class
    # when you login and enter the main UI,
    # if you are student, you will see all your class by getclass()
    # and if your class is not in, you can search for in by getallclass()
    # and join it by addclass()
    # if you are teacher, you will see all your class by getclass()
    # and if your class is not in, you can create it by addclass()
################################################################
    # student search all class
    @app.route('/api/getallclass', methods=['POST'])
    @jwt_required()
    def getallclass():
        required_keys = ['phonenum',
                         'ident']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            ident = request.form.get('ident')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "ident": ident
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:
                if ident == 'student':
                    # get all class
                    classes = Class.getall(Class)
                    res = list()
                    for cls in classes:
                        res.append(Class.out(Class, cls))
                    data['message'] = res
                    data['status'] = 200

                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # when student or teacher enters main UI, get his class automatically
    @app.route('/api/getclass', methods=['POST'])
    @jwt_required()
    def getclass():
        required_keys = ['phonenum',
                         'ident',
                         'ID']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            ident = request.form.get('ident')
            ID = request.form.get('ID')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "ident": ident,
                        "ID": ID
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:
                if ident == 'student':

                    # connect classtable with jointable
                    classes = Class.stugetclass(Class, ID)
                    res = list()
                    for cls in classes:
                        res.append(Class.out(Class, cls))
                    data['message'] = res
                    data['status'] = 200
                elif ident == 'teacher':

                    # connect classtable with teachtable
                    classes = Class.teagetclass(Class, ID)
                    res = list()
                    for cls in classes:
                        res.append(Class.out(Class, cls))
                    data['message'] = res
                    data['status'] = 200
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # teacher create class via classID & classname
    # student join class via classID
    @app.route('/api/addclass', methods=['POST'])
    @jwt_required()
    def addclass():
        required_keys = ['phonenum',
                         'ident',
                         'ID',
                         'classID',
                         'classname']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            ident = request.form.get('ident')
            ID = request.form.get('ID')
            classID = request.form.get('classID')
            classname = request.form.get('classname')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "ident": ident,
                        "ID": ID,
                        "classID": classID,
                        "classname": classname
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:
                if ident == 'teacher':

                    # create class
                    # 1. assume teach relation not exist
                    # 2. if class exist then create relationship
                    # 3. if class not exist then create both
                    tcls = TeachTable.get(TeachTable, classID, ID)
                    if tcls:
                        data['status'] = 400
                        data['message'] = 'teach relation exist!'
                    else:
                        cls = Class.get(Class, classID)
                        if cls:
                            tcls = TeachTable(tid=TeachTable.getid(TeachTable)+1,
                                              classID=classID,
                                              jobID=ID)
                            _ = TeachTable.add(TeachTable, tcls)
                            data['status'] = 200
                            data['message'] = 'Teacher successfully added!'
                        else:
                            cls = Class(classID=classID,
                                        classname=classname)
                            _ = Class.add(Class, cls)
                            tcls = TeachTable(tid=TeachTable.getid(TeachTable)+1,
                                              classID=classID,
                                              jobID=ID)
                            _ = TeachTable.add(TeachTable, tcls)
                            data['status'] = 200
                            data['message'] = 'Teacher successfully added!'


                elif ident == 'student':

                    # join class
                    # 1. assume relation not exist
                    # 2. if class exist join it
                    # 2. if class not exist return
                    jcls = JoinTable.get(JoinTable, classID, ID)
                    if jcls:
                        data['status'] = 400
                        data['message'] = 'join relation exist!'
                    else:
                        cls = Class.get(Class, classID)
                        if cls:
                            jcls = JoinTable(jid=JoinTable.getid(JoinTable)+1,
                                             classID=classID,
                                             stuID=ID)
                            _ = JoinTable.add(JoinTable, jcls)
                            data['status'] = 200
                            data['message'] = 'Student successfully joined!'
                        else:
                            data['status'] = 400
                            data['message'] = 'Class not exist!'

                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

# AFTER ENTERING THE CLASS
################################################################
    # about members subUI
    # when you login and enter the main UI and select your class
    # if you are student or teacher, in members subUI, you will see
    # all students who selected this class by getallstudent()
    # teacher can view students' signin status by getSignIn()
################################################################
    # when student or teacher enters class UI, get all students who joined this class
    @app.route('/api/getallstudent', methods=['POST'])
    @jwt_required()
    def getallstudent():
        required_keys = ['phonenum',
                         'classID',
                         'ident']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:

                # get all users in the specific class
                users = User.getall(User, classID)
                res = list()
                for usr in users:
                    res.append(User.out(User, usr))

                if ident == 'student':

                    data['status'] = 200
                    data['message'] = res
                elif ident == 'teacher':

                    data['status'] = 200
                    data['message'] = res
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp


################################################################
    # about message subUI
    # when you login and enter the main UI and select your class
    # if you are student, in this UI, you can submit your message by addmessage()
    # and see teacher's bulletins by getbulletin()
    # and replies by getmessage()
    # if you are teacher, in this UI, you can submit your bulletin by addbulletin()
    # and reply to one student by addmessage()
    # and see student's message by getmessage()
################################################################
    # students submit message to teacher
    # teachers give replies
    # use time in app
    @app.route('/api/addmessage', methods=['POST'])
    @jwt_required()
    def addmessage():
        required_keys = ['phonenum',
                         'classID',
                         'ident',
                         'ID',
                         'content',
                         'time',
                         'isleave']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')
            stuID = request.form.get('ID')
            content = request.form.get('content')
            time = request.form.get('time')
            isleave = request.form.get('isleave')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident,
                        "ID": stuID,
                        "content": content,
                        "time": time,
                        "isleave": isleave
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:

                # student or teacher add message
                mess = Message(mid=Message.getid(Message) + 1,
                               classID=classID,
                               stuID=stuID,
                               time=time,
                               content=content,
                               sender=ident,
                               isleave=isleave)

                if ident == 'student':

                    _ = Message.add(Message, mess)
                    data['status'] = 200
                    data['message'] = 'Students message successfully added!'
                elif ident == 'teacher':

                    _ = Message.add(Message, mess)
                    data['status'] = 200
                    data['message'] = 'teachers message successfully registered!'
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # teacher add bulletin
    @app.route('/api/addbulletin', methods=['POST'])
    @jwt_required()
    def addbulletin():
        required_keys = ['phonenum',
                         'classID',
                         'ident',
                         'content',
                         'time']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')
            content = request.form.get('content')
            time = request.form.get('time')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident,
                        "content": content,
                        "time": time
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:

                # teacher add bulletin
                if ident == 'teacher':

                    bull = Bulletin(bid=Bulletin.getid(Bulletin) + 1,
                                    classID=classID,
                                    time=time,
                                    content=content)
                    _ = Bulletin.add(Bulletin, bull)
                    data['status'] = 200
                    data['message'] = 'Teacher successfully broadcast!'
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # get all message(s2t & t2s)
    @app.route('/api/getmessage', methods=['POST'])
    @jwt_required()
    def getmessage():
        required_keys = ['phonenum',
                         'classID',
                         'ID',
                         'ident']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            stuID = request.form.get('ID')
            ident = request.form.get('ident')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ID": stuID,
                        "ident": ident
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]


            if conforms_to_schema:

                #get all messages here

                if ident == 'student':

                    messes = Message.get(Message, classID, stuID)
                    res = list()
                    for mess in messes:
                        res.append(Message.out(Message, mess))

                    data['status'] = 200
                    data['message'] = res
                elif ident == 'teacher':

                    messes = Message.getall(Message, classID)
                    res = list()
                    for mess in messes:
                        res.append(Message.out(Message, mess))

                    data['status'] = 200
                    data['message'] = res
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # get all bulletin
    @app.route('/api/getbulletin', methods=['POST'])
    @jwt_required()
    def getbulletin():
        required_keys = ['phonenum',
                         'classID',
                         'ident']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]

            if conforms_to_schema:

                # get all bulletins here
                bulls = Bulletin.getall(Bulletin, classID)
                res = list()
                for bull in bulls:
                    res.append(Bulletin.out(Bulletin, bull))

                if ident == 'student':

                    data['status'] = 200
                    data['message'] = res
                elif ident == 'teacher':

                    data['status'] = 200
                    data['message'] = res
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp


################################################################
    # about signin subUI
    # when you login and enter the main UI and select your class
    # firstly, teacher start signin by startSignIn(), and inform of all the students
    # then, students finish signin by startSignIn()
    # finally, teacher close the signin by closeSignIn(),
    # and if teacher forgot that, app will automatically request to do this
    # after signin, teacher will see all signin status by getSignIn()
    # and students will see his/her signin status by getSignIn()
################################################################
    # student or teacher click signin
    # student finish signining
    # teacher start signing
    @app.route('/api/startSignIn', methods=['POST'])
    @jwt_required()
    def startSignIn():
        required_keys = ['phonenum',
                         'classID',
                         'ident',
                         'ID',
                         'time',
                         'location']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')
            ID = request.form.get('ID')
            stime = request.form.get('time')
            location = request.form.get('location')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident,
                        "ID": ID,
                        "time": stime,
                        "location": location
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]

            if conforms_to_schema:

                if ident == 'teacher':

                    # teacher starts signing
                    # 1. assume that this class is not signing
                    # 2. add info to table
                    # 3. add info to CLASS_SIGNIN_STATUS
                    if classID in CLASS_SIGNIN_STATUS:
                        data['status'] = 400
                        data['message'] = 'cannot start twice!'
                    else:
                        users = User.getall(User, classID)
                        for usr in users:
                            attendInfo = Attendtable(
                                aid=Attendtable.getid(Attendtable)+1,
                                classID=classID,
                                stuID=usr.stuID,
                                time=stime,
                                result=0
                            )
                            _ = Attendtable.add(Attendtable, attendInfo)
                        CLASS_SIGNIN_STATUS[classID] = location
                        print(CLASS_SIGNIN_STATUS[classID])
                        data['status'] = 200
                        data['message'] = 'Signin successfully started!'

                elif ident == 'student':

                    # student starts signing
                    # 1. assume that this class is signing
                    if classID not in CLASS_SIGNIN_STATUS:
                        data['status'] = 400
                        data['message'] = 'class is not signining now!'
                    else:
                        tlocation = CLASS_SIGNIN_STATUS[classID]
                        print(tlocation)
                        tx, ty = tlocation.split()
                        tx, ty = float(tx), float(ty)
                        slocation = location
                        print(slocation)
                        sx, sy = slocation.split()
                        sx, sy = float(sx), float(sy)


                        # trans and cal

                        if (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy) < 1:
                            Attendtable.update(Attendtable, classID=classID, stuID=ID)
                            data['status'] = 200
                            data['message'] = 'Student successfully signined!'
                        else:
                            data['status'] = 200
                            data['message'] = 'signin fail!'
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # teacher click signin again to close it
    @app.route('/api/closeSignIn', methods=['POST'])
    @jwt_required()
    def closeSignIn():
        required_keys = ['phonenum',
                         'classID',
                         'ident']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]

            if conforms_to_schema:

                if ident == 'teacher':

                    if classID not in CLASS_SIGNIN_STATUS:
                        data['status'] = 400
                        data['message'] = 'class is not signining!'
                    else:
                        del CLASS_SIGNIN_STATUS[classID]
                        data['message'] = 'Signin successfully closed!'
                        data['status'] = 200

                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    @app.route('/api/getSignIn', methods=['POST'])
    @jwt_required()
    def getSignIn():
        required_keys = ['phonenum',
                         'classID',
                         'ident',
                         'ID']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            classID = request.form.get('classID')
            ident = request.form.get('ident')
            ID = request.form.get('ID')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "classID": classID,
                        "ident": ident,
                        "ID": ID
                    }
                )
                conforms_to_schema = True
            except MultipleInvalid as e:
                conforms_to_schema = False
                if "expected" in e.msg:
                    data['message'] = e.path[0] + " is not in the correct format"
                else:
                    data['message'] = e.msg + " for " + e.path[0]

            if conforms_to_schema:

                if ident == 'teacher':

                    # for teacher
                    # display all students' signin status in classID
                    atts = Attendtable.getall(Attendtable, classID)
                    res = list()
                    for att in atts:
                        res.append(Attendtable.out(Attendtable, att))

                    data['status'] = 200
                    data['message'] = res

                elif ident == 'student':

                    # for student
                    # display his/her signin status in classID
                    atts = Attendtable.get(Attendtable, classID, ID)
                    res = list()
                    for att in atts:
                        res.append(Attendtable.out(Attendtable, att))

                    data['status'] = 200
                    data['message'] = res
                else:
                    data['status'] = 406
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

################################################################

    @jwt_required()
    def protected():
        return '%s' % current_identity


    def validate_data_format(request, required_keys):
        data = {}
        data['status'] = 404
        valid_data = True
        if not request.form:
            data['message'] = 'No data was provided'
            valid_data = False
        else:
            valid_data = all(
                key in request.form for key in required_keys)  # Check if request.json contains all the required keys
            if valid_data:
                valid_data = "" not in request.form.to_dict().values()  # Check if request.json contains content for all values
            if valid_data == False:
                data['message'] = 'All fields must be provided!'
        return (valid_data, data)


    # for testing
    @app.route('/')
    def index():
        return jsonify({'message': 'test'})

    @app.route('/api/test', methods=['POST'])
    def test():
        phonenum = request.form.get('phonenum')
        password  = request.form.get('password')
        print(request.form)
        print(phonenum)
        print(password)
        if phonenum == '11111111111' and password == 'admin':
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': 'fail'})