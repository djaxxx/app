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

  // Geographic Data
  async getRegions() {
    return this.request<{ code: string; name: string }[]>('/api/geo/regions');
  }

  async getDepartments(regionCode?: string) {
    const params = regionCode ? `?region_code=${regionCode}` : '';
    return this.request<{
      code: string;
      name: string;
      region_code?: string;
      region_name?: string;
      lat: number;
      lon: number;
    }[]>(`/api/geo/departments${params}`);
  }

  async lookupCity(city: string) {
    return this.request<{
      city: string;
      department_code: string;
      department_name: string;
      region_code: string;
      region_name: string;
      lat: number;
      lon: number;
    } | { error: string }>(`/api/geo/lookup-city?city=${encodeURIComponent(city)}`);
  }

  async getDJsForMap(filters: {
    region_code?: string;
    department_code?: string;
    type_evenement?: string;
    verifie_uniquement?: boolean;
  } = {}) {
    const params = new URLSearchParams();
    if (filters.region_code) params.append('region_code', filters.region_code);
    if (filters.department_code) params.append('department_code', filters.department_code);
    if (filters.type_evenement) params.append('type_evenement', filters.type_evenement);
    if (filters.verifie_uniquement) params.append('verifie_uniquement', 'true');

    return this.request<{
      total: number;
      djs: {
        user_id: string;
        nom_de_scene: string;
        ville: string;
        department_name?: string;
        region_name?: string;
        latitude: number;
        longitude: number;
        photo_profil?: string;
        note_moyenne: number;
        badge_verifie: boolean;
        tarif_indicatif?: string;
        types_evenements?: string[];
      }[];
    }>(`/api/geo/djs-map?${params.toString()}`);
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

  async deleteContact(requestId: string) {
    return this.request<{ message: string }>(`/api/dj/contacts/${requestId}`, {
      method: 'DELETE',
    });
  }

  // Boost
  async getBoostPlans() {
    return this.request<any[]>('/api/boost/plans');
  }

  async getBoostStatus() {
    return this.request<{
      boost_active: boolean;
      boost_plan: string | null;
      boost_start: string | null;
      boost_end: string | null;
      days_remaining: number;
    }>('/api/boost/status');
  }

  async createBoostCheckout(plan: string, originUrl: string) {
    return this.request<{ checkout_url: string; session_id: string; plan: string; amount: number }>('/api/boost/create-checkout', {
      method: 'POST',
      body: JSON.stringify({ plan, origin_url: originUrl }),
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

  // Admin APIs
  async adminListDJs() {
    return this.request<{ djs: any[]; total: number }>('/api/admin/djs');
  }

  // Reviews APIs
  async submitReview(data: { dj_user_id: string; client_nom: string; client_email: string; note: number; commentaire: string; type_evenement?: string; date_evenement?: string }) {
    return this.request<{ message: string; review_id: string }>('/api/reviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDJReviews(userId: string) {
    return this.request<any[]>(`/api/djs/${userId}/reviews`);
  }

  async getPendingReviews() {
    return this.request<{ reviews: any[]; count: number }>('/api/dj/reviews/pending');
  }

  async getAllMyReviews() {
    return this.request<{ reviews: any[]; total: number; pending_count: number }>('/api/dj/reviews/all');
  }

  async approveReview(reviewId: string) {
    return this.request<{ message: string }>(`/api/dj/reviews/${reviewId}/approve`, { method: 'PUT' });
  }

  async rejectReview(reviewId: string) {
    return this.request<{ message: string }>(`/api/dj/reviews/${reviewId}/reject`, { method: 'PUT' });
  }

  async adminCreateDJ(djData: any) {
    return this.request<{ message: string; dj: any }>('/api/admin/create-dj', {
      method: 'POST',
      body: JSON.stringify(djData),
    });
  }

  async adminToggleSubscription(userId: string) {
    return this.request<{ message: string; subscription_status: string }>(`/api/admin/djs/${userId}/toggle-subscription`, {
      method: 'PUT',
    });
  }

  async adminDeleteDJ(userId: string) {
    return this.request<{ message: string }>(`/api/admin/djs/${userId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiService();
