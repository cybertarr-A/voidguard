import React from "react";

export type Alert = {
  id: number | string;
  agent_id: string;
  ip_address: string;
  risk_score: number;
  action_taken: "ALLOW" | "ALERT" | "BLOCK" | string;
  reason: string;
  created_at: string;
};

interface ThreatStreamProps {
  alerts: Alert[];
}

export function ThreatStream({ alerts }: ThreatStreamProps) {
  return (
    <div className="glass-panel p-6 flex flex-col h-full">
      <h2 className="text-xl font-bold mb-4 neon-text-blue uppercase tracking-wider">Live Threat Stream</h2>
      
      <div className="overflow-auto flex-1 pr-2">
        {alerts.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">No alerts detected...</div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => {
              const isBlock = alert.action_taken === "BLOCK";
              const isAlert = alert.action_taken === "ALERT";
              
              let bgColor = "bg-gray-800/50";
              let badgeColor = "bg-green-500/20 text-green-400 border-green-500/30";
              
              if (isBlock) {
                bgColor = "bg-red-900/20 border border-red-500/20";
                badgeColor = "bg-red-500/20 text-red-400 border-red-500/30";
              } else if (isAlert) {
                bgColor = "bg-yellow-900/20 border border-yellow-500/20";
                badgeColor = "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
              }

              return (
                <div key={alert.id} className={`p-4 rounded-md transition-all duration-300 ${bgColor} animate-in fade-in slide-in-from-right-4`}>
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 text-xs font-mono uppercase tracking-wider border rounded ${badgeColor}`}>
                        {alert.action_taken}
                      </span>
                      <span className="font-mono text-sm text-gray-300">{alert.ip_address}</span>
                    </div>
                    <span className="text-xs text-gray-500">{new Date(alert.created_at).toLocaleTimeString()}</span>
                  </div>
                  
                  <div className="mt-2 flex items-center justify-between">
                    <p className="text-sm text-gray-400 font-mono flex-1">{alert.reason}</p>
                    <div className="flex items-center gap-2 ml-4">
                      <span className="text-xs text-gray-500">RISK</span>
                      <span className={`font-bold ${isBlock ? "text-red-500" : isAlert ? "text-yellow-500" : "text-green-500"}`}>
                        {Math.round(alert.risk_score)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
