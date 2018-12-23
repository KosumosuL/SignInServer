from flask import jsonify, request
from flask_jwt import JWT, jwt_required, current_identity, JWTError
from SignIn.model import *
from werkzeug.security import safe_str_cmp
from collections import OrderedDict
from datetime import datetime
from voluptuous import Schema, Any, MultipleInvalid


def init_api(app):

    # Define Schema
    schema = Schema({
        "phonenum": Any(int, lambda s: len(s) == 11),
        "password": Any(str, lambda s: 8 <= len(s) <= 20),
        "nickname": Any(str),
        "college": Any(str),
        "major": Any(str),
        "sex": Any(int, lambda x: x == 0 or x == 1),
        "ID": Any(str, lambda s: len(s) == 10),
        "realname": Any(str),
        "ident": Any(str, lambda s: s == 'student' or s == 'teacher')
    })


    # for auth
    # @jwt_required() means the route is protected, token is needed
    # "C:\Users\11096\Desktop\SignInServer\lib\site-packages\flask_jwt\__init__.py"
    # the request to auth api must be in application/json

    def authenticate(phonenum, password):
        print(phonenum)
        print(password)
        # remains to be modified
        userInfo = User.query.filter_by(phonenum=phonenum).first()
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
        return User.get(phonenum)

    jwt = JWT(app, authenticate, identity)


    @jwt.jwt_payload_handler
    def payload_handler(identity):
        iat = datetime.utcnow()
        exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
        nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
        identity = str(getattr(identity, 'phonenum'))
        return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}

    # @jwt.auth_response_handler
    # def auth_response_handler(access_token, identity):
    #     return jsonify({
    #         'access_token': access_token.decode('utf-8'),
    #         'user_type': identity['type']
    #     })

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
                        user = User(phonenum=phonenum,
                                    password=password,
                                    nickname=nickname,
                                    college=college,
                                    major=major,
                                    sex=sex,
                                    stuID=ID,
                                    srealname=realname,
                                    jobID=None,
                                    trealname=None)
                        _ = User.add(User, user)
                        data['status'] = 200
                        data['message'] = 'Student successfully registered!'
                    elif ident == 'teacher':
                        user = User(phonenum=phonenum,
                                    password=password,
                                    nickname=nickname,
                                    college=college,
                                    major=major,
                                    sex=sex,
                                    stuID=None,
                                    srealname=None,
                                    jobID=ID,
                                    trealname=realname)
                        _ = User.add(User, user)
                        data['status'] = 200
                        data['message'] = 'Student successfully registered!'
                    else:
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
                         'stuID',
                         'jobID']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            ident = request.form.get('ident')
            stuID = request.form.get('stuID')
            jobID = request.form.get('jobID')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "ident": ident,
                        "stuID": stuID,
                        "jobID": jobID
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
                    classes = JoinTable.stugetclass(JoinTable, stuID)
                    res = list()
                    for cls in classes:
                        res.append(Class.out(Class, cls))
                    data['message'] = res
                    data['status'] = 200
                elif ident == 'teacher':

                    # connect classtable with teachtable
                    classes = TeachTable.teagetclass(TeachTable, jobID)
                    res = list()
                    for cls in classes:
                        res.append(Class.out(Class, cls))
                    data['message'] = res
                    data['status'] = 200
                else:
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    # teacher create class via classID & classname
    @app.route('/api/addclass', methods=['POST'])
    @jwt_required()
    def addclass():
        required_keys = ['phonenum',
                         'ident',
                         'stuID',
                         'jobID',
                         'classID',
                         'classname']
        validation = validate_data_format(request, required_keys)
        valid_format = validation[0]
        data = validation[1]

        if valid_format:
            phonenum = request.form.get('phonenum')
            ident = request.form.get('ident')
            stuID = request.form.get('stuID')
            jobID = request.form.get('jobID')
            classID = request.form.get('classID')
            classname = request.form.get('classname')

            try:
                schema(
                    {
                        "phonenum": phonenum,
                        "ident": ident,
                        "stuID": stuID,
                        "jobID": jobID,
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
                    cls = Class.get(Class, classID)
                    # decide by one ksy classID, hence only check Class
                    if ~ safe_str_cmp(cls.classname.encode('utf-8'), classname.encode('utf-8')):
                        cls = Class(classID=classID,
                                    classname=classname)
                        _ = Class.add(Class, cls)
                        tcls = TeachTable(classID=classID,
                                          jobID=jobID)
                        _ = TeachTable.add(TeachTable, tcls)
                        data['status'] = 200
                        data['message'] = 'Teacher successfully added!'
                    else:
                        data['status'] = 400
                        data['message'] = 'Class exist!'

                elif ident == 'student':

                    jcls = JoinTable(classID=classID,
                                     stuID=stuID)
                    _ = JoinTable.add(JoinTable, jcls)
                    data['status'] = 200
                    data['message'] = 'Student successfully joined!'
                else:
                    data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

# # AFTER ENTERING THE CLASS
# ################################################################
#     # about members subUI
#     # when you login and enter the main UI and select your class
#     # if you are student or teacher, in members subUI, you will see
#     # all students who selected this class by getallstudent()
# ################################################################
#     # when student or teacher enters class UI, get all students who joined this class
#     @app.route('/api/getallstudent', methods=['POST'])
#     @jwt_required()
#     def getallstudent():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#
#             if conforms_to_schema:
#
#                 # get all users in the specific class
#                 if ident == 'student':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 elif ident == 'teacher':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
# ################################################################
#     # about message subUI
#     # when you login and enter the main UI and select your class
#     # if you are student, in this UI, you can submit your message by addmessage()
#     # and leaving message by addleavemessage()
#     # and see teacher's bulletins by getbulletin()
#     # and replies by getmessage()
#     # if you are teacher, in this UI, you can submit your bulletin by addbulletin()
#     # and reply to one student by addmessage()
#     # and see student's message by getmessage()
#     # and leavemessage by getleavemessage()
# ################################################################
#     # students submit message to teacher
#     # teachers give replies
#     # use time in app
#     @app.route('/api/addmessage', methods=['POST'])
#     @jwt_required()
#     def addmessage():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident',
#                          'content',
#                          'time']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#             content = request.form.get('content')
#             time = request.form.get('time')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident,
#                         "content": content,
#                         "time": time
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#
#             if conforms_to_schema:
#
#                 # student or teacher add message
#                 if ident == 'student':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 elif ident == 'teacher':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
#     # student submit leave message to teacher
#     @app.route('/api/addleavemessage', methods=['POST'])
#     @jwt_required()
#     def addleavemessage():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident',
#                          'content',
#                          'time',
#                          'leavetime',
#                          'returntime']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#             time = request.form.get('time')
#             content = request.form.get('content')
#             leavetime = request.form.get('leavetime')
#             returntime = request.form.get('returntime')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident,
#                         "content": content,
#                         "time": time,
#                         "leavetime": leavetime,
#                         "returntime": returntime
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#
#             if conforms_to_schema:
#
#                 # student add leave message
#                 if ident == 'student':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
#     # teacher add bulletin
#     @app.route('/api/addbulletin', methods=['POST'])
#     @jwt_required()
#     def addbulletin():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident',
#                          'content',
#                          'time']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#             content = request.form.get('content')
#             time = request.form.get('time')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident,
#                         "content": content,
#                         "time": time
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#
#             if conforms_to_schema:
#
#                 # teacher add bulletin
#                 if ident == 'teacher':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
#     # get all message(s2t & t2s)
#     @app.route('/api/getmessage', methods=['POST'])
#     @jwt_required()
#     def getmessage():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#
#             if conforms_to_schema:
#
#                 #get all messages here
#
#                 if ident == 'student':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 elif ident == 'teacher':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
#     # get all leavemessage
#     @app.route('/api/getmessage', methods=['POST'])
#     @jwt_required()
#     def getmessage():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#             if conforms_to_schema:
#
#                 # get all leavemessages here
#
#                 if ident == 'student':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 elif ident == 'teacher':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
#     # get all bulletin
#     @app.route('/api/getmessage', methods=['POST'])
#     @jwt_required()
#     def getmessage():
#         required_keys = ['phonenum',
#                          'classID',
#                          'ident']
#         validation = validate_data_format(request, required_keys)
#         valid_format = validation[0]
#         data = validation[1]
#
#         if valid_format:
#             phonenum = request.form.get('phonenum')
#             classID = request.form.get('classID')
#             ident = request.form.get('ident')
#
#             try:
#                 schema(
#                     {
#                         "phonenum": phonenum,
#                         "classID": classID,
#                         "ident": ident
#                     }
#                 )
#                 conforms_to_schema = True
#             except MultipleInvalid as e:
#                 conforms_to_schema = False
#                 if "expected" in e.msg:
#                     data['message'] = e.path[0] + " is not in the correct format"
#                 else:
#                     data['message'] = e.msg + " for " + e.path[0]
#
#             if conforms_to_schema:
#
#                 # get all bulletins here
#
#                 if ident == 'student':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 elif ident == 'teacher':
#
#                     data['status'] = 200
#                     data['message'] = 'Student successfully registered!'
#                 else:
#                     data['message'] = 'illegal identity'
#
#         resp = jsonify(data)
#         resp.status_code = data['status']
#         return resp
#
#
# ################################################################
#     # about signin subUI
#     # when you login and enter the main UI and select your class
#     # if you are student, in this UI, you can
#     # if you are teacher, in this UI, you can
# ################################################################
#
#
#
#
# ################################################################

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