from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import openai
import tiktoken
import os
import glob

app = Flask(__name__)
FILES_DIRECTORY = '/files/'
txt_extensions = ['.txt', '.ps1', '.py','.sh']
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', '.ps1', '.py','.sh'}
encoding = tiktoken.encoding_for_model("gpt-4")

token_buffer=100

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
@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.json.get('prompt')
    system=request.json.get('system')
    context=request.json.get('context')
    model="gpt-4"
    if context:
        context="You, referred to by text that starts AI:, and a human, referred to by test that starts with Human:, previously had this conversation: \n"+context+"\nYou do not need to prepend AI or Human to any answer, instead just answer the prompt directly.\n\n"
        prompt=context+prompt
    return jsonify(chat_generate_text(prompt, model=model, system_prompt=system, max_tokens=8000))
def chat_generate_text(
    prompt,
    model = "gpt-3.5-turbo",
    system_prompt= "You are a helpful assistant.",
    temperature=0.9,
    max_tokens= 256,
    n= 1,
    stop = None,
    presence_penalty = 0,
    frequency_penalty = 0.1
    ):

    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": prompt},
    ]
    openai.api_key=os.environ.get("OPENAI_API_KEY")
    avail_toks=max_tokens
    # Count the number of tokens
    num_tokens=len(encoding.encode(prompt))+token_buffer
    avail_toks=avail_toks-num_tokens

    if avail_toks<0:
        return "The token context is greater than "+max_tokens+". Please reduce the context size or the question length"
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=avail_toks,
        n=n,
        stop=stop,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )

    generated_texts = [
        choice.message["content"].strip() for choice in response["choices"]
    ]
    return generated_texts[0]
if __name__ == '__main__':
    app.run()

