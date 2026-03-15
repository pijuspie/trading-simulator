from flask import Flask, send_from_directory, jsonify, redirect, request

# serve static pages
# sign up
# sign in
# create update delete projects
# buy sell stocks

app = Flask(__name__, static_folder="static")

@app.before_request
def strip_index_html():
    path = request.path

    if path.endswith("/index.html"):
        new_path = path[:-10]
        return redirect(new_path, code=301)

# @app.post("/api/signup")
# def signup():
#     data = request.json

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        try:
            return send_from_directory(app.static_folder, path+"index.html")
        except:
            return "Page not found", 404
