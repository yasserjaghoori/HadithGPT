"use client";

import { useState } from "react";
import HadithCard from "./HadithCard";
import type { HadithResult } from "@/types";

interface HadithCarouselProps {
  hadiths: HadithResult[];
  title?: string;
  startRank?: number;
}

export default function HadithCarousel({ hadiths, title, startRank = 1 }: HadithCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (hadiths.length === 0) return null;

  const currentHadith = hadiths[currentIndex];
  const currentRank = startRank + currentIndex;

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % hadiths.length);
  };

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + hadiths.length) % hadiths.length);
  };

  const goToIndex = (index: number) => {
    setCurrentIndex(index);
  };

  return (
    <div className="space-y-3">
      {/* Optional Title */}
      {title && (
        <div className="flex items-center gap-2 px-2">
          <div className="flex-1 h-px bg-gradient-to-r from-primary-500/20 to-transparent"></div>
          <h3 className="text-sm font-semibold text-primary-600 dark:text-primary-400 flex items-center gap-2">
            <span className="text-lg">📖</span>
            {title}
          </h3>
          <div className="flex-1 h-px bg-gradient-to-l from-primary-500/20 to-transparent"></div>
        </div>
      )}

      {/* Hadith Card */}
      <div className="relative group">
        <HadithCard hadith={currentHadith} rank={currentRank} />

        {/* Navigation Overlay (only show if more than 1 hadith) */}
        {hadiths.length > 1 && (
          <>
            {/* Previous Button */}
            {currentIndex > 0 && (
              <button
                onClick={goToPrevious}
                className="absolute left-2 top-1/2 -translate-y-1/2
                         bg-white dark:bg-gray-800 border-2 border-primary-500
                         text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20
                         rounded-full p-3 shadow-lg transition-all hover:scale-110
                         opacity-0 group-hover:opacity-100"
                aria-label="Previous hadith"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}

            {/* Next Button */}
            {currentIndex < hadiths.length - 1 && (
              <button
                onClick={goToNext}
                className="absolute right-2 top-1/2 -translate-y-1/2
                         bg-white dark:bg-gray-800 border-2 border-primary-500
                         text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20
                         rounded-full p-3 shadow-lg transition-all hover:scale-110
                         opacity-0 group-hover:opacity-100"
                aria-label="Next hadith"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            )}
          </>
        )}
      </div>

      {/* Dot Indicators (only show if more than 1 hadith) */}
      {hadiths.length > 1 && (
        <div className="flex items-center justify-center gap-2 py-2">
          <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">
            {currentIndex + 1} of {hadiths.length}
          </span>
          {hadiths.map((_, index) => (
            <button
              key={index}
              onClick={() => goToIndex(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentIndex
                  ? "bg-primary-500 w-6"
                  : "bg-gray-300 dark:bg-gray-600 hover:bg-primary-300"
              }`}
              aria-label={`Go to hadith ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Keyboard Shortcuts Hint */}
      {hadiths.length > 1 && (
        <div className="text-center text-xs text-gray-400 dark:text-gray-500 italic">
          Use ← → arrow keys or swipe to navigate
        </div>
      )}
    </div>
  );
}
