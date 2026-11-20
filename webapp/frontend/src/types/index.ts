export type QualityTier = 'all' | 'original' | 'high-copy' | 'copy';

export type Page =
  | 'dashboard'
  | 'analysis'
  | 'assistant'
  | 'saved'
  | 'reviews'
  | 'settings'
  | 'studio'
  | 'compare'
  | 'extension'
  | 'preview';

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface MaterialVerdict {
  status: 'ORIGINAL' | 'HIGH_COPY' | 'COPY';
  status_label: string;
  is_original_material: boolean;
  claimed_material: string;
  actual_material: string;
  discrepancies?: string[];
}

export interface PriceHistoryPoint {
  label_en: string;
  label_ar: string;
  price_usd: number;
  formatted_usd: string;
  formatted_egp: string;
}

export interface PriceHistoryInsight {
  lowest_usd: string;
  lowest_egp: string;
  highest_usd: string;
  highest_egp: string;
  avg_90d_usd: string;
  avg_90d_egp: string;
  price_drop_14d_percent: number;
  discount_verdict: 'REAL_DROP' | 'INFLATED_MSRP' | 'FAIR_MARKET';
  discount_verdict_en: string;
  discount_verdict_ar: string;
  stock_status?: 'IN_STOCK' | 'OUT_OF_STOCK' | 'UNAVAILABLE';
  points: PriceHistoryPoint[];
}

export interface PriceTierInfo {
  tier?: string;
  tier_label?: string;
  badge?: string;
  price: string;
  price_usd?: string;
  price_egp?: string;
  retail_msrp?: string;
  retailer?: string;
  material_summary?: string;
  savings?: string;
  url?: string;
  button_text?: string;
  is_verified?: boolean;
  verification_status?: string; // "VERIFIED" | "PARTIALLY_VERIFIED" | "UNVERIFIED"
  is_buy_button_enabled?: boolean;
  disabled_reason?: string;
  condition?: string;
  retrieval_timestamp?: string;
  shipping_info?: Record<string, any>;
  warranty_info?: string;
  stock_status?: 'IN_STOCK' | 'OUT_OF_STOCK' | 'UNAVAILABLE';
  price_history?: PriceHistoryInsight | null;
}

export interface PriceMatrix {
  original: PriceTierInfo;
  high_copy: PriceTierInfo;
  copy: PriceTierInfo;
}

export interface BuyingSource {
  title?: string;
  store_name?: string;
  price?: string;
  buy_url?: string;
  material_note?: string;
}

export interface ChatMessage {
  id: string;
  sender?: 'user' | 'ai';
  role?: 'user' | 'assistant';
  text?: string;
  content?: string;
  timestamp?: string;
  model?: string;
  model_name?: string;
  confidence?: number;
  is_recommendation?: boolean;
  has_verified_match?: boolean;
  material_verdict?: MaterialVerdict;
  price_matrix?: PriceMatrix;
  recommendation?: string;
  source?: string;
  sources?: BuyingSource[];
  error?: boolean;
  uncertainty_indicators?: Record<string, any>;
  provider_metadata?: Record<string, any>;
}

export interface ChatThread {
  id: string;
  title: string;
  model: string;
  createdAt: string;
  messages: ChatMessage[];
  updatedAt?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  updatedAt: string;
}

export interface Product {
  id?: number;
  name: string;
  brand?: string;
  category?: string;
  original_msrp?: string | number;
  authentic_materials?: string;
  verification_telltales?: string[];
  recommended_sources?: { tier: string; store: string; price: number; url: string }[];
  image?: string;
  url?: string;
  illustrative?: boolean;
}

export interface Audit {
  product_name: string;
  authenticity_score: number;
  verdict: string;
  verdict_title?: string;
  verdict_desc?: string;
  source?: string;
  source_notice?: string;
  catalog_image?: string;
  reality_image?: string;
  reality_synthesis_prompt?: string;
  analysis_breakdown?: Record<string, {
    score?: number;
    notes?: string;
    perceived_quality?: string;
    claimed_quality?: string;
    visible_discrepancies?: string[];
    catalog_description?: string;
    real_world_appearance?: string;
  }>;
  key_findings?: {
    positives?: string[];
    drawbacks?: string[];
  };
}

export interface AnalysisRecord {
  id: string;
  product: Product;
  audit: Audit;
  date: string;
}

export interface CommunityReview {
  id: number;
  user_name: string;
  product_name: string;
  tier?: 'original' | 'high-copy' | 'copy';
  rating: number;
  material_accuracy_rating: number;
  price_paid?: number;
  store_purchased_from?: string;
  product_url?: string;
  comment: string;
  is_verified_buyer?: boolean;
  upvotes: number;
  created_at: string;
}

export interface ReviewStats {
  total_reviews: number;
  avg_rating: number;
  avg_material_accuracy: number;
}

export interface StoreReputation {
  id: number;
  store_name: string;
  platform: string;
  specialty_tier: string;
  trust_score: number;
  material_honesty_rating: number;
  verified_url?: string;
  notes?: string;
}
