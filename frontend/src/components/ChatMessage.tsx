import HadithCarousel from "./HadithCarousel";
import HadithCluster from "./HadithCluster";
import type { Message } from "@/types";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  // Render hadiths with clustering using carousel
  const renderHadiths = () => {
    if (!message.hadithResults || message.hadithResults.length === 0) {
      return null;
    }

    if (message.clusters && message.clusters.length > 0) {
      // We have clusters - render clusters and collect standalone hadiths
      const processedIndices = new Set<number>();
      const elements: JSX.Element[] = [];
      let currentRank = 1;

      // Render clusters
      message.clusters.forEach((cluster, clusterIdx) => {
        elements.push(
          <HadithCluster
            key={`cluster-${clusterIdx}`}
            cluster={cluster}
            hadiths={message.hadithResults!}
            startRank={currentRank}
          />
        );
        cluster.hadith_indices.forEach((idx) => processedIndices.add(idx));
        currentRank += cluster.hadith_indices.length;
      });

      // Collect standalone hadiths
      const standaloneHadiths = message.hadithResults.filter((_, index) => !processedIndices.has(index));

      // Render standalone hadiths in carousel if any
      if (standaloneHadiths.length > 0) {
        elements.push(
          <HadithCarousel
            key="standalone-carousel"
            hadiths={standaloneHadiths}
            startRank={currentRank}
          />
        );
      }

      return elements;
    } else {
      // No clusters - render all hadiths in a single carousel
      return (
        <HadithCarousel
          hadiths={message.hadithResults}
          startRank={1}
        />
      );
    }
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-3xl ${isUser ? "w-auto" : "w-full"}`}>
        {/* Message Bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? "bg-primary-500 text-white"
              : "bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700"
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>

          {/* Enhanced Query Debug Info (Optional) */}
          {message.metadata?.enhanced_query && (
            <details className="mt-2 text-xs opacity-70">
              <summary className="cursor-pointer hover:opacity-100">Enhanced Query</summary>
              <p className="mt-1 font-mono">{message.metadata.enhanced_query}</p>
            </details>
          )}
        </div>

        {/* Hadith Results (with clusters if available) */}
        {message.hadithResults && message.hadithResults.length > 0 && (
          <div className="mt-4 space-y-4">
            {renderHadiths()}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 px-1">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </div>
  );
}
