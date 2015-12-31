import numpy
from PIL import Image
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    x = request.files['input1']
    b = Image.open(x)
    b = numpy.array(b)
    return str(b)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)