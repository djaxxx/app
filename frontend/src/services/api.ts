import { DJProfile, DJSearchFilters, EventType, ContactRequest, Review } from '../types';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  }

  // SIRET Verification
  async verifySiret(siret: string) {
    return this.request<{
      valid: boolean;
      company_name?: string;
      address?: string;
      activity?: string;
      message?: string;
    }>('/api/verify-siret', {
      method: 'POST',
      body: JSON.stringify({ siret }),
    });
  }

  // Event Types
  async getEventTypes(): Promise<EventType[]> {
    return this.request<EventType[]>('/api/event-types');
  }

  // DJ Profiles (Public)
  async searchDJs(filters: DJSearchFilters = {}, page = 1, limit = 20) {
    const params = new URLSearchParams();
    if (filters.ville) params.append('ville', filters.ville);
    if (filters.type_evenement) params.append('type_evenement', filters.type_evenement);
    if (filters.budget_max) params.append('budget_max', filters.budget_max.toString());
    if (filters.note_min) params.append('note_min', filters.note_min.toString());
    if (filters.verifie_uniquement) params.append('verifie_uniquement', 'true');
    params.append('page', page.toString());
    params.append('limit', limit.toString());

    return this.request<{
      total: number;
      page: number;
      limit: number;
      pages: number;
      djs: DJProfile[];
    }>(`/api/djs?${params.toString()}`);
  }

  async getDJProfile(userId: string): Promise<DJProfile> {
    return this.request<DJProfile>(`/api/djs/${userId}`);
  }

  // DJ Registration
  async registerDJ(profileData: Partial<DJProfile>) {
    return this.request<{ message: string; profile: DJProfile }>('/api/dj/register', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  }

  // DJ Profile Management (Authenticated)
  async getMyDJProfile(): Promise<DJProfile> {
    return this.request<DJProfile>('/api/dj/profile');
  }

  async updateDJProfile(updates: Partial<DJProfile>) {
    return this.request<{ message: string; profile: DJProfile }>('/api/dj/profile', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // DJ Dashboard
  async getDJDashboard() {
    return this.request<{
      nombre_vues: number;
      nombre_demandes: number;
      demandes_non_lues: number;
      note_moyenne: number;
      nombre_avis: number;
      profil_complete_percent: number;
      badge_verifie: boolean;
      subscription_status: string;
      subscription_end_date?: string;
      recent_reviews: Review[];
    }>('/api/dj/dashboard');
  }

  // Contact Requests
  async sendContactRequest(data: {
    dj_user_id: string;
    client_nom: string;
    client_email: string;
    client_telephone: string;
    date_evenement: string;
    lieu_evenement: string;
    type_evenement: string;
    message: string;
  }) {
    return this.request<{ message: string; request_id: string }>('/api/contact', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDJContacts(status?: string): Promise<ContactRequest[]> {
    const params = status ? `?status=${status}` : '';
    return this.request<ContactRequest[]>(`/api/dj/contacts${params}`);
  }

  async markContactRead(requestId: string) {
    return this.request<{ message: string }>(`/api/dj/contacts/${requestId}/read`, {
      method: 'PUT',
    });
  }

  // Reviews
  async submitReview(data: {
    dj_user_id: string;
    client_nom: string;
    client_email: string;
    note: number;
    commentaire: string;
    type_evenement?: string;
  }) {
    return this.request<{ message: string; review_id: string }>('/api/reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDJReviews(userId: string): Promise<Review[]> {
    return this.request<Review[]>(`/api/djs/${userId}/reviews`);
  }

  // Subscription
  async getSubscriptionPlans() {
    return this.request<{
      id: string;
      amount: number;
      currency: string;
      label: string;
      description: string;
      days: number;
    }[]>('/api/subscription/plans');
  }

  async createSubscriptionCheckout(originUrl: string, plan: 'monthly' | 'annual' = 'monthly') {
    return this.request<{ checkout_url: string; session_id: string; plan: string; amount: number }>('/api/subscription/create-checkout', {
      method: 'POST',
      body: JSON.stringify({ origin_url: originUrl, plan }),
    });
  }

  async checkSubscriptionStatus(sessionId: string) {
    return this.request<{
      status: string;
      payment_status: string;
      amount_total: number;
      currency: string;
    }>(`/api/subscription/status/${sessionId}`);
  }
}

export const api = new ApiService();
