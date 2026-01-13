"use client";
import React, { useState, useRef, useEffect } from "react";
import Image from "next/image";
import { Send, MoreHorizontal, Sparkles, User, RefreshCw, Zap } from "lucide-react";
import Sidebar from "@/components/Sidebar"; 
import ReactMarkdown from 'react-markdown';

type Message = { role: 'user' | 'assistant'; content: string; };

export default function HomePage() {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [regeneratingIndex, setRegeneratingIndex] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(() => scrollToBottom(), [messages, isLoading]);

  const sendMessage = async (messageText: string, historyOverride?: Message[]) => {
    const history = historyOverride || messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ 
          message: messageText,
          history: history
        }) 
      });
      
      if (!response.ok) throw new Error("API Error");
      
      const data = await response.json();
      return data.response || "No text returned.";
    } catch (error) {
      return "⚠️ API Error. Is backend running?";
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const newUserMsg: Message = { role: 'user', content: inputValue };
    setMessages((prev) => [...prev, newUserMsg]);
    
    const messageToSend = inputValue;
    setInputValue("");
    setIsLoading(true);

    const response = await sendMessage(messageToSend);
    
    setMessages((prev) => [...prev, { 
      role: 'assistant', 
      content: response
    }]);
    setIsLoading(false);
  };

  const handleRegenerate = async (index: number) => {
    const userMessageIndex = index - 1;
    if (userMessageIndex < 0 || messages[userMessageIndex].role !== 'user') return;

    const userMessage = messages[userMessageIndex].content;
    const historyUpToUser = messages.slice(0, userMessageIndex).map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    setRegeneratingIndex(index);
    const newResponse = await sendMessage(userMessage, historyUpToUser);
    
    setMessages((prev) => {
      const updated = [...prev];
      updated[index] = { role: 'assistant', content: newResponse };
      return updated;
    });

    setRegeneratingIndex(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { 
      e.preventDefault(); 
      handleSend(); 
    }
  };

  // Suggested prompts for empty state
  const suggestedPrompts = [
    { icon: "⚽", text: "Who are the top scorers this season?", gradient: "from-purple-600 to-pink-600" },
    { icon: "📊", text: "Compare Haaland vs Salah", gradient: "from-blue-600 to-cyan-600" },
    { icon: "🎯", text: "Analyze Arsenal's tactical approach", gradient: "from-green-600 to-emerald-600" },
    { icon: "🏆", text: "Show me the league standings", gradient: "from-orange-600 to-red-600" },
  ];

  return (
    <div className="h-full flex flex-col bg-[#09090b] text-white relative overflow-hidden">
      
      {/* Premier League Gradient Background Effect */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl animate-pulse [animation-delay:1s]" />
      </div>
      
      {/* SIDEBAR */}
      <Sidebar />

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col h-full pl-20 transition-all duration-300 relative z-10">

        {/* Header with PL Branding */}
        

        {messages.length === 0 ? (
          // --- ENHANCED HERO VIEW ---
          <div className="flex-1 w-full flex flex-col items-center justify-center px-4 relative">
     
     {/* Animated Logo */}
     {/* 3. Added 'flex justify-center' to ensure the wrapper itself is centered */}
     <div className="relative mb-10 flex justify-center items-center">
       <div className="absolute -inset-8 bg-linear-to-r from-purple-600/30 via-pink-600/30 to-purple-600/30 rounded-full blur-3xl animate-pulse"></div>
       <div className="relative w-32 h-32 rounded-full bg-linear-to-br from-purple-900 via-black to-pink-900 border-2 border-purple-500/50 shadow-2xl flex items-center justify-center overflow-hidden">
          <div className="absolute inset-0 bg-linear-to-br from-white/10 to-transparent"></div>
          <div className="relative w-20 h-20 flex items-center justify-center">
            <Image 
              src="/Premier_league_logo.svg" 
              alt="PL Logo" 
              fill 
              className="object-contain invert opacity-90" 
              priority 
            />
          </div>
       </div>
     </div>
             
             {/* Premier League Styled Title */}
             <h1 className="text-5xl md:text-6xl font-black text-white text-center mb-3 tracking-tight">
               <span className="bg-linear-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                 Premier League
               </span>
             </h1>
             <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">AI Scout</h2>
             <p className="text-zinc-400 text-base mb-12 font-medium text-center">Powered by Advanced Analytics • Real-time Stats • Tactical Intelligence</p>

             {/* Suggested Prompts */}
             <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8 w-full max-w-2xl">
               {suggestedPrompts.map((prompt, idx) => (
                 <button
                   key={idx}
                   onClick={() => setInputValue(prompt.text)}
                   className="group relative p-4 rounded-xl bg-zinc-900/50 border border-white/5 hover:border-purple-500/50 transition-all duration-300 text-left overflow-hidden"
                 >
                   <div className={`absolute inset-0 bg-linear-to-r ${prompt.gradient} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
                   <div className="relative flex items-center gap-3">
                     <span className="text-2xl">{prompt.icon}</span>
                     <span className="text-sm text-zinc-300 group-hover:text-white transition-colors">{prompt.text}</span>
                   </div>
                 </button>
               ))}
             </div>

             {/* Enhanced Input */}
             <div className="w-full max-w-2xl bg-linear-to-br from-zinc-900 to-black border-2 border-purple-500/30 rounded-2xl p-1 shadow-2xl relative group focus-within:border-purple-500/60 transition-all">
               <div className="absolute -inset-1 bg-linear-to-r from-purple-600 to-pink-600 rounded-2xl opacity-0 group-focus-within:opacity-20 blur transition-opacity"></div>
               <div className="relative bg-black rounded-xl p-4">
                 <input 
                   type="text" 
                   value={inputValue} 
                   onChange={(e) => setInputValue(e.target.value)} 
                   onKeyDown={handleKeyDown} 
                   className="w-full bg-transparent text-white placeholder:text-zinc-500 text-base px-2 py-2 outline-none font-medium" 
                   placeholder="Ask about players, teams, tactics..." 
                 />
                 <div className="flex justify-end items-center mt-3">
                   <button 
                     onClick={handleSend} 
                     disabled={!inputValue.trim()}
                     className={`px-6 py-2.5 rounded-lg font-bold text-sm transition-all duration-200 ${
                       inputValue.trim() 
                         ? 'bg-linear-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg hover:shadow-purple-500/50 hover:scale-105' 
                         : 'bg-zinc-800 text-zinc-600 cursor-not-allowed'
                     }`}
                   >
                     {inputValue.trim() ? 'Analyze' : 'Enter Query'}
                   </button>
                 </div>
               </div>
             </div>

             {/* Stats Badge */}
             <div className="mt-8 flex items-center gap-6 text-xs text-zinc-500">
               <div className="flex items-center gap-2">
                 <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                 <span>Live Data</span>
               </div>
               <span>•</span>
               <span>380 Matches Analyzed</span>
               <span>•</span>
               <span>2023-24 Season</span>
             </div>
          </div>
        ) : (
          // --- ENHANCED CHAT VIEW ---
          <div className="flex-1 flex flex-col relative overflow-hidden">
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-hide">
               <div className="max-w-4xl mx-auto space-y-6 pb-32">
                 {messages.map((msg, idx) => (
                   <div key={idx} className={`w-full flex items-start gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                     
                     {/* AI Avatar with PL Branding */}
                     {msg.role === 'assistant' && (
                        <div className="relative w-10 h-10 rounded-xl bg-linear-to-br from-purple-600 to-pink-600 flex items-center justify-center shrink-0 shadow-lg">
                          <div className="absolute inset-0 bg-linear-to-br from-white/20 to-transparent rounded-xl"></div>
                          <Image src="/Premier_league_logo.svg" alt="AI" width={20} height={20} className="invert opacity-90 relative z-10"/>
                        </div>
                     )}

                     {/* Message Bubble */}
                     <div className="flex flex-col gap-2 max-w-[75%]">
                       <div className={`w-fit px-6 py-4 rounded-2xl text-[15px] leading-relaxed ${
                          msg.role === 'user' 
                          ? 'bg-linear-to-br from-zinc-800 to-zinc-900 text-white rounded-tr-sm border border-white/10 shadow-lg' 
                          : 'text-zinc-200 bg-zinc-900/30 border border-purple-500/20 backdrop-blur-sm'
                        }`}>
                          <ReactMarkdown
                            components={{
                              strong: ({node, ...props}) => <span className="font-bold text-white" {...props} />,
                              ul: ({node, ...props}) => <ul className="list-disc pl-4 space-y-1 my-2" {...props} />,
                              ol: ({node, ...props}) => <ol className="list-decimal pl-4 space-y-1 my-2" {...props} />,
                              li: ({node, ...props}) => <li className="pl-1" {...props} />,
                              p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                       </div>

                       {/* Regenerate Button */}
                       {msg.role === 'assistant' && (
                         <button
                           onClick={() => handleRegenerate(idx)}
                           disabled={regeneratingIndex === idx}
                           className="flex items-center gap-2 px-3 py-1.5 text-xs text-zinc-500 hover:text-purple-400 transition-colors self-start group rounded-lg hover:bg-purple-500/10"
                         >
                           <RefreshCw 
                             size={14} 
                             className={`${regeneratingIndex === idx ? 'animate-spin' : 'group-hover:rotate-180'} transition-transform duration-500`}
                           />
                           <span className="font-medium">{regeneratingIndex === idx ? 'Regenerating...' : 'Regenerate'}</span>
                         </button>
                       )}
                     </div>

                     {/* User Avatar */}
                     {msg.role === 'user' && (
                        <div className="w-10 h-10 rounded-xl bg-zinc-800 flex items-center justify-center border border-white/10 shrink-0 shadow-lg">
                           <User size={16} className="text-zinc-400" />
                        </div>
                     )}
                   </div>
                 ))}
                 
                 {/* Loading State */}
                 {isLoading && (
                   <div className="flex gap-4 items-start">
                     <div className="relative w-10 h-10 rounded-xl bg-linear-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-lg">
                       <Sparkles size={18} className="text-white animate-pulse" />
                     </div>
                     <div className="flex flex-col gap-2">
                       <div className="flex items-center gap-2 h-12 px-5 bg-zinc-900/30 border border-purple-500/20 rounded-2xl backdrop-blur-sm">
                         <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                         <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                         <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                         <span className="text-xs text-purple-400 font-medium ml-2">Analyzing...</span>
                       </div>
                     </div>
                   </div>
                 )}
                 <div ref={messagesEndRef} />
               </div>
            </div>
            
            {/* Enhanced Bottom Input */}
            <div className="absolute bottom-0 left-0 w-full p-6 bg-linear-to-t from-[#09090b] via-[#09090b] to-transparent z-20">
              <div className="max-w-4xl mx-auto">
                <div className="bg-linear-to-br from-zinc-900 to-black border-2 border-purple-500/30 rounded-2xl flex items-center p-2 shadow-2xl focus-within:border-purple-500/60 transition-all">
                  <input 
                    autoFocus 
                    className="flex-1 bg-transparent border-none outline-none text-white px-4 py-3 placeholder:text-zinc-500 font-medium" 
                    placeholder="Ask a follow-up question..." 
                    value={inputValue} 
                    onChange={(e) => setInputValue(e.target.value)} 
                    onKeyDown={handleKeyDown} 
                  />
                  <button 
                    onClick={handleSend} 
                    className={`px-5 py-3 rounded-xl font-bold text-sm transition-all duration-200 flex items-center gap-2 ${
                      inputValue.trim() 
                        ? 'bg-linear-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg hover:shadow-purple-500/50 hover:scale-105' 
                        : 'bg-zinc-800 text-zinc-600 cursor-not-allowed'
                    }`}
                    disabled={!inputValue.trim()}
                  >
                    <Send size={16} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}