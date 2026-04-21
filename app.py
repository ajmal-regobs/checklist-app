import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify
from redis_client import get_redis

app = Flask(__name__)
r = get_redis()

CHECKLIST_KEY = "checklists"


@app.route("/")
def index():
    items = r.hgetall(CHECKLIST_KEY)
    checklists = [{"id": k, "name": v} for k, v in items.items()]
    return render_template("index.html", checklists=checklists)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("index"))
    item_id = str(uuid.uuid4())
    r.hset(CHECKLIST_KEY, item_id, name)
    return redirect(url_for("index"))


@app.route("/remove/<item_id>", methods=["POST"])
def remove(item_id):
    r.hdel(CHECKLIST_KEY, item_id)
    return redirect(url_for("index"))


@app.route("/api/checklists")
def api_list():
    items = r.hgetall(CHECKLIST_KEY)
    return jsonify([{"id": k, "name": v} for k, v in items.items()])


@app.route("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
