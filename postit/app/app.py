from flask import Flask, request, render_template_string, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import glob

app = Flask(__name__)
FILES_DIRECTORY = '/files/'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        filename = request.form['filename']
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)
            full_path = os.path.join(FILES_DIRECTORY, filename)
            if os.path.exists(full_path):
                return jsonify(error=f'File {filename} already exists'), 409
            file.save(full_path)
            return f'Saved file to {full_path}'
        else:
            if not filename.endswith('.txt'):
                filename += '.txt'
            full_path = os.path.join(FILES_DIRECTORY, filename)
            # Ensure the final path is within FILES_DIRECTORY to prevent directory traversal attacks
            if not os.path.commonprefix([full_path, FILES_DIRECTORY]) == FILES_DIRECTORY:
                return jsonify(error="Invalid filename"), 400
            # Check if the file already exists and return a 409 status code
            if os.path.isfile(full_path):
                return jsonify(error=f"File {filename} already exists"), 409
            text = request.form['text']
            with open(full_path, 'w') as f:
                f.write(text)
            return f'Saved text to {filename}'
    else:
        files = glob.glob(FILES_DIRECTORY + '*')
        files = [os.path.basename(file) for file in files]  # Get the base filename only
        return render_template_string('''
        <!doctype html>
        <html>
            <head>
                <title>Post It!</title>
                <!-- CodeMirror Resources -->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/codemirror.min.css">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/codemirror.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

                <!-- Specify the desired syntax mode here -->
                <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.62.0/mode/python/python.min.js"></script>

                <style>
                    .CodeMirror { height: auto; border: 1px solid #ddd; }
                    .context-menu {
                        display: none;
                        position: absolute;
                        z-index: 10000;
                        padding: 5px;
                        background: #fff;
                        border: 1px solid #ccc;
                    }
                    .context-menu-item {
                        cursor: pointer;
                        padding: 5px 10px;
                    }
                    .context-menu-item:hover {
                        background: #ddd;
                    }
                    .file-item {
                        display: inline-block;
                        text-align: center;
                        margin: 10px;
                    }
                    .file-item img {
                        width: 100px;
                        height: 100px;
                    }
                    .file-item span {
                        display: block;
                    }
                    .warning-box {
                        background-color: yellow;
                        border: 2px solid red;
                        padding: 20px;
                        margin: 10px;
                        position: relative;
                    }
                    .warning-box::before {
                        content: "!";
                        font-size: 40px;
                        color: red;
                        position: absolute;
                        left: 10px;
                        top: 50%;
                        transform: translateY(-50%);
                    }
                    .warning-box-content {
                        margin-left: 60px;  /* Make sure the content doesn't overlap the exclamation point */
                    }
                    .content {
                        width: 80%;
                        margin: auto;
                        background-color: white;
                        padding: 20px;
                        box-sizing: border-box;
                    }
                    body {
                        background-color: skyblue;
                    }
                </style>
            </head>
            <body>
            <div class="content">
                <h2>Post It! Paste Manager</h2>
                <hr />
                <form id="submitForm" method="POST">
                    <input type="text" id="filename" name="filename" maxlength="60" placeholder="Filename">
                    <input type="file" id="fileUpload" accept="*/*"><br>
                    <textarea id="editor" name="text"></textarea>
                    <button type="submit">Save</button>
                    <button type="button" id="clear">Clear</button>
                </form>

                <div id="contextMenu" class="context-menu">
                    <div id="loadFile" class="context-menu-item">Load</div>
                    <div id="deleteFile" class="context-menu-item">Delete</div>
                </div>
                <hr />
                <h2>Files</h2>
                <p>Right Click to load or delete a file. Left click will download the file.</p>
                <div id="fileList">
                    {% for file in files %}
                    <div class="file-item">
                        {% if file.endswith('.txt') %}
                            <img src="data:image/png;base64,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" alt="File Icon">
                        {% else %}
                            <img src="data:image/png;base64,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" alt="File Icon">
                        {% endif %}
                        <span class="file-name">{{ file }}</span>
                    </div>
                    {% endfor %}
                </div>

                <script>
                    var editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
                        lineNumbers: true,
                        mode: "python"  // change this to the mode you want
                    });

                    $("#submitForm").on("submit", function(e) {
                        e.preventDefault();
                        var filename = $("#filename").val();
                        var fileUpload = $("#fileUpload").get(0).files[0];
                        var data = new FormData();
                        data.append('filename', filename);
                        if (fileUpload) {
                            data.append('file', fileUpload);
                        } else {
                            data.append('text', editor.getValue());
                        }
                        $.ajax({
                            url: '/',
                            type: 'POST',
                            processData: false,  // required for file uploading
                            contentType: false,  // required for file uploading
                            data: data,
                            success: function() {
                                location.reload();
                            },
                            error: function(xhr) {
                                if (xhr.status == 409) {
                                    if (confirm(xhr.responseJSON.error + ' Do you want to overwrite it?')) {
                                        $.ajax({
                                            url: '/',
                                            type: 'POST',
                                            processData: false,
                                            contentType: false,
                                            data: data,
                                            success: function() {
                                                location.reload();
                                            }
                                        });
                                    }
                                }
                            }
                        });
                    });

                    $("#clear").on("click", function() {
                        $("#filename").val('');
                        editor.setValue('');
                    });

                    var currentFile;
                    $(".file-item").on("contextmenu", function(e) {
                        e.preventDefault();
                        currentFile = $(this).find(".file-name").text();
                        $("#contextMenu").css({
                            display: "block",
                            left: e.pageX,
                            top: e.pageY
                        });
                    });

                    $("#loadFile").on("click", function() {
                        $.ajax({
                            url: '/load',
                            type: 'POST',
                            data: { filename: currentFile },
                            success: function(data) {
                                $("#filename").val(currentFile);
                                editor.setValue(data);
                                $("#contextMenu").hide();
                            }
                        });
                    });

                    $("#deleteFile").on("click", function() {
                        $.ajax({
                            url: '/delete',
                            type: 'POST',
                            data: { filename: currentFile },
                            success: function() {
                                location.reload();
                            }
                        });
                    });

                    // Hide the context menu when clicking outside it
                    $(document).on("click", function(e) {
                        if ($(e.target).closest("#contextMenu").length === 0) {
                            $("#contextMenu").hide();
                        }
                    });

                    // Download file on left click
                    $(".file-item").on("click", function() {
                        var filename = $(this).find(".file-name").text();
                        window.location.href = "/download/" + filename;
                    });
                </script>
            </div>
            </body>
        </html>
        ''', files=files)

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
    if not filename.endswith('.txt'):
        return jsonify(error="Can only load .txt files"), 400
    if os.path.isfile(full_path):
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    return '', 404

if __name__ == '__main__':
    app.run()

