"use client";
import React from "react";
import Image from "next/image";
import { Home, Plus } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full z-50 flex flex-col bg-[#09090b] border-r border-white/10 transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] w-20 hover:w-[280px] group overflow-hidden shadow-2xl">
      
      {/* --- BRANDING HEADER --- */}
      <div className="h-24 flex items-center shrink-0 border-b border-white/5 whitespace-nowrap">
        
        {/* LOGO CONTAINER */}
        <div className="w-20 h-full flex items-center justify-center shrink-0">
           <div className="relative w-20 h-20"> {/* Adjusted size slightly for better proportion */}
             <Image 
               src="/Premier_league_logo.svg" 
               alt="PL" 
               fill 
               className="invert object-contain" 
             />
           </div>
        </div>
        
        {/* UPDATED TEXT: Aesthetic & Bold */}
        <div className="opacity-0 group-hover:opacity-100 transition-all duration-500 delay-100 pl-2">
           <h1 className="font-extrabold text-xl text-zinc-100 tracking-tighter leading-none select-none">
             Premier League
           </h1>
           {/* Optional: Subtle sub-text for extra 'Pro' feel */}
           <p className="text-[10px] font-medium text-zinc-500 uppercase tracking-widest mt-0.5">
             Official Data
           </p>
        </div>
      </div>

      {/* --- ACTION BUTTON --- */}
      <div className="p-4 shrink-0">
        <button className="flex items-center justify-center w-full h-12 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 transition-all group-hover:justify-start group-hover:px-4 relative overflow-hidden">
          <Plus size={24} className="text-white shrink-0" />
          <span className="ml-3 text-sm font-medium text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap absolute left-12">New Chat</span>
        </button>
      </div>

      {/* --- NAVIGATION --- */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden py-2 px-0 space-y-2 scrollbar-hide">
        <NavItem icon={<Home size={24}/>} label="Home" active />
      </div>

      {/* --- FOOTER / PROFILE --- */}
      <div className="p-0 border-t border-white/5 bg-zinc-900/50 whitespace-nowrap">
        <button className="flex items-center w-full h-20 transition-colors group/profile">
          
          {/* Avatar Container: Centered in w-20 */}
          <div className="w-20 flex justify-center shrink-0">
            <div className="w-10 h-10 rounded-full bg-linear-to-tr from-purple-600 to-blue-600 p-0.5">
              <div className="w-full h-full rounded-full bg-black flex items-center justify-center text-xs font-bold text-white">
                JM
              </div>
            </div>
          </div>

          {/* User Details */}
          <div className="text-left opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
            <div className="text-sm font-medium text-white group-hover/profile:text-purple-300 transition-colors">Judha M.</div>
            <div className="text-xs text-zinc-500">Pro Scout</div>
          </div>
        </button>
      </div>
    </aside>
  );
}

// --- Nav Item Helper ---
function NavItem({ icon, label, active = false }: { icon: any, label: string, active?: boolean }) {
  return (
    <button className={`relative flex items-center h-14 w-full transition-all duration-200 group/item overflow-hidden
      ${active ? 'text-white' : 'text-zinc-400 hover:text-white'}
    `}>
      {/* Active Indicator Line */}
      {active && (
         <div className="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-1 bg-purple-500 rounded-r-full" />
      )}

      {/* ICON CONTAINER: w-20 (80px) to match sidebar width */}
      <div className="w-20 h-full flex items-center justify-center shrink-0 z-10">
        <div className={`p-2 rounded-xl transition-all duration-200 ${active ? 'bg-white/10' : 'group-hover/item:bg-white/5'}`}>
          {icon}
        </div>
      </div>

      {/* Label */}
      <span className="text-[15px] font-medium opacity-0 group-hover:opacity-100 transition-all duration-300 whitespace-nowrap">
        {label}
      </span>
    </button>
  )
}