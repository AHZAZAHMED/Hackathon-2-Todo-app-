import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { AuthProvider } from "@/components/providers/AuthProvider";
import { ChatUIProvider } from "@/lib/contexts/ChatUIContext";
import { FloatingChatLauncher } from "@/components/chat/FloatingChatLauncher";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Todo App - Manage Your Tasks Efficiently",
  description: "A modern task management application built with Next.js. Organize your tasks, track progress, and boost productivity.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* Load ChatKit web component */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
        <AuthProvider>
          <ChatUIProvider>
            <Navbar />
            <main className="min-h-screen">{children}</main>
            <Footer />
            <FloatingChatLauncher />
          </ChatUIProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
