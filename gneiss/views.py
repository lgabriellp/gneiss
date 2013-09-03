from flask import Blueprint

stats = Blueprint("stats", __name__, static_folder="static")


@stats.route("/")
def index():
    return "Gneiss"
