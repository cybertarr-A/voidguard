"use client";

import { useState } from "react";
import Link from "next/link";
import { ScanInput } from "../../components/ScanInput";
import { AIInsightsPanel } from "../../components/AIInsightsPanel";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

type Vulnerability = {
  id: number;
  vuln_type: string;
  severity: string;
  description: string;
  evidence: any;
};

type ScanResult = {
  id: string;
  target_url: string;
  status: string;
  scan_type: string;
  risk_score: number | null;
  ai_explanation: string | null;
  vulnerabilities: Vulnerability[];
};

export default function ScanPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pollScanResult = async (scanId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/v1/scan/${scanId}`);
      if (res.ok) {
        const data = await res.json();
        setScanResult(data);
        if (data.status === "RUNNING") {
          setTimeout(() => pollScanResult(scanId), 3000);
        } else {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
        setError("Failed to fetch scan results.");
      }
    } catch (e) {
      setIsLoading(false);
      setError("Network error while polling.");
    }
  };

  const handleScan = async (url: string, scanType: string, depth: number) => {
    setIsLoading(true);
    setError(null);
    setScanResult(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/scan/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, scan_type: scanType, depth })
      });

      if (!res.ok) throw new Error("Failed to start scan");
      
      const data = await res.json();
      pollScanResult(data.scan_id);
    } catch (e) {
      setIsLoading(false);
      setError(e instanceof Error ? e.message : "Error initiating scan");
    }
  };

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
            <Link href="/" className="text-gray-400 hover:text-neon-blue px-3 py-1 transition-colors">
              DASHBOARD
            </Link>
            <Link href="/scan" className="text-neon-blue font-bold px-3 py-1 border-b-2 border-neon-blue">
              SCANNER
            </Link>
          </nav>
        </div>
      </header>

      {error && (
        <div className="glass-panel p-4 text-neon-red border-red-500 text-center font-mono">
          {error}
        </div>
      )}

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        <div className="flex flex-col gap-6">
          <ScanInput onScan={handleScan} isLoading={isLoading} />
          
          {scanResult && (
            <div className="glass-panel p-6">
              <h2 className="text-xl font-bold mb-4 neon-text-blue uppercase tracking-wider">Scan Summary</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-gray-800 pb-2">
                  <span className="text-gray-400 font-mono text-sm">STATUS</span>
                  <span className={`font-bold ${scanResult.status === 'RUNNING' ? 'text-yellow-500 animate-pulse' : scanResult.status === 'COMPLETED' ? 'text-green-500' : 'text-red-500'}`}>
                    {scanResult.status}
                  </span>
                </div>
                <div className="flex justify-between items-center border-b border-gray-800 pb-2">
                  <span className="text-gray-400 font-mono text-sm">RISK SCORE</span>
                  <span className={`font-bold text-xl ${
                    (scanResult.risk_score || 0) >= 75 ? 'text-red-500' : 
                    (scanResult.risk_score || 0) >= 40 ? 'text-yellow-500' : 'text-green-500'
                  }`}>
                    {scanResult.risk_score !== null ? scanResult.risk_score : "CALCULATING..."}
                  </span>
                </div>
                <div className="flex justify-between items-center border-b border-gray-800 pb-2">
                  <span className="text-gray-400 font-mono text-sm">VULNERABILITIES</span>
                  <span className="font-bold text-white">{scanResult.vulnerabilities.length}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="h-1/3">
            <AIInsightsPanel explanation={scanResult?.ai_explanation || null} />
          </div>
          
          <div className="glass-panel p-6 flex-1 flex flex-col overflow-hidden">
            <h2 className="text-xl font-bold mb-4 neon-text-red uppercase tracking-wider">Vulnerability Findings</h2>
            
            <div className="flex-1 overflow-auto pr-2 space-y-4">
              {!scanResult ? (
                <div className="text-center text-gray-500 mt-10 font-mono text-sm">
                  Waiting for target acquisition...
                </div>
              ) : scanResult.vulnerabilities.length === 0 ? (
                <div className="text-center text-green-500 mt-10 font-mono">
                  {scanResult.status === "RUNNING" ? "Scanning target..." : "No vulnerabilities detected. Target appears secure."}
                </div>
              ) : (
                scanResult.vulnerabilities.map(vuln => (
                  <div key={vuln.id} className="p-4 border rounded bg-gray-900/50 border-gray-800">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="font-bold text-white">{vuln.vuln_type}</h3>
                      <span className={`px-2 py-1 text-xs font-bold rounded ${
                        vuln.severity === 'HIGH' ? 'bg-red-900/50 text-red-400' :
                        vuln.severity === 'MEDIUM' ? 'bg-yellow-900/50 text-yellow-400' :
                        'bg-blue-900/50 text-blue-400'
                      }`}>
                        {vuln.severity}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-3">{vuln.description}</p>
                    <div className="bg-black/50 p-3 rounded overflow-x-auto">
                      <pre className="text-xs text-green-400 font-mono">
                        {JSON.stringify(vuln.evidence, null, 2)}
                      </pre>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
