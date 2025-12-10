"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import ThemeToggle from "@/components/ThemeToggle";
import { searchHadiths, getCollections } from "@/lib/api";
import { getCurrentUser } from "@/lib/supabase";
import type { Message, HadithResult } from "@/types";

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [collections, setCollections] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check auth status
    getCurrentUser().then(setCurrentUser);

    // Load available collections
    getCollections()
      .then((data) => {
        // Extract collection names from the response
        const collectionNames = data.available_collections?.map((c: any) => c.name) || [];
        setCollections(collectionNames);
      })
      .catch(console.error);

    // Add welcome message
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: "Assalamu Alaikum! I'm HadithGPT. Ask me anything about the Hadiths, and I'll search across Sahih Bukhari, Sahih Muslim, and other collections to find relevant narrations.",
        timestamp: new Date(),
      },
    ]);
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (query: string, selectedCollections: string[]) => {
    if (!query.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call API (let backend LLM determine result count)
      const response = await searchHadiths({
        query,
        collections: selectedCollections.length > 0 ? selectedCollections : undefined,
        user_id: currentUser?.id,
        // No top_k - let LLM decide based on query intent
      });

      // Add assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message || (response.results.length > 0 ? "Here are the most relevant Hadiths I found:" : "No results found."),
        timestamp: new Date(),
        hadithResults: response.results.length > 0 ? response.results : undefined,
        clusters: response.clusters,
        metadata: {
          query_type: response.query_type,
          enhanced_query: response.enhanced_query,
          total_results: response.total_results,
        },
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I encountered an error: ${error.response?.data?.detail || error.message || "Please try again."}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        currentUser={currentUser}
        onNewChat={() => {
          setMessages([
            {
              id: "1",
              role: "assistant",
              content: "Assalamu Alaikum! I'm HadithGPT. Ask me anything about the Hadiths.",
              timestamp: new Date(),
            },
          ]);
        }}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {!isSidebarOpen && (
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            )}
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Hadith<span className="text-primary-500">GPT</span>
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            {!currentUser && (
              <button
                onClick={() => router.push("/auth/login")}
                className="px-4 py-2 text-sm text-primary-500 hover:bg-primary-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                Sign In
              </button>
            )}
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <ChatInput
          onSend={handleSendMessage}
          isLoading={isLoading}
          collections={collections}
        />
      </div>
    </div>
  );
}
