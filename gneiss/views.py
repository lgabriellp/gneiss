from flask import Blueprint

from gneiss import util

stats = Blueprint("stats", __name__, static_folder="static")


@stats.route("/emulation/<int:id>")
def index():
    return util.render_text("index", {"canvas": [{"name": "round"}]})


@stats.route("/emulation/<int:eid>/round/<int:rid>")
def round(eid, rid):
    pass
