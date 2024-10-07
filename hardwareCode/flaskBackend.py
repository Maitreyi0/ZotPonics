from flask import Flask, jsonify
from AtlasI2C_Subsystem import AtlasI2C_SubsystemData

app = Flask(__name__)

@app.route('/get_object', methods=['GET'])
def get_object():
    obj = MyClass('example', 42)
    return jsonify(obj.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
