import type { HadithResult } from "@/types";

interface HadithCardProps {
  hadith: HadithResult;
  rank: number;
}

export default function HadithCard({ hadith, rank }: HadithCardProps) {
  // Extract collection name (e.g., "hadith-bukhari" -> "Bukhari")
  const collectionName = hadith.collection
    ? hadith.collection
        .replace("hadith-", "")
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    : "Unknown";

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
      <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
        {hadith.hadith_id && (
          <span>Hadith #{hadith.hadith_id}</span>
        )}
        {hadith.in_book_reference && (
          <span>• {hadith.in_book_reference}</span>
        )}
      </div>
    </div>
  );
}
