import openai
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# OpenAI API Key (Replace with a secure method to store API keys)
OPENAI_API_KEY = "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"

SUPPORTED_LANGUAGES = [
    "python", "javascript", "java", "c", "cpp", "csharp", "go", "ruby", "php", "swift", "kotlin", "rust", "r", "typescript", "dart", "elixir", "haskell", "lua", "perl", "scala", "clojure", "fsharp", "shell", "html", "css", "sql"
]

SUPPORTED_FRAMEWORKS = [
    "astro", "vite", "next.js", "svelte", "vue", "remix", "react", "angular", "nuxt.js", "solidjs"
]

def generate_code(prompt, language):
    """Generates code using OpenAI API"""
    if language not in SUPPORTED_LANGUAGES:
        return f"Unsupported language: {language}. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Generate {language} code: {prompt}"}]
    )
    return response["choices"][0]["message"]["content"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt", "")
    language = data.get("language", "python")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    code = generate_code(prompt, language)
    return jsonify({"code": code})

@app.route("/debug", methods=["POST"])
def debug():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "Code is required"}), 400
    
    debug_prompt = f"Debug this {language} code and provide fixes: {code}"
    debugged_code = generate_code(debug_prompt, language)
    return jsonify({"debugged_code": debugged_code})

@app.route("/preview", methods=["POST"])
def preview():
    data = request.json
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "Code is required"}), 400
    
    preview_file = "static/preview.html"
    with open(preview_file, "w") as f:
        f.write(code)
    
    return jsonify({"preview_url": f"/{preview_file}"})

@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "Code is required"}), 400
    
    script_path = f"temp_code.{language}"
    with open(script_path, "w") as f:
        f.write(code)
    
    try:
        output = subprocess.run(["nix-shell", "--run", f"{language} {script_path}"], capture_output=True, text=True, check=True)
        return jsonify({"output": output.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr})

@app.route("/deploy", methods=["POST"])
def deploy():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "html")
    deploy_path = "deployed_app"
    os.makedirs(deploy_path, exist_ok=True)
    file_path = os.path.join(deploy_path, f"index.{language}")
    
    with open(file_path, "w") as f:
        f.write(code)
    
    return jsonify({"deploy_url": f"/{deploy_path}/index.{language}"})

if __name__ == "__main__":
    app.run(debug=True)
