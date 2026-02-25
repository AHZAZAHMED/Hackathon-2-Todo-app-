import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { AuthProvider } from "@/components/providers/AuthProvider";
import { TasksProvider } from "@/contexts/TasksContext";
import { ChatProvider } from "@/components/chat/ChatProvider";
import { ChatIcon } from "@/components/chat/ChatIcon";
import { ChatWindow } from "@/components/chat/ChatWindow";

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
        <AuthProvider>
          <TasksProvider>
            <ChatProvider>
              <Navbar />
              <main className="min-h-screen">{children}</main>
              <Footer />
              <ChatIcon />
              <ChatWindow />
            </ChatProvider>
          </TasksProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
