// Cluster Types
export interface HadithCluster {
  event_title: string;
  primary_index: number;
  hadith_indices: number[];
  reasoning?: string;
}

// Message Types
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  hadithResults?: HadithResult[];
  clusters?: HadithCluster[];
  metadata?: {
    query_type?: string;
    enhanced_query?: string;
    total_results?: number;
  };
}

// Hadith Search Types (matches FastAPI backend)
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

export interface SearchRequest {
  query: string;
  collections?: string[];
  top_k?: number;
  user_id?: string;
  session_id?: string;
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

// Conversation Types
export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
}

// User Types
export interface UserProfile {
  id: string;
  email: string;
  display_name?: string;
  preferred_language?: string;
  favorite_collections?: string[];
  created_at: Date;
}
