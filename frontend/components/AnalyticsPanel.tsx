"use client";
import React from "react";

const Sparkline = ({ values=[1,3,2,5,6,7] }: { values?: number[] })=>{
  const w=120, h=36; const max=Math.max(...values); const step = w/(values.length-1);
  const pts = values.map((v,i)=>`${i*step},${h - (v/max)*h}`).join(" ");
  return <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none"><polyline points={pts} stroke="#34D399" strokeWidth="2" fill="none"/></svg>;
};

export default function AnalyticsPanel(){
  return (
    <aside className="analytics-panel glass p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs small-muted">Overview</div>
          <div className="font-semibold text-white">Match & Player KPIs</div>
        </div>
        <div className="text-xs small-muted">Live</div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-md border border-white/4">
          <div className="kpi-title">Top Scorer</div>
          <div className="kpi-value">Haaland</div>
          <div className="text-xs small-muted">27 goals</div>
        </div>
        <div className="p-3 rounded-md border border-white/4">
          <div className="kpi-title">Top Creator</div>
          <div className="kpi-value">Cole Palmer</div>
          <div className="text-xs small-muted">22 goals • 11 assists</div>
        </div>
      </div>

      <div className="p-3 rounded-md border border-white/4 flex items-center justify-between">
        <div>
          <div className="text-xs small-muted">Team Momentum</div>
          <div className="font-medium">Manchester City</div>
        </div>
        <Sparkline values={[1,2,3,2,4,6,8]} />
      </div>

      <div className="p-3 rounded-md border border-white/4">
        <div className="text-xs small-muted mb-2">Recent Matches</div>
        <table className="w-full text-sm">
          <tbody>
            <tr className="border-t border-white/6"><td>City vs Chelsea</td><td className="text-right">1-1</td></tr>
            <tr className="border-t border-white/6"><td>Chelsea vs City</td><td className="text-right">4-4</td></tr>
            <tr className="border-t border-white/6"><td>Arsenal vs ManU</td><td className="text-right">2-0</td></tr>
          </tbody>
        </table>
      </div>

      <div className="mt-auto text-xs small-muted">DB: <span className="text-cyan-300">Neo4j</span> • Model: <span className="text-emerald-300">Gemini 2.5</span></div>
    </aside>
  );
}
