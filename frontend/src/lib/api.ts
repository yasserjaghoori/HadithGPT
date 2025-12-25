import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface HadithResult {
  score: number;
  collection: string;
  hadith_id: number;
  collection_reference: string;
  in_book_reference: string;
  web_reference: string;
  grading: string;
  narrator: string;
  text: string;
  arabic: string;
}

export interface HadithCluster {
  event_title: string;
  primary_index: number;
  hadith_indices: number[];
  reasoning?: string;
}

export interface SearchResponse {
  query: string;
  enhanced_query: string;
  query_type: string;
  message?: string;
  results: HadithResult[];
  total_results: number;
  searched_collections: string[];
  timestamp: string;
  clusters?: HadithCluster[];
}

export interface SearchRequest {
  query: string;
  user_id?: string;
  session_id?: string;
  top_k?: number;
  collections?: string[];
}

export const searchHadiths = async (
  request: SearchRequest,
  onProgress?: (progress: number, stage: string) => void
): Promise<SearchResponse> => {
  // Track progress through known stages
  const stages = [
    { progress: 20, stage: 'Analyzing query...' },
    { progress: 40, stage: 'Enhancing search...' },
    { progress: 60, stage: 'Searching collections...' },
    { progress: 80, stage: 'Ranking results...' },
    { progress: 95, stage: 'Processing hadiths...' }
  ];

  let currentStage = 0;
  const progressInterval = setInterval(() => {
    if (currentStage < stages.length && onProgress) {
      onProgress(stages[currentStage].progress, stages[currentStage].stage);
      currentStage++;
    }
  }, 400); // Update every 400ms for smooth progression

  try {
    const response = await axios.post<SearchResponse>(`${API_URL}/search`, request);
    clearInterval(progressInterval);
    if (onProgress) {
      onProgress(100, 'Complete!');
    }
    return response.data;
  } catch (error) {
    clearInterval(progressInterval);
    throw error;
  }
};

export const getCollections = async () => {
  const response = await axios.get(`${API_URL}/collections`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
};
