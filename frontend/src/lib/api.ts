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

export const searchHadiths = async (request: SearchRequest): Promise<SearchResponse> => {
  const response = await axios.post<SearchResponse>(`${API_URL}/search`, request);
  return response.data;
};

export const getCollections = async () => {
  const response = await axios.get(`${API_URL}/collections`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
};
