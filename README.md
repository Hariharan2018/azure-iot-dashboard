Azure IoT Dashboard

A full-stack demonstration that receives telemetry from Azure IoT Hub, consumes events through the IoT Hub Event Hubs-compatible endpoint, converts the received text message into ASCII codes, and displays the result in a React dashboard.

Live Demo

Frontend (Render Static Site): https://azure-iot-dashboard-1.onrender.com/

Backend API (Render Web Service): https://azure-iot-dashboard.onrender.com/

Latest telemetry endpoint: https://azure-iot-dashboard.onrender.com/api/latest

Health endpoint: https://azure-iot-dashboard.onrender.com/health

Deployment URLs were recorded during deployment on October 18, 2026. If a service URL changes in Render, update this section.

Features

Receives events from Azure IoT Hub through its Event Hubs-compatible endpoint.

Consumes messages using Azure Event Hubs client libraries.

Decodes message content as text and calculates the ASCII code for each character.

Exposes the latest message and status through a Flask REST API.

Displays backend data in a React frontend.

Deploys the frontend and backend as separate Render services.

Keeps connection credentials in environment variables rather than source code.

Architecture

flowchart LR
    A["Telemetry source / device"] -->|"Message"| B["Azure IoT Hub"]
    B -->|"Event Hubs-compatible endpoint"| C["Python EventHubConsumerClient"]
    C --> D["Flask backend"]
    D --> E["Decode message and convert each character to ASCII"]
    E --> F["GET /api/latest"]
    F -->|"HTTPS JSON"| G["React dashboard"]
    G --> H["Render Static Site"]
    D --> I["Render Python Web Service"]

The Event Hubs consumer receives messages from the IoT Hub built-in endpoint. The backend keeps the latest received message and its ASCII values in application memory and returns them from /api/latest. This is a latest-message demo, not a persistent telemetry database.

Technology Stack

Layer

Technology

IoT ingestion

Azure IoT Hub

Event consumption

Azure Event Hubs-compatible endpoint, azure-eventhub Python package

Backend API

Python, Flask, Flask-CORS

Frontend

React (Create React App / react-scripts)

Hosting

Render Web Service and Render Static Site

Configuration

Environment variables; local .env file for development

Repository Structure

The repository is organized around a Python backend and a React frontend. The exact files may evolve; the important entry points are:

azure-iot-dashboard/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env                 # local only; must not be committed
├── src/
│   └── azure_web.js         # React dashboard / API polling
├── public/
├── package.json
├── .gitignore
└── README.md

Data Flow

A device or test producer sends a message to Azure IoT Hub.

The backend connects to the IoT Hub Event Hubs-compatible endpoint using EventHubConsumerClient.

The consumer receives an event and decodes its body as text.

Each character is converted to its ASCII/Unicode code point for the message used in this demo. For the current sample message, all characters are ASCII.

Flask stores the most recently received message, values, timestamp, and connection/error status in process memory.

The React frontend polls GET /api/latest and renders the returned JSON.

Example message: one_credit_course_project

Example ASCII result:

{
  "message": "one_credit_course_project",
  "ascii_values": [111, 110, 101, 95, 99, 114, 101, 100, 105, 116, 95, 99, 111, 117, 114, 115, 101, 95, 112, 114, 111, 106, 101, 99, 116],
  "azure_connected": true,
  "last_error": null
}

The exact response may also include a timestamp and other status fields.

Run Locally

Prerequisites

Python installed

Node.js and npm installed

Azure IoT Hub configured to receive messages

An Event Hubs-compatible endpoint connection string and the relevant event hub name, if required by the code

1. Configure the backend

Open a terminal at the repository root:

cd backend
python -m venv .venv

Activate the environment on Windows:

.venv\Scripts\Activate.ps1

Install Python packages:

pip install -r requirements.txt

Create backend/.env locally and add the Azure Event Hubs-compatible connection string, event hub name (if your code expects a separate value), and consumer group using the exact environment-variable names referenced by backend/server.py. Do not commit .env or paste connection strings into issues or screenshots.

Run the API:

python server.py

The backend uses Render's PORT variable when deployed. Locally, it typically uses port 5000.

2. Configure and run the frontend

Open a second terminal at the repository root:

npm install

In src/azure_web.js, make sure the API base URL points to the intended environment.

For local backend testing:

http://127.0.0.1:5000/api/latest

For the deployed backend:

https://azure-iot-dashboard.onrender.com/api/latest

Run the React development server:

npm start

Create React App typically opens at http://localhost:3000.

API

GET /api/latest

Returns the latest message and its decoded ASCII values, plus status information.

Example fields:

Field

Meaning

message

Most recently received text message

ascii_values

Array containing the code for each character

timestamp

Time associated with the latest received message, when available

azure_connected

Backend's current connection/status indicator

last_error

Most recent recorded error, or null

GET /health

Health/status endpoint for checking whether the Flask service responds. A successful HTTP response does not by itself prove that a new Azure message has arrived; check /api/latest as well.

Render Deployment

The project uses two separate Render services.

Backend — Web Service

Service URL: https://azure-iot-dashboard.onrender.com

Root Directory: backend

Build Command: pip install -r requirements.txt

Start Command: python server.py

Required configuration: Azure Event Hubs-compatible connection details and consumer group, named exactly as expected by server.py.

CORS: Allow the deployed frontend origin: https://azure-iot-dashboard-1.onrender.com.

Frontend — Static Site

Service URL: https://azure-iot-dashboard-1.onrender.com/

Build Command: npm install && npm run build

Publish Directory: build (this project uses Create React App, not Vite's dist directory)

API URL: https://azure-iot-dashboard.onrender.com/api/latest

The Flask CORS configuration must allow the exact frontend origin. If the code uses a FRONTEND_ORIGIN environment variable, set it in the backend Web Service's Environment page, not the Static Site. The code must read this variable for it to have an effect.

Environment Variables and Secrets

Never commit .env files, Azure connection strings, shared-access keys, or credentials.

Keep local credentials in backend/.env; make sure .env is ignored by Git.

Add deployment secrets in Render → backend Web Service → Environment.

Use the exact variable names read by backend/server.py. Do not guess variable names from this README.

The frontend should contain only the public backend API URL. Do not put Azure connection strings or backend secrets in React source or variables exposed to the browser.

Keep FRONTEND_ORIGIN set to https://azure-iot-dashboard-1.onrender.com if the backend code uses it for CORS.

Use the consumer group configured for the application (the deployed setup has used $Default).

Security action required: an Azure connection string was exposed during earlier debugging. Rotate/regenerate the relevant shared-access key in Azure, then update the backend's Render environment variable and local .env. Do not paste the new secret into GitHub or chat.

Recommended .gitignore entries:

# Secrets
.env
.env.*
!.env.example
**/.env
**/.env.*

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node
node_modules/
build/

Review the existing .gitignore before editing so you preserve any project-specific rules. If a secret was committed previously, adding it to .gitignore does not remove it from Git history; rotate the secret first.

Troubleshooting

Frontend says DISCONNECTED: confirm src/azure_web.js uses the deployed backend URL, not 127.0.0.1 or localhost, then redeploy the Static Site.

CORS error: allow https://azure-iot-dashboard-1.onrender.com in Flask CORS and redeploy the backend.

API returns waiting values: inspect backend logs and confirm the Event Hubs consumer receives events.

Publish directory does not exist: for Create React App use build, not dist.

Render starts the wrong command: the current simple deployment uses python server.py; do not switch back to gunicorn server:app unless the receiver thread is moved into the correct Gunicorn worker lifecycle.

No new telemetry: this implementation keeps only the latest message in process memory. It does not provide durable history.

Final Verification Checklist

https://azure-iot-dashboard.onrender.com/api/latest returns valid JSON.

message and ascii_values match the received telemetry.

The frontend at https://azure-iot-dashboard-1.onrender.com/ displays the data.

Browser Console has no 127.0.0.1:5000 request or CORS error.

Backend CORS allows the deployed frontend origin.

.env files and credentials are not tracked by Git.

The previously exposed Azure key has been rotated.

README deployment URLs and commands match the current Render service settings.

License

Add the license required by your course or project. Do not claim an open-source license unless a license file has been added.
