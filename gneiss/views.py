from gneiss import app


@app.route("/")
def index():
    return "Gneiss"
