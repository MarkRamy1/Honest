import { CommunityReview, ReviewStats, StoreReputation, User } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

// Tier-S Lightweight Client Cache (speed-engineer: 60s staleTime + in-flight deduplication, no Redis)
const CLIENT_CACHE_TTL_MS = 60_000;
const responseCache = new Map<string, { data: any; expiresAt: number }>();
const inFlightRequests = new Map<string, Promise<any>>();

async function cachedGetJson<T = any>(cacheKey: string, url: string, ttlMs = CLIENT_CACHE_TTL_MS): Promise<T> {
  const now = Date.now();
  const cached = responseCache.get(cacheKey);
  if (cached && cached.expiresAt > now) {
    return cached.data as T;
  }
  const existingFlight = inFlightRequests.get(cacheKey);
  if (existingFlight) {
    return existingFlight as Promise<T>;
  }
  const reqPromise = fetch(url)
    .then((res) => res.json())
    .then((data) => {
      responseCache.set(cacheKey, { data, expiresAt: Date.now() + ttlMs });
      inFlightRequests.delete(cacheKey);
      return data as T;
    })
    .catch((err) => {
      inFlightRequests.delete(cacheKey);
      throw err;
    });
  inFlightRequests.set(cacheKey, reqPromise);
  return reqPromise;
}

export function invalidateApiCache(prefix: string): void {
  for (const key of Array.from(responseCache.keys())) {
    if (key.startsWith(prefix)) {
      responseCache.delete(key);
    }
  }
}

function getHeaders(extraHeaders: Record<string, string> = {}): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...extraHeaders
  };
  const token = localStorage.getItem('honest_jwt_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Health
  async checkHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.json();
  },

  // Agent
  async askAgent(payload: {
    question: string;
    product_title?: string;
    model?: string;
    tier?: string;
    apiKey?: string;
  }) {
    const customKey = payload.apiKey || localStorage.getItem('honest_gemini_api_key') || '';
    const headers: Record<string, string> = {};
    if (customKey) {
      headers['X-API-Key'] = customKey;
    }

    const res = await fetch(`${API_BASE}/api/agent/ask`, {
      method: 'POST',
      headers: getHeaders(headers),
      body: JSON.stringify({
        question: payload.question,
        product_title: payload.product_title || payload.question,
        model: payload.model || 'honest-engine',
        tier: payload.tier || 'all',
        apiKey: customKey
      })
    });
    return res.json();
  },

  async recommendProducts(query: string, category?: string, budget?: number, useCases?: string[]) {
    const res = await fetch(`${API_BASE}/api/agent/recommend`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ query, category, budget, useCases })
    });
    return res.json();
  },

  async compareInCart(productTitle: string, currentPrice?: number) {
    const res = await fetch(`${API_BASE}/api/agent/compare-in-cart`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ productTitle, currentPrice })
    });
    return res.json();
  },

  // Reviews
  async getReviews(params?: { product?: string; tier?: string; brand?: string; page?: number }): Promise<{
    success: boolean;
    reviews: CommunityReview[];
    pagination: { current_page: number; last_page: number; total: number };
    stats: ReviewStats;
  }> {
    const query = new URLSearchParams();
    if (params?.product) query.set('product', params.product);
    if (params?.tier) query.set('tier', params.tier);
    if (params?.brand) query.set('brand', params.brand);
    if (params?.page) query.set('page', String(params.page));

    const qs = query.toString();
    return cachedGetJson(`reviews:${qs}`, `${API_BASE}/api/reviews?${qs}`, 30_000);
  },

  async submitReview(review: {
    product_name: string;
    user_name?: string;
    tier: string;
    rating: number;
    material_accuracy_rating: number;
    price_paid?: number;
    store_purchased_from?: string;
    product_url?: string;
    comment: string;
  }) {
    const res = await fetch(`${API_BASE}/api/reviews`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(review)
    });
    const data = await res.json();
    invalidateApiCache('reviews:');
    return data;
  },

  async upvoteReview(id: number) {
    const res = await fetch(`${API_BASE}/api/reviews/${id}/upvote`, {
      method: 'POST',
      headers: getHeaders()
    });
    const data = await res.json();
    invalidateApiCache('reviews:');
    return data;
  },

  // Catalog
  async searchCatalog(q: string = '') {
    const encoded = encodeURIComponent(q);
    return cachedGetJson(`catalog:search:${encoded}`, `${API_BASE}/api/catalog/search?q=${encoded}`, 60_000);
  },

  async getStores(): Promise<{ success: boolean; stores: StoreReputation[] }> {
    return cachedGetJson('catalog:stores', `${API_BASE}/api/catalog/stores`, 60_000);
  },

  // Auth
  async register(name: string, email: string, password: string): Promise<{ success: boolean; message: string; user?: User; token?: string }> {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (data.token) {
      localStorage.setItem('honest_jwt_token', data.token);
    }
    return data;
  },

  async login(email: string, password: string): Promise<{ success: boolean; message: string; user?: User; token?: string }> {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (data.token) {
      localStorage.setItem('honest_jwt_token', data.token);
    }
    return data;
  },

  async googleAuth(payload: { credential?: string; email?: string; name?: string }): Promise<{
    success: boolean;
    is_new_user?: boolean;
    message: string;
    user?: User;
    token?: string;
    detail?: string;
  }> {
    const res = await fetch(`${API_BASE}/api/auth/google`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.token) {
      localStorage.setItem('honest_jwt_token', data.token);
    }
    return data;
  },

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        headers: getHeaders()
      });
    } finally {
      localStorage.removeItem('honest_jwt_token');
      localStorage.removeItem('honest_auth_user');
    }
  },

  async getMe(): Promise<{ authenticated: boolean; user: User | null }> {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: getHeaders()
    });
    return res.json();
  }
};
