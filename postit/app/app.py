from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import glob

app = Flask(__name__)
FILES_DIRECTORY = '/files/'
txt_extensions = ['.txt', '.ps1', '.py','.sh']
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', '.ps1', '.py','.sh'}
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)
            full_path = os.path.join(FILES_DIRECTORY, filename)
            if os.path.exists(full_path):
                return jsonify(error=f'File {filename} already exists'), 409
            file.save(full_path)
        else:
            filename = request.form['filename']
            text = request.form['text']
            if os.path.splitext(filename)[1] not in txt_extensions:
                filename += '.txt'
            full_path = os.path.join(FILES_DIRECTORY, filename)
            if os.path.exists(full_path):
                return jsonify(error=f'File {filename} already exists'), 409
            with open(full_path, 'w') as f:
                f.write(text)
        return '', 204
    else:
        files = glob.glob(FILES_DIRECTORY + '*')
        files = [os.path.basename(file) for file in files]  # Get the base filename only
        return render_template("index.html", files=files)

@app.route('/uploads/<path:filename>', methods=['GET'])
def uploads(filename):
    return send_from_directory(FILES_DIRECTORY, filename, as_attachment=True)
@app.route('/img/<path:filename>', methods=['GET'])
def img(filename):
    return send_from_directory("/img/", filename, as_attachment=True)
@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    full_path = os.path.join(FILES_DIRECTORY, filename)
    # Ensure the final path is within FILES_DIRECTORY to prevent directory traversal attacks
    if not os.path.commonprefix([full_path, FILES_DIRECTORY]) == FILES_DIRECTORY:
        return jsonify(error="Invalid filename"), 400
    return send_from_directory(FILES_DIRECTORY, filename, as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete_file():
    filename = request.form['filename']
    full_path = os.path.join(FILES_DIRECTORY, filename)
    # Ensure the final path is within FILES_DIRECTORY to prevent directory traversal attacks
    if not os.path.commonprefix([full_path, FILES_DIRECTORY]) == FILES_DIRECTORY:
        return jsonify(error="Invalid filename"), 400
    if os.path.isfile(full_path):
        os.remove(full_path)
    return '', 204

@app.route('/load', methods=['POST'])
def load_file():
    filename = request.form['filename']
    full_path = os.path.join(FILES_DIRECTORY, filename)
    # Ensure the final path is within FILES_DIRECTORY to prevent directory traversal attacks
    if not os.path.commonprefix([full_path, FILES_DIRECTORY]) == FILES_DIRECTORY:
        return jsonify(error="Invalid filename"), 400
    if os.path.splitext(filename)[1] not in txt_extensions:
        return jsonify(error="Can only load text files"), 400
    if os.path.isfile(full_path):
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    return '', 404

if __name__ == '__main__':
    app.run()

