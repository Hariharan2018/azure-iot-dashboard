# Azure IoT Hub Live Telemetry Web Dashboard (`azure_web`)

A real-time telemetry monitoring dashboard designed to ingest, decode, and display live IoT messages from **Azure IoT Hub** / **Azure Event Hubs** using a **Flask (Python)** backend and a **React (JavaScript)** web interface.

---

## 🎯 What We Are Going to Do

The objective of this project is to build an end-to-end telemetry monitoring pipeline that receives messages sent to Azure IoT Hub from connected devices/sensors and presents them live in a web browser.

### Step-by-Step Implementation Workflow:

1. **Telemetry Ingestion from Azure**:
   - IoT devices or simulation scripts transmit sensor data / messages to Azure IoT Hub.
   - Azure IoT Hub forwards messages to its built-in Event Hub-compatible endpoint (`EntityPath`).

2. **Backend Processing & Message Decoding (`server.py`)**:
   - A Python Flask backend runs an asynchronous background consumer thread using `EventHubConsumerClient` from the `azure-eventhub` SDK.
   - It listens for incoming events starting from `@latest`.
   - It decodes diverse payload formats into readable strings:
     - **Plain text / UTF-8 strings**.
     - **JSON ASCII code arrays** (e.g., `[72, 101, 108, 108, 111]` $\rightarrow$ `"Hello"`).
     - **Comma-separated ASCII integers** (e.g., `"72,101,108,108,111"` $\rightarrow$ `"Hello"`).
   - In-memory state (`latest` message and ISO UTC timestamp) is kept thread-safe via `threading.Lock`.

3. **REST API Exposure**:
   - The backend provides two endpoints on port `8000` with CORS enabled:
     - `GET /api/latest`: Returns the most recent decoded telemetry message and timestamp.
     - `GET /health`: Health check endpoint returning service status.

4. **Frontend Dashboard (`src/azure_web.js`)**:
   - Replaces the default `App.js` with a dedicated `azure_web.js` component.
   - Polls `http://127.0.0.1:5000/api/latest` once every second (`1000ms`).
   - Renders:
     - **Connection Status indicator**: `CONNECTED` (green), `CONNECTING` (yellow), or `DISCONNECTED` (red).
     - **Decoded Message panel**: Real-time display of the latest message payload.
     - **Timestamp**: Formatted local date and time of the last received event.

---

## 🏗️ Architecture & Data Pipeline

```
+-------------------------------------------------------------+
|                     IoT Device / Sensor                     |
|           (Sends ASCII codes, byte arrays, or text)         |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                       Azure IoT Hub                         |
|             (Built-in Event Hubs Endpoint)                  |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     Flask Backend Service                   |
|                          (server.py)                        |
|   - EventHubConsumerClient (Background listener)            |
|   - Payload Decoder (ASCII array / comma-separated / UTF-8) |
|   - REST API: GET /api/latest & GET /health                 |
+------------------------------+------------------------------+
                               |
                               v (HTTP Polling every 1s)
+-------------------------------------------------------------+
|                   React Web Frontend                        |
|                  (src/azure_web.js)                         |
|   - Real-time message card                                  |
|   - Live connection state (CONNECTED / DISCONNECTED)        |
|   - Localized event timestamp                               |
+-------------------------------------------------------------+
```

---

## 📁 Project Structure

```
azure_web/
├── backend 
|   |server.py             # Flask backend: Azure Event Hub consumer & REST API
├── package.json           # React frontend dependencies and scripts
├── public/                # Static assets (HTML template, icons)
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── azure_web.js       # Main React telemetry dashboard (replaces App.js)
│   ├── index.js           # React entry point mounting AzureWeb component
│   ├── App.css            # Component styles
│   ├── index.css          # Global typography and base styles
│   └── setupTests.js      # Testing configuration
└── README.md              # Project documentation and roadmap
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python**: Version 3.9 or higher
- **Node.js**: Version 18 or higher (with `npm`)
- **Azure IoT Hub**: Active Azure subscription with IoT Hub and Event Hub connection string.

### 2. Backend Setup (`server.py`)

1. Install required Python packages:
   ```bash
   pip install flask flask-cors azure-eventhub
   ```

2. Verify or update Azure connection settings in `server.py`:
   - `CONNECTION_STRING`: Azure Event Hub-compatible connection string.
   - `CONSUMER_GROUP`: Default consumer group (`$default`).

3. Start the Flask backend:
   ```bash
   python3 server.py
   ```
   The backend will start on `http://127.0.0.1:8000` and begin listening for telemetry from Azure Event Hubs.

### 3. Frontend Setup (`azure_web.js`)

1. Install npm dependencies (if not already installed):
   ```bash
   npm install
   ```

2. Launch the React development server:
   ```bash
   npm start
   ```
   The web application will open at `http://localhost:3000`.

---

## 📡 API Reference

| Endpoint | Method | Description | Example Response |
| :--- | :--- | :--- | :--- |
| `/api/latest` | `GET` | Returns the latest received telemetry message and UTC timestamp | `{"message": "Hello World", "timestamp": "2026-10-11T15:20:00Z"}` |
| `/health` | `GET` | Health check probe | `{"status": "ok"}` |

---

