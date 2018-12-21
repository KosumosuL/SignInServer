from SignIn import init_app

app = init_app('SignIn.config')

if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])