import asyncio
import db
from feedgen.feed import FeedGenerator
from flask import Flask, Response
from logger import get_logger
import threading

logger = get_logger(__name__)

app = Flask(__name__)
fg = FeedGenerator()
fg.title("Vinted Notifications")
fg.description("RSS Feed for Vinted Notifications")
fg.link(href="http://localhost:8080")

rss_items = []


@app.route("/")
def rss():
    global rss_items
    fg = FeedGenerator()
    fg.title("Vinted Notifications")
    fg.description("RSS Feed for Vinted Notifications")
    fg.link(href="http://localhost:8080")

    for item in rss_items[-50:]:
        fe = fg.add_entry()
        fe.title(item["title"])
        fe.link(href=item["url"])
        fe.description(item["description"])

    return Response(fg.rss_str(pretty=True), mimetype="application/rss+xml")


def run_flask():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)


def rss_feed_process(queue):
    logger.info("RSS feed process started")
    global rss_items

    # Start Flask in a thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        while True:
            if not queue.empty():
                item = queue.get()
                content, url, button_text, buy_url, buy_button_text = item
                rss_items.append({
                    "title": content.split("\n")[0] if content else "New Item",
                    "url": url,
                    "description": content,
                })
            # Small sleep to prevent high CPU usage
            import time
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        logger.info("RSS feed process stopped")
