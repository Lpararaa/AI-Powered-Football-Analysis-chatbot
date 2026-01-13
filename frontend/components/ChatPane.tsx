"use client";
import React, { useState } from "react";

export default function ChatPane() {
  const [input, setInput] = useState("");

  const onSend = () => {
    if (!input) return;
    // placeholder behaviour: in real app send to your API
    console.log("send:", input);
    setInput("");
  };

  return (
    <div className="chat-wrap">
      <h2 className="text-2xl font-semibold mb-4">Scout Chat</h2>

      <div className="chat-window glass flex flex-col">
        {/* Example assistant message */}
        <div className="bubble assistant max-w-[60%]">
          <div className="text-sm">
            Ask about players, matches, xG or tactical reports.<br />
            Try: <span className="kv">"Compare Haaland vs Palmer"</span>
          </div>
        </div>

        {/* spacer for scrollable area */}
        <div style={{flex:1}} />

        {/* input */}
        <div className="chat-input">
          <input
            value={input}
            onChange={(e)=>setInput(e.target.value)}
            placeholder="Ask about players, matches or tactics..."
            className="inputbox"
            onKeyDown={(e) => { if (e.key === "Enter") onSend(); }}
          />
          <button onClick={onSend} className="px-4 py-3 rounded-lg bg-avpAccent text-white hover:opacity-95 transition">Send</button>
        </div>
      </div>
    </div>
  );
}
