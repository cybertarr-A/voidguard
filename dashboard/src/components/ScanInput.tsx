import React, { useState } from "react";

interface ScanInputProps {
  onScan: (url: string, scanType: string, depth: number) => void;
  isLoading: boolean;
}

export function ScanInput({ onScan, isLoading }: ScanInputProps) {
  const [url, setUrl] = useState("");
  const [scanType, setScanType] = useState("PASSIVE");
  const [depth, setDepth] = useState(1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url) {
      onScan(url, scanType, depth);
    }
  };

  return (
    <div className="glass-panel p-6">
      <h2 className="text-xl font-bold mb-4 neon-text-blue uppercase tracking-wider">Target Acquisition</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-mono text-gray-400 mb-1">TARGET URL</label>
          <input
            type="url"
            required
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="input-cyber w-full"
            disabled={isLoading}
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-1">SCAN TYPE</label>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="input-cyber w-full"
              disabled={isLoading}
            >
              <option value="PASSIVE">PASSIVE (Recon Only)</option>
              <option value="ACTIVE">ACTIVE (Payload Injection)</option>
              <option value="AI">AI (Cognitive Analysis)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-1">CRAWL DEPTH</label>
            <input
              type="number"
              min="1"
              max="3"
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="input-cyber w-full"
              disabled={isLoading}
            />
          </div>
        </div>

        <button 
          type="submit" 
          className="btn-cyber w-full mt-4"
          disabled={isLoading || !url}
        >
          {isLoading ? (
            <span className="animate-pulse">INITIALIZING SCAN...</span>
          ) : (
            "ENGAGE TARGET"
          )}
        </button>
      </form>
    </div>
  );
}
