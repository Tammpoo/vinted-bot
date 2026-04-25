import os
import db
import core
from flask import Flask, render_template, request, jsonify, redirect, url_for
from logger import get_logger

logger = get_logger(__name__)
app = Flask(__name__)


def get_port():
    return int(os.environ.get("PORT", 8000))


@app.route("/")
def index():
    queries = db.get_queries()
    items = db.get_items(limit=50)
    config = {
        "telegram_enabled": db.get_parameter("telegram_enabled") == "True",
        "telegram_token": db.get_parameter("telegram_token") or "",
        "telegram_chat_id": db.get_parameter("telegram_chat_id") or "",
        "rss_enabled": db.get_parameter("rss_enabled") == "True",
        "query_refresh_delay": db.get_parameter("query_refresh_delay") or "30",
        "items_per_query": db.get_parameter("items_per_query") or "20",
        "message_template": db.get_parameter("message_template") or "",
        "banwords": db.get_parameter("banwords") or "",
        "proxies": db.get_parameter("proxies") or "",
    }
    is_up_to_date, ver, latest, github_url = core.check_version()
    return render_template(
        "index.html",
        queries=queries,
        items=items,
        config=config,
        version=ver,
        latest_version=latest,
        is_up_to_date=is_up_to_date,
        github_url=github_url,
    )


@app.route("/queries")
def queries_page():
    queries = db.get_queries()
    return render_template("queries.html", queries=queries)


@app.route("/api/add_query", methods=["POST"])
def api_add_query():
    data = request.json
    query_url = data.get("query", "")
    name = data.get("name", None)
    if not query_url:
        return jsonify({"success": False, "message": "Query URL is required"})
    message, is_new = core.process_query(query_url, name)
    return jsonify({"success": is_new, "message": message})


@app.route("/api/remove_query", methods=["POST"])
def api_remove_query():
    data = request.json
    query_id = data.get("id", "")
    message, success = core.process_remove_query(str(query_id))
    return jsonify({"success": success, "message": message})


@app.route("/api/update_config", methods=["POST"])
def api_update_config():
    data = request.json
    for key, value in data.items():
        db.set_parameter(key, str(value))
    return jsonify({"success": True, "message": "Configuration updated"})


@app.route("/items")
def items_page():
    query_id = request.args.get("query_id", None)
    if query_id:
        items = db.get_items(query_id=int(query_id), limit=100)
    else:
        items = db.get_items(limit=100)
    queries = db.get_queries()
    return render_template("items.html", items=items, queries=queries)


@app.route("/allowlist")
def allowlist_page():
    allowlist = db.get_allowlist()
    if allowlist == 0:
        allowlist = []
    return render_template("allowlist.html", allowlist=allowlist)


@app.route("/api/add_country", methods=["POST"])
def api_add_country():
    data = request.json
    country = data.get("country", "")
    message, country_list = core.process_add_country(country)
    return jsonify({"success": True, "message": message, "allowlist": country_list})


@app.route("/api/remove_country", methods=["POST"])
def api_remove_country():
    data = request.json
    country = data.get("country", "")
    message, country_list = core.process_remove_country(country)
    return jsonify({"success": True, "message": message, "allowlist": country_list})


@app.route("/config")
def config_page():
    config = {
        "telegram_enabled": db.get_parameter("telegram_enabled") == "True",
        "telegram_token": db.get_parameter("telegram_token") or "",
        "telegram_chat_id": db.get_parameter("telegram_chat_id") or "",
        "rss_enabled": db.get_parameter("rss_enabled") == "True",
        "query_refresh_delay": db.get_parameter("query_refresh_delay") or "30",
        "items_per_query": db.get_parameter("items_per_query") or "20",
        "message_template": db.get_parameter("message_template") or "",
        "banwords": db.get_parameter("banwords") or "",
        "proxies": db.get_parameter("proxies") or "",
    }
    return render_template("config.html", config=config)


@app.route("/logs")
def logs_page():
    log_content = ""
    log_path = "./logs/vinted_notifications.log"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log_content = f.read()[-5000:]
    return render_template("logs.html", logs=log_content)


def web_ui_process():
    logger.info("Web UI process started")
    port = get_port()
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
