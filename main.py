import os
from flask import Flask, render_template, request, jsonify
from utils.openai_vision import analyze_plant_image

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    try:
        result = analyze_plant_image(image)
        print("Structured result:", result)  # Add this line for debugging
        return jsonify(result)
    except Exception as e:
        print("Error:", str(e))  # Add this line for debugging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
