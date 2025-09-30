from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False, ssl_context=('cert.pem', 'key.pem'))
