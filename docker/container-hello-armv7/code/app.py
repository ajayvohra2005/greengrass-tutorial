from flask import Flask
from flask import Response
import json
import time

app = Flask(__name__)

counter = 0

@app.route('/')
def hello():
    global counter
    counter += 1
    res={}
    res['message'] = "Hello world!"
    res['count'] = counter
    res['timestamp'] = time.time()
    return Response(response=json.dumps(res), 
                    status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
