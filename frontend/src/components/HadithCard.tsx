"use client";

import { useState } from "react";
import type { HadithResult } from "@/types";

interface HadithCardProps {
  hadith: HadithResult;
  rank: number;
}
// testing 
export default function HadithCard({ hadith, rank }: HadithCardProps) {
  const [copySuccess, setCopySuccess] = useState(false);

  // Extract collection name (e.g., "hadith-bukhari" -> "Bukhari")
  const collectionName = hadith.collection
    ? hadith.collection
        .replace("hadith-", "")
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    : "Unknown";

  // Format hadith for copying/sharing
  const formatHadithText = () => {
    let formatted = `${collectionName} - ${hadith.collection_reference}\n`;
    if (hadith.grading) formatted += `Grading: ${hadith.grading}\n`;
    formatted += `\n${hadith.text}\n`;
    if (hadith.arabic) formatted += `\n${hadith.arabic}\n`;
    if (hadith.narrator) formatted += `\nNarrator: ${hadith.narrator}\n`;
    if (hadith.in_book_reference) formatted += `\nReference: ${hadith.in_book_reference}`;
    if (hadith.web_reference) formatted += `\nSource: ${hadith.web_reference}`;
    return formatted;
  };

  // Copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formatHadithText());
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  // Share using Web Share API or fallback to copy
  const handleShare = async () => {
    const shareData = {
      title: `${collectionName} - ${hadith.collection_reference}`,
      text: formatHadithText(),
      url: hadith.web_reference || undefined,
    };

    try {
      if (navigator.share && navigator.canShare?.(shareData)) {
        await navigator.share(shareData);
      } else {
        // Fallback to copy
        await handleCopy();
      }
    } catch (err) {
      // User cancelled or error occurred
      if ((err as Error).name !== "AbortError") {
        console.error("Share failed:", err);
      }
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-6 h-6 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full text-xs font-semibold">
            {rank}
          </span>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {collectionName}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {hadith.collection_reference || "No reference"}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          {hadith.grading && (
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 rounded">
              {hadith.grading}
            </span>
          )}
        </div>
      </div>

      {/* English Text */}
      <div className="mb-3">
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
          {hadith.text}
        </p>
      </div>

      {/* Arabic Text (if available) */}
      {hadith.arabic && (
        <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-900/50 rounded border-r-4 border-primary-500">
          <p className="text-right text-lg leading-loose font-arabic text-gray-900 dark:text-white" dir="rtl">
            {hadith.arabic}
          </p>
        </div>
      )}

      {/* Narrator */}
      {hadith.narrator && (
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span className="font-medium">Narrator:</span> {hadith.narrator}
        </div>
      )}

      {/* Footer Info */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap gap-2">
          {hadith.hadith_id && (
            <span>Hadith #{hadith.hadith_id}</span>
          )}
          {hadith.in_book_reference && (
            <span>• {hadith.in_book_reference}</span>
          )}
        </div>

        {/* Copy and Share Buttons */}
        <div className="flex gap-2 ml-auto">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            title="Copy hadith"
          >
            {copySuccess ? (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Copied!</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>Copy</span>
              </>
            )}
          </button>

          <button
            onClick={handleShare}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            title="Share hadith"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            <span>Share</span>
          </button>
        </div>
      </div>
    </div>
  );
}
