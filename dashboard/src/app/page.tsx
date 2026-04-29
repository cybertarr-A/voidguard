"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Alert = {
  id: number;
  agent_id: string;
  ip_address: string;
  risk_score: number;
  action_taken: "ALLOW" | "ALERT" | "BLOCK" | string;
  reason: string;
  created_at: string;
};

type HealthState = "checking" | "online" | "offline";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

function actionClass(action: string) {
  return action.toLowerCase();
}

function riskColor(score: number) {
  if (score >= 75) return "var(--status-block)";
  if (score >= 40) return "var(--status-alert)";
  return "var(--status-allow)";
}

export default function Home() {
  const [health, setHealth] = useState<HealthState>("checking");
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const stats = useMemo(() => {
    const blocked = alerts.filter((alert) => alert.action_taken === "BLOCK").length;
    const suspicious = alerts.filter((alert) => alert.action_taken === "ALERT").length;
    const allowed = alerts.filter((alert) => alert.action_taken === "ALLOW").length;
    const averageRisk =
      alerts.length === 0
        ? 0
        : Math.round(
            alerts.reduce((total, alert) => total + alert.risk_score, 0) /
              alerts.length,
          );

    return { allowed, averageRisk, blocked, suspicious, total: alerts.length };
  }, [alerts]);

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
        setHealth(response.ok ? "online" : "offline");
      } catch {
        setHealth("offline");
      }
    }

    checkHealth();
    const id = window.setInterval(checkHealth, 10000);
    return () => window.clearInterval(id);
  }, []);

  async function loadAlerts(activeToken = token) {
    if (!activeToken) return;

    setIsLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/v1/alerts/`, {
        headers: {
          Authorization: `Bearer ${activeToken}`,
        },
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`Alert request failed with ${response.status}`);
      }

      setAlerts((await response.json()) as Alert[]);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to load alerts");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setMessage("");

    try {
      const formData = new URLSearchParams();
      formData.set("username", username);
      formData.set("password", password);

      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const data = (await response.json()) as { access_token: string };
      setToken(data.access_token);
      await loadAlerts(data.access_token);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="dashboard-layout">
      <header className="topbar">
        <div className="logo">
          <span className="logo-icon" />
          VOIDGUARD
        </div>
        <div className={`system-state ${health}`}>
          <span />
          {health === "checking" ? "Checking" : health}
        </div>
      </header>

      <main className="main-content">
        <section className="command-strip">
          <div>
            <h1>Security Operations</h1>
            <p>Telemetry intake, risk scoring, and autonomous response status.</p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            <input
              aria-label="Username"
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Username"
              type="text"
              value={username}
            />
            <input
              aria-label="Password"
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
              type="password"
              value={password}
            />
            <button disabled={isLoading} type="submit">
              {token ? "Refresh" : "Login"}
            </button>
          </form>
        </section>

        {message ? <div className="notice">{message}</div> : null}

        <section className="grid-container">
          <div className="panel">
            <div className="panel-header">Total alerts</div>
            <div className="stat-value stat-glow">{stats.total}</div>
          </div>
          <div className="panel">
            <div className="panel-header">Blocked</div>
            <div className="stat-value danger">{stats.blocked}</div>
          </div>
          <div className="panel">
            <div className="panel-header">Suspicious</div>
            <div className="stat-value warning">{stats.suspicious}</div>
          </div>
          <div className="panel">
            <div className="panel-header">Average risk</div>
            <div className="stat-value">{stats.averageRisk}</div>
          </div>
        </section>

        <section className="panel alerts-panel">
          <div className="table-header">
            <div>
              <div className="panel-header">Recent decisions</div>
              <h2>Threat Activity</h2>
            </div>
            <button disabled={!token || isLoading} onClick={() => loadAlerts()} type="button">
              Reload
            </button>
          </div>

          <div className="table-wrap">
            <table className="alerts-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Risk</th>
                  <th>IP address</th>
                  <th>Agent</th>
                  <th>Reason</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td>
                      <span className={`badge ${actionClass(alert.action_taken)}`}>
                        {alert.action_taken}
                      </span>
                    </td>
                    <td>
                      <strong>{Math.round(alert.risk_score)}</strong>
                      <div className="risk-bar">
                        <div
                          className="risk-fill"
                          style={{
                            background: riskColor(alert.risk_score),
                            width: `${Math.min(alert.risk_score, 100)}%`,
                          }}
                        />
                      </div>
                    </td>
                    <td>{alert.ip_address}</td>
                    <td className="mono">{alert.agent_id}</td>
                    <td>{alert.reason}</td>
                    <td>{new Date(alert.created_at).toLocaleString()}</td>
                  </tr>
                ))}
                {alerts.length === 0 ? (
                  <tr>
                    <td className="empty-state" colSpan={6}>
                      Login, keep the client container running, then refresh alerts.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
