"use client";

import { useState, useEffect } from "react";

interface WelcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExampleClick?: (query: string) => void;
}

export default function WelcomeModal({ isOpen, onClose, onExampleClick }: WelcomeModalProps) {
  if (!isOpen) return null;

  const handleExampleClick = (query: string) => {
    onClose();
    if (onExampleClick) {
      onExampleClick(query);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="overflow-y-auto max-h-[90vh]">
          {/* Header */}
          <div className="bg-primary-500 text-white p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Welcome to HadithGPT</h2>
              <button
                onClick={onClose}
                className="p-1 hover:bg-primary-600 rounded-lg transition-colors"
                aria-label="Close"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <p className="mt-2 text-primary-50">Your trusted hadith search companion</p>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* How It Works */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Authentic & Trustworthy
              </h3>
              <div className="bg-primary-50 dark:bg-gray-700 p-4 rounded-lg space-y-2 text-sm text-gray-700 dark:text-gray-300">
                <p className="font-medium text-primary-700 dark:text-primary-400">
                  HadithGPT searches directly from the authentic hadith collections - not the internet.
                </p>
                <p>
                  We use a <strong>Retrieval Augmented Generation (RAG)</strong> system that pulls hadiths exclusively from the 6 major authentic books:
                </p>
                <ul className="list-disc list-inside pl-2 space-y-1">
                  <li>Sahih al-Bukhari</li>
                  <li>Sahih Muslim</li>
                  <li>Sunan Abu Dawud</li>
                  <li>Jami' at-Tirmidhi</li>
                  <li>Sunan an-Nasa'i</li>
                  <li>Sunan Ibn Majah</li>
                </ul>
                <p className="mt-3 font-medium text-primary-700 dark:text-primary-400">
                  ✓ AI helps you <em>find</em> hadiths, but never <em>generates</em> or fabricates them.
                </p>
              </div>
            </div>

            {/* How to Use */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                How to Get the Best Results
              </h3>
              <div className="space-y-3">
                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">✨ Try these example queries (click to search):</p>
                  <div className="space-y-2">
                    <button
                      onClick={() => handleExampleClick("What did the Prophet say about praying alone in a row?")}
                      className="w-full bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-600 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all text-left group"
                    >
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Example 1:</p>
                      <p className="text-sm font-mono text-primary-600 dark:text-primary-400 group-hover:text-primary-700 dark:group-hover:text-primary-300">
                        "What did the Prophet say about praying alone in a row?"
                      </p>
                    </button>
                    <button
                      onClick={() => handleExampleClick("Show me hadiths about the fly falling in a drink")}
                      className="w-full bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-600 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all text-left group"
                    >
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Example 2:</p>
                      <p className="text-sm font-mono text-primary-600 dark:text-primary-400 group-hover:text-primary-700 dark:group-hover:text-primary-300">
                        "Show me hadiths about the fly falling in a drink"
                      </p>
                    </button>
                    <button
                      onClick={() => handleExampleClick("What are the Prophet's teachings on charity in Ramadan?")}
                      className="w-full bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-600 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all text-left group"
                    >
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Example 3:</p>
                      <p className="text-sm font-mono text-primary-600 dark:text-primary-400 group-hover:text-primary-700 dark:group-hover:text-primary-300">
                        "What are the Prophet's teachings on charity in Ramadan?"
                      </p>
                    </button>
                  </div>
                </div>

                <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-4 rounded-lg">
                  <p className="text-sm text-amber-800 dark:text-amber-200">
                    <strong>💡 Tip:</strong> The more specific your question, the better the results! Include topics, situations, or even narrator names if you know them.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 bg-gray-50 dark:bg-gray-900">
            <button
              onClick={onClose}
              className="w-full px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-lg transition-colors shadow-sm"
            >
              Get Started
            </button>
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-3">
              You can always access this information again from the help menu
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}