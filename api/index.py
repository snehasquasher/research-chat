from flask import Flask, redirect, request
import sys

app = Flask(__name__)

@app.route("/api/python")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/uploadFiles", methods = ['POST'])
def upload_papers():
    print("HI!", file=sys.stderr)
    print("FILES: ", request.files, file=sys.stderr)
    return redirect("/chat")