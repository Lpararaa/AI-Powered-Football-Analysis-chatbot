import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "Premier League AI",
  description: "Stats • Insights • Predictions",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark h-full">
      <body 
        className="antialiased bg-[#09090b] text-white h-full"
        suppressHydrationWarning={true}  // <-- Add this line here
      >
        <main className="h-full w-full">
          {children}
        </main>
      </body>
    </html>
  );
}