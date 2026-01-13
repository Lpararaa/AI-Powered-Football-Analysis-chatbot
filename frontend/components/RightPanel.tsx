"use client";
import React from "react";

const Sparkline = ({ values=[1,3,2,5,4] }: { values?: number[] })=>{
  const w=120,h=36; const max=Math.max(...values); const step = w/(values.length-1);
  const pts = values.map((v,i)=>`${i*step},${h - (v/max)*h}`).join(" ");
  return <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none"><polyline points={pts} stroke="#34D399" strokeWidth="2" fill="none"/></svg>;
};

export default function RightPanel(){
  return (
    <aside className="right-panel glass p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs small-muted">Insights</div>
          <div className="font-semibold">Quick Actions</div>
        </div>
        <div className="text-xs small-muted">Live</div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-md border border-white/5">
          <div className="kpi-title">Top Prompt</div>
          <div className="kpi-value">Player Compare</div>
          <div className="text-xs small-muted">Usage 3.2k</div>
        </div>
        <div className="p-3 rounded-md border border-white/5">
          <div className="kpi-title">Templates</div>
          <div className="kpi-value">Tactical Report</div>
          <div className="text-xs small-muted">Save custom templates</div>
        </div>
      </div>

      <div className="p-3 rounded-md border border-white/5 flex items-center justify-between">
        <div>
          <div className="text-xs small-muted">System Load</div>
          <div className="font-medium">Stable</div>
        </div>
        <Sparkline />
      </div>

      <div className="p-3 rounded-md border border-white/5">
        <div className="text-xs small-muted mb-2">Recent</div>
        <div className="text-sm">Haaland vs Palmer • 12 Nov</div>
        <div className="text-sm mt-2">City Tactics • 17 Feb</div>
      </div>

      <div className="mt-auto text-xs small-muted">Powered by local API</div>
    </aside>
  );
}
