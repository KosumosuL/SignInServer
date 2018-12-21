from flask import jsonify, request
from flask_jwt import JWT, jwt_required, current_identity, JWTError
from SignIn.User.model import User
from SignIn import utility
from werkzeug.security import safe_str_cmp
from collections import OrderedDict
from datetime import datetime
from voluptuous import Schema, Any, Required, All, Length, Range, MultipleInvalid, Invalid


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


    # auth part
    # @jwt_required() means the route is protected, token is needed
    # "C:\Users\11096\Desktop\SignInServer\lib\site-packages\flask_jwt\__init__.py"
    # the request to auth api must be in application/json

    def authenticate(phonenum, password):
        print(phonenum)
        print(password)
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




    # work part
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
                        data['status'] = 200
                        data['message'] = 'Student successfully registered!'
                    else:
                        data['message'] = 'illegal identity'

        resp = jsonify(data)
        resp.status_code = data['status']
        return resp

    @app.route('/protected', methods=['POST'])
    @jwt_required()
    def protected():
        return '%s' % current_identity


    # 'request.form' remains to be test
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


    # test part
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