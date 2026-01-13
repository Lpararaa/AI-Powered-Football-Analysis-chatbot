"use client";
import React from "react";
import Image from "next/image";

export default function TopBar() {
  const toggle = () => {
    const root = document.documentElement;
    if (root.classList.contains("dark")) {
      root.classList.remove("dark");
      localStorage.setItem("theme","light");
    } else {
      root.classList.add("dark");
      localStorage.setItem("theme","dark");
    }
  };

  return (
    <div className="topbar glass">
      <div className="flex items-center gap-3">
        <Image src="/Premier_League_logo.svg" alt="PL" width={36} height={36} className="object-contain invert dark:invert-0"/>
        <div>
          <div className="text-lg font-semibold">Premier League AI</div>
          <div className="text-xs small-muted">Stats • Insights • Predictions</div>
        </div>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <div className="small-muted text-sm">Model: Gemini 2.5</div>
        <button onClick={toggle} className="p-2 rounded-md hover:bg-avpGlass transition">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="5" stroke="white" strokeOpacity="0.8"/></svg>
        </button>
      </div>
    </div>
  );
}
