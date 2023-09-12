from flask import Flask, request

app = Flask(__name__)
app.secret_key = 'document_scanner_app'

@app.route('/')
def index():
    return 'hello world'




if __name__ == "__main__" :
    app.run(debug=True)


