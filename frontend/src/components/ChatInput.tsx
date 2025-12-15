"use client";

import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (query: string, collections: string[]) => void;
  isLoading: boolean;
  collections: string[];
}

export default function ChatInput({ onSend, isLoading, collections }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [selectedCollections, setSelectedCollections] = useState<string[]>([]);
  const [showCollections, setShowCollections] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea on input
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // Auto-resize based on content
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim(), selectedCollections);
      setInput("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleCollection = (collection: string) => {
    setSelectedCollections((prev) =>
      prev.includes(collection)
        ? prev.filter((c) => c !== collection)
        : [...prev, collection]
    );
  };

  // Format collection name for display
  const formatCollectionName = (id: string | any) => {
    if (typeof id !== 'string') return String(id);
    return id
      .replace("hadith-", "")
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4">
      <div className="max-w-4xl mx-auto">
        {/* Collection Filter */}
        {collections.length > 0 && (
          <div className="mb-3">
            <button
              onClick={() => setShowCollections(!showCollections)}
              className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 dark:hover:text-primary-400 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filter Collections
              {selectedCollections.length > 0 && (
                <span className="ml-1 px-2 py-0.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full text-xs">
                  {selectedCollections.length}
                </span>
              )}
            </button>

            {showCollections && (
              <div className="mt-2 flex flex-wrap gap-2">
                {collections.map((collection) => (
                  <button
                    key={collection}
                    onClick={() => toggleCollection(collection)}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      selectedCollections.includes(collection)
                        ? "bg-primary-500 text-white"
                        : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                    }`}
                  >
                    {formatCollectionName(collection)}
                  </button>
                ))}
                {selectedCollections.length > 0 && (
                  <button
                    onClick={() => setSelectedCollections([])}
                    className="px-3 py-1 text-sm text-red-500 hover:text-red-600"
                  >
                    Clear
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about any Hadith... (e.g., 'What did the Prophet say about prayer?')"
            disabled={isLoading}
            className="w-full resize-none rounded-3xl border-none outline-none focus:outline-none focus:ring-0 bg-white dark:bg-gray-800 shadow-lg px-5 py-4 pr-14 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 dark:focus:border-primary-500 disabled:opacity-50 disabled:cursor-not-allowed max-h-32 overflow-y-auto transition-all"
            rows={1}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-3 bottom-3 p-2 rounded-full bg-primary-500 text-white hover:bg-primary-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95 shadow-md"
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            )}
          </button>
        </form>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}