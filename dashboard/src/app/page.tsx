"use client";

import { FormEvent, useEffect, useMemo, useState, useRef } from "react";
import { ThreatStream, Alert } from "../components/ThreatStream";
import { RiskGraph } from "../components/RiskGraph";
import Link from "next/link";

type HealthState = "checking" | "online" | "offline";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";
const WS_URL = API_URL.replace("http", "ws");

export default function Home() {
  const [health, setHealth] = useState<HealthState>("checking");
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

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

  // Setup WebSocket connection when token is available
  useEffect(() => {
    if (!token) return;

    function connectWs() {
      const ws = new WebSocket(`${WS_URL}/api/v1/ws/alerts`);
      
      ws.onopen = () => {
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Add new alert to the top of the list
          setAlerts(prev => [data, ...prev].slice(0, 100)); // keep last 100
        } catch (e) {
          console.error("Failed to parse websocket message", e);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 5s...");
        setTimeout(connectWs, 5000);
      };

      wsRef.current = ws;
    }

    connectWs();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token]);

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
        throw new Error("Login failed. Check credentials.");
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
    <div className="flex-1 flex flex-col p-6 max-w-[1600px] mx-auto w-full gap-6">
      <header className="flex justify-between items-center glass-panel p-4">
        <div className="flex items-center gap-6">
          <div className="font-bold text-2xl tracking-widest flex items-center gap-2">
            <span className="text-neon-blue">VOID</span>
            <span className="text-white">GUARD</span>
            <span className="text-xs ml-2 px-2 py-0.5 bg-blue-900/50 text-blue-400 border border-blue-500/30 rounded font-mono">SOC</span>
          </div>
          
          <nav className="flex gap-4">
            <Link href="/" className="text-neon-blue font-bold px-3 py-1 border-b-2 border-neon-blue">
              DASHBOARD
            </Link>
            <Link href="/scan" className="text-gray-400 hover:text-neon-blue px-3 py-1 transition-colors">
              SCANNER
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-mono">
            <span>SYS_HEALTH:</span>
            <span className={health === "online" ? "text-neon-green font-bold" : "text-neon-red font-bold"}>
              {health.toUpperCase()}
            </span>
          </div>
          
          {!token ? (
            <form onSubmit={handleLogin} className="flex gap-2">
              <input
                type="text"
                placeholder="Username"
                className="input-cyber text-sm py-1"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <input
                type="password"
                placeholder="Password"
                className="input-cyber text-sm py-1"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button type="submit" className="btn-cyber text-sm py-1" disabled={isLoading}>
                AUTH
              </button>
            </form>
          ) : (
            <div className="flex items-center gap-2 text-sm text-green-400 border border-green-500/30 bg-green-900/20 px-3 py-1 rounded">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              AUTH_ESTABLISHED
            </div>
          )}
        </div>
      </header>

      {message && (
        <div className="glass-panel p-4 text-neon-red border-red-500 text-center font-mono animate-pulse">
          {message}
        </div>
      )}

      {token ? (
        <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
          <div className="lg:col-span-2 h-[calc(100vh-140px)]">
            <ThreatStream alerts={alerts} />
          </div>
          
          <div className="flex flex-col gap-6 h-[calc(100vh-140px)]">
            <div className="h-1/3">
              <RiskGraph averageRisk={stats.averageRisk} totalAlerts={stats.total} />
            </div>
            
            <div className="glass-panel p-6 flex-1 flex flex-col">
              <h2 className="text-xl font-bold mb-4 neon-text-blue uppercase tracking-wider">Metrics</h2>
              <div className="flex-1 flex flex-col justify-center space-y-4">
                <div className="flex justify-between items-center p-3 border border-red-500/20 bg-red-900/10 rounded">
                  <span className="font-mono text-gray-400">BLOCKED</span>
                  <span className="text-2xl font-bold text-red-500">{stats.blocked}</span>
                </div>
                <div className="flex justify-between items-center p-3 border border-yellow-500/20 bg-yellow-900/10 rounded">
                  <span className="font-mono text-gray-400">SUSPICIOUS</span>
                  <span className="text-2xl font-bold text-yellow-500">{stats.suspicious}</span>
                </div>
                <div className="flex justify-between items-center p-3 border border-green-500/20 bg-green-900/10 rounded">
                  <span className="font-mono text-gray-400">ALLOWED</span>
                  <span className="text-2xl font-bold text-green-500">{stats.allowed}</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="glass-panel p-10 text-center max-w-md">
            <div className="text-4xl mb-4">🔒</div>
            <h2 className="text-2xl font-bold mb-2 neon-text-blue tracking-wider uppercase">Authentication Required</h2>
            <p className="text-gray-400 font-mono text-sm">Please authenticate to access the Security Operations Center command console.</p>
          </div>
        </div>
      )}
    </div>
  );
}
