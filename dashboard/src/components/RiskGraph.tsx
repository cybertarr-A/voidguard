import React from "react";

interface RiskGraphProps {
  averageRisk: number;
  totalAlerts: number;
}

export function RiskGraph({ averageRisk, totalAlerts }: RiskGraphProps) {
  // A simple visual representation
  const riskColor = averageRisk >= 75 ? "bg-red-500" : averageRisk >= 40 ? "bg-yellow-500" : "bg-green-500";
  
  return (
    <div className="glass-panel p-6 flex flex-col justify-between">
      <div>
        <h2 className="text-xl font-bold mb-1 neon-text-blue uppercase tracking-wider">System Risk Level</h2>
        <p className="text-xs text-gray-400 font-mono">Aggregated heuristic threat score</p>
      </div>
      
      <div className="flex items-center justify-center my-6">
        <div className="relative flex items-center justify-center w-32 h-32 rounded-full border-4 border-gray-800">
          <div 
            className={`absolute w-full h-full rounded-full opacity-20 animate-pulse ${riskColor}`}
          />
          <div className="text-4xl font-bold text-white z-10" style={{ textShadow: "0 0 10px rgba(255,255,255,0.5)" }}>
            {averageRisk}
          </div>
        </div>
      </div>
      
      <div className="flex justify-between items-end border-t border-gray-800/50 pt-4 mt-auto">
        <div>
          <p className="text-xs text-gray-500 font-mono">TOTAL EVENTS</p>
          <p className="text-lg font-bold text-gray-300">{totalAlerts}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 font-mono">STATUS</p>
          <p className={`text-sm font-bold uppercase tracking-wider ${averageRisk >= 75 ? "text-red-500" : averageRisk >= 40 ? "text-yellow-500" : "text-green-500"}`}>
            {averageRisk >= 75 ? "CRITICAL" : averageRisk >= 40 ? "ELEVATED" : "SECURE"}
          </p>
        </div>
      </div>
    </div>
  );
}
