import React, { useState } from "react";
import { SourceChunk } from "../lib/api";

interface SourceChipsProps {
  sources: SourceChunk[];
}

export default function SourceChips({ sources }: SourceChipsProps) {
  const [tooltip, setTooltip] = useState<string | null>(null);

  if (!sources || sources.length === 0) return null;

  // Deduplicate by filename
  const unique = sources.filter(
    (s, i, arr) => arr.findIndex((x) => x.filename === s.filename) === i
  );

  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      <span className="text-xs text-slate-400 self-center">Sources:</span>
      {unique.map((source, idx) => (
        <div key={idx} className="relative group">
          <button
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-medium transition-colors duration-150 border border-slate-200"
            onMouseEnter={() => setTooltip(`${source.filename}-${idx}`)}
            onMouseLeave={() => setTooltip(null)}
            aria-label={`Source: ${source.filename}`}
          >
            <span>📄</span>
            <span className="max-w-[140px] truncate">{source.filename}</span>
          </button>

          {/* Tooltip */}
          {tooltip === `${source.filename}-${idx}` && source.chunk_preview && (
            <div className="absolute bottom-full left-0 mb-1 z-50 w-64 p-2 bg-slate-800 text-white text-xs rounded-lg shadow-lg pointer-events-none animate-fade-in">
              <p className="font-medium mb-1 text-slate-300">{source.filename}</p>
              <p className="text-slate-400 leading-relaxed">
                {source.chunk_preview.length > 120
                  ? source.chunk_preview.substring(0, 120) + "..."
                  : source.chunk_preview}
              </p>
              {source.distance !== undefined && (
                <p className="mt-1 text-slate-500">
                  Relevance: {((1 - source.distance) * 100).toFixed(0)}%
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
