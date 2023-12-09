from flask import request, json, jsonify
from index import app  # Import the app instance
import requests 
import sys

@app.route("/api/uploadFiles", methods = ['POST'])
def upload_papers():
    print("FILES: ", request.files, len(request.files), file=sys.stderr)
    
    # save PDFs to user-uploads folder
    docID = 1
    for filename, file in request.files.items():
        name = request.files[filename].name
        print("file ", str(docID), name, file=sys.stderr)
        # file.save('user-uploads/' + str(docID) + '.pdf')
        docID += 1
    
    # return total number of PDFs
    return jsonify(str(docID -1)), 200

@app.route("/api/chatHelper", methods = ["POST"])
def chat_helper():
    if request.data == None:
        return jsonify("empty message"), 300
    else:
        files = os.listdir('user-uploads')
        if len(files) == 0:
            return jsonify("no uploaded user files"), 400
        
        # for now, just do the first file
        data = {}
        data['messages'] = [{"role": "user", "content": str(request.data)}]
        data['filename'] = files[0]
        json_data = json.dumps(data)
        return requests.post(request.url_root + '/api/chat', data=json_data)