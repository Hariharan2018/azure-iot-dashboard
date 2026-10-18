
import { useEffect, useState } from "react";

// Flask backend runs on port 5000
const API_URL = "http://127.0.0.1:5000/api/latest";

// Update these with your actual details
const STUDENT_NAME = "HARIHARAN S";
const ROLL_NUMBER = "24EIR037";

export default function AzureWeb() {
  const [data, setData] = useState({
    ascii_values: null,
    message: "Waiting for Azure telemetry...",
    timestamp: null,
    azure_connected: false,
    last_error: null,
  });

  const [status, setStatus] = useState("CONNECTING");

  useEffect(() => {
    let active = true;

    async function fetchTelemetry() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error("Backend request failed");
        }

        const result = await response.json();

        if (active) {
          setData(result);

          // Use the backend's status instead of assuming that
          // every successful HTTP response means Azure is connected.
          setStatus(
            result.azure_connected ? "CONNECTED" : "WAITING"
          );
        }
      } catch (error) {
        if (active) {
          setStatus("DISCONNECTED");
        }
      }
    }

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 2000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const statusColor =
    status === "CONNECTED"
      ? "#6ee7a0"
      : status === "WAITING" || status === "CONNECTING"
      ? "#facc15"
      : "#fb7185";

  const asciiText =
    Array.isArray(data.ascii_values)
      ? data.ascii_values.join(", ")
      : "No ASCII values received";

  return (
    <main style={styles.page}>
      <div style={styles.container}>
        <header>
          <p style={styles.eyebrow}>TELEMETRY MONITORING SYSTEM</p>
          <h1 style={styles.title}>Azure IoT Hub</h1>
          <p style={styles.subtitle}>
            Live messages received from Azure
          </p>
        </header>

        <section style={styles.panel}>
          <div style={styles.studentGrid}>
            <div>
              <p style={styles.label}>STUDENT NAME</p>
              <p style={styles.value}>{STUDENT_NAME}</p>
            </div>
            <div>
              <p style={styles.label}>ROLL NUMBER</p>
              <p style={styles.value}>{ROLL_NUMBER}</p>
            </div>
          </div>

          <div style={styles.divider} />

          <div style={styles.panelHeader}>
            <span style={styles.label}>CONNECTION STATUS</span>
            <span style={{ ...styles.status, color: statusColor }}>
              ● {status}
            </span>
          </div>

          <div style={styles.divider} />

          <p style={styles.label}>RECEIVED ASCII VALUES</p>
          <pre style={styles.ascii}>{asciiText}</pre>

          <div style={styles.divider} />

          <p style={styles.label}>CONVERTED STRING</p>
          <pre style={styles.message}>{data.message}</pre>

          <div style={styles.divider} />

          <div style={styles.footer}>
            <span style={styles.label}>LAST EVENT TIMESTAMP</span>
            <span style={styles.timestamp}>
              {data.timestamp
                ? new Date(data.timestamp).toLocaleString()
                : "No events received"}
            </span>
          </div>

          {data.last_error && (
            <p style={styles.error}>
              Backend error: {data.last_error}
            </p>
          )}
        </section>

        <p style={styles.note}>
          Azure IoT Hub → Event Hubs Endpoint → Flask → React
        </p>
      </div>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    width: "100%",
    boxSizing: "border-box",
    background: "#050505",
    color: "#f5f5f5",
    fontFamily: "monospace",
    padding: "48px 24px",
  },
  container: {
    width: "100%",
    maxWidth: "900px",
    margin: "0 auto",
  },
  eyebrow: {
    color: "#777",
    fontSize: "12px",
    letterSpacing: "3px",
  },
  title: {
    fontSize: "clamp(28px, 5vw, 44px)",
    fontWeight: 600,
    margin: "18px 0 10px",
  },
  subtitle: {
    color: "#999",
    fontSize: "14px",
  },
  panel: {
    marginTop: "40px",
    padding: "28px",
    background: "#101010",
    border: "1px solid #292929",
    borderRadius: "12px",
  },
  studentGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "20px",
  },
  value: {
    color: "#f5f5f5",
    fontSize: "15px",
    overflowWrap: "anywhere",
  },
  panelHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "12px",
  },
  label: {
    color: "#888",
    fontSize: "11px",
    letterSpacing: "1.5px",
  },
  status: {
    fontSize: "12px",
    fontWeight: 600,
  },
  divider: {
    height: "1px",
    background: "#292929",
    margin: "24px 0",
  },
  ascii: {
    whiteSpace: "pre-wrap",
    overflowWrap: "anywhere",
    color: "#93c5fd",
    fontSize: "14px",
    lineHeight: 1.8,
  },
  message: {
    minHeight: "40px",
    whiteSpace: "pre-wrap",
    overflowWrap: "anywhere",
    color: "#6ee7a0",
    fontSize: "clamp(18px, 3vw, 24px)",
    lineHeight: 1.7,
    fontFamily: "monospace",
  },
  footer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    flexWrap: "wrap",
    gap: "12px",
  },
  timestamp: {
    color: "#bbb",
    fontSize: "12px",
  },
  error: {
    color: "#fb7185",
    fontSize: "12px",
    overflowWrap: "anywhere",
  },
  note: {
    textAlign: "center",
    color: "#555",
    fontSize: "11px",
    marginTop: "24px",
  },
};
