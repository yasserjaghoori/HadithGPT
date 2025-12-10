"use client";

import HadithCarousel from "./HadithCarousel";
import type { HadithResult, HadithCluster as HadithClusterType } from "@/types";

interface HadithClusterProps {
  cluster: HadithClusterType;
  hadiths: HadithResult[];
  startRank: number;
}

export default function HadithCluster({ cluster, hadiths, startRank }: HadithClusterProps) {
  // Get the hadiths in this cluster, with primary first
  const clusterHadiths = cluster.hadith_indices.map((idx) => hadiths[idx]);

  // Reorder to put primary first
  const primaryHadith = hadiths[cluster.primary_index];
  const otherHadiths = clusterHadiths.filter((h) => h !== primaryHadith);
  const orderedHadiths = [primaryHadith, ...otherHadiths];

  return (
    <div className="space-y-2">
      {/* Use Carousel for clustered hadiths */}
      <HadithCarousel
        hadiths={orderedHadiths}
        title={cluster.event_title}
        startRank={startRank}
      />

      {/* Optional: Show reasoning in dev mode */}
      {process.env.NODE_ENV === "development" && cluster.reasoning && (
        <details className="text-xs text-gray-500 dark:text-gray-400 px-2">
          <summary className="cursor-pointer hover:text-primary-600 dark:hover:text-primary-400">
            Why these were grouped (dev only)
          </summary>
          <p className="mt-1 pl-4 italic">{cluster.reasoning}</p>
        </details>
      )}
    </div>
  );
}
