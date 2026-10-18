
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

# Allow the local React app.
# Add your Vercel domain here when the frontend is deployed.
allowed_origins = [
    "http://localhost:3000",
]

vercel_origin = os.getenv("FRONTEND_ORIGIN")
if vercel_origin:
    allowed_origins.append(vercel_origin.rstrip("/"))

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
)

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
        error = "Missing EVENTHUB_CONNECTION_STRING environment variable"
        with data_lock:
            status["last_error"] = error
        print(error, flush=True)
        return

    try:
        print("Connecting to Azure Event Hubs...", flush=True)

        client = EventHubConsumerClient.from_connection_string(
            conn_str=CONNECTION_STRING,
            consumer_group=CONSUMER_GROUP,
        )

        def on_event(partition_context, event):
            if event is None:
                return

            try:
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

            except Exception as exc:
                print("Event processing error:", str(exc), flush=True)

        with client:
            client.receive(
                on_event=on_event,
                starting_position="@latest",
            )

    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        with data_lock:
            status["azure_connected"] = False
            status["last_error"] = error

        print("Azure receiver error:", error, flush=True)


@app.route("/")
def home():
    return jsonify({
        "service": "Azure IoT Hub Backend",
        "status": "running",
    })


@app.route("/health", methods=["GET"])
def health():
    with data_lock:
        return jsonify({
            "backend_status": "ok",
            **status,
        })


@app.route("/api/latest", methods=["GET"])
def get_latest():
    with data_lock:
        result = {
            **latest,
            **status,
        }

    print("API DATA:", result, flush=True)
    return jsonify(result)


# Start the receiver when the module is imported by Gunicorn.
# Keep Render configured with one Gunicorn worker for this simple setup.
receiver_thread = threading.Thread(
    target=receive_events,
    daemon=True,
    name="azure-eventhub-receiver",
)
receiver_thread.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
