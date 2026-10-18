
import json
import os
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from azure.eventhub import EventHubConsumerClient

load_dotenv()

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"]
    }
})

CONNECTION_STRING = os.getenv("EVENTHUB_CONNECTION_STRING")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "$Default")

latest = {
    "ascii_values": None,
    "message": "Waiting for Azure telemetry...",
    "timestamp": None,
}

status = {
    "azure_connected": False,
    "last_error": None,
}

data_lock = threading.Lock()


def decode_message(raw):
    text = raw.strip()
    codes = None

    # JSON ASCII array: [72,101,108,108,111]
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list) and all(
            type(x) is int and 0 <= x <= 127 for x in parsed
        ):
            codes = parsed
    except (json.JSONDecodeError, TypeError):
        pass

    # Comma-separated ASCII: 72,101,108,108,111
    if codes is None and "," in text:
        try:
            parsed = [int(x.strip()) for x in text.split(",")]
            if all(0 <= x <= 127 for x in parsed):
                codes = parsed
        except ValueError:
            pass

    if codes is not None:
        return codes, "".join(chr(x) for x in codes)

    # Ordinary ASCII text
    try:
        return list(text.encode("ascii")), text
    except UnicodeEncodeError:
        return None, text


def receive_events():
    if not CONNECTION_STRING:
        with data_lock:
            status["last_error"] = (
                "Missing EVENTHUB_CONNECTION_STRING in backend/.env"
            )
        print(status["last_error"], flush=True)
        return

    try:
        client = EventHubConsumerClient.from_connection_string(
            conn_str=CONNECTION_STRING,
            consumer_group=CONSUMER_GROUP,
        )

        def on_event(partition_context, event):
            if event is None:
                return

            raw = event.body_as_str(encoding="UTF-8")
            ascii_values, message = decode_message(raw)

            timestamp = (
                event.enqueued_time.isoformat()
                if event.enqueued_time
                else datetime.now(timezone.utc).isoformat()
            )

            with data_lock:
                latest["ascii_values"] = ascii_values
                latest["message"] = message
                latest["timestamp"] = timestamp
                status["azure_connected"] = True
                status["last_error"] = None

            print("Received ASCII:", ascii_values, flush=True)
            print("Decoded message:", message, flush=True)

        print("Connecting to Azure Event Hubs...", flush=True)

        with client:
            client.receive(
                on_event=on_event,
                starting_position="@latest",
            )

    except Exception as exc:
        with data_lock:
            status["azure_connected"] = False
            status["last_error"] = str(exc)

        print("Azure receiver error:", exc, flush=True)


@app.route("/api/latest", methods=["GET"])
def get_latest():
    with data_lock:
        return jsonify({
            **latest,
            **status,
        })


@app.route("/health", methods=["GET"])
def health():
    with data_lock:
        return jsonify({
            "backend_status": "ok",
            **status,
        })


if __name__ == "__main__":
    receiver_thread = threading.Thread(
        target=receive_events,
        daemon=True,
    )
    receiver_thread.start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )

if __name__ == "__main__":
    receiver_thread = threading.Thread(
        target=receive_events,
        daemon=True,
    )
    receiver_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
