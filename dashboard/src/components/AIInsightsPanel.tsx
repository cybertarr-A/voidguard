import React from "react";

interface AIInsightsPanelProps {
  explanation: string | null;
}

export function AIInsightsPanel({ explanation }: AIInsightsPanelProps) {
  return (
    <div className="glass-panel p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse-glow" />
        <h2 className="text-xl font-bold uppercase tracking-wider text-purple-400" style={{textShadow: "0 0 5px rgba(178,0,255,0.5)"}}>
          AI Analysis
        </h2>
      </div>
      
      {explanation ? (
        <div className="bg-purple-900/10 border border-purple-500/20 rounded p-4">
          <p className="text-gray-300 leading-relaxed font-mono text-sm whitespace-pre-wrap">
            {explanation}
          </p>
        </div>
      ) : (
        <div className="text-center text-gray-500 mt-4 italic font-mono text-sm">
          Awaiting target analysis...
        </div>
      )}
    </div>
  );
}
