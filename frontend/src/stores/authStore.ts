import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, DJProfile } from '../types';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';
const TOKEN_KEY = 'session_token';

async function getToken(): Promise<string | null> {
  try { return await AsyncStorage.getItem(TOKEN_KEY); } catch { return null; }
}
async function setToken(token: string | null): Promise<void> {
  try {
    if (token) await AsyncStorage.setItem(TOKEN_KEY, token);
    else await AsyncStorage.removeItem(TOKEN_KEY);
  } catch {}
}

async function authedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await getToken();
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return fetch(url, { ...options, headers });
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  checkAuth: () => Promise<void>;
  exchangeSession: (sessionId: string) => Promise<User | null>;
  registerWithEmail: (email: string, password: string, name: string) => Promise<User | null>;
  loginWithEmail: (email: string, password: string) => Promise<User | null>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  checkAuth: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await authedFetch(`${API_URL}/api/auth/me`);
      if (response.ok) {
        const user = await response.json();
        if (user.session_token) await setToken(user.session_token);
        set({ user, isAuthenticated: true, isLoading: false });
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch (error) {
      console.error('Auth check error:', error);
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  exchangeSession: async (sessionId: string) => {
    try {
      set({ isLoading: true, error: null });
      const response = await authedFetch(`${API_URL}/api/auth/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (response.ok) {
        const user = await response.json();
        if (user.session_token) await setToken(user.session_token);
        set({ user, isAuthenticated: true, isLoading: false });
        return user;
      } else {
        const error = await response.json();
        set({ error: error.detail || 'Erreur d\'authentification', isLoading: false });
        return null;
      }
    } catch (error) {
      console.error('Session exchange error:', error);
      set({ error: 'Erreur de connexion', isLoading: false });
      return null;
    }
  },

  registerWithEmail: async (email: string, password: string, name: string) => {
    try {
      set({ isLoading: true, error: null });
      const response = await authedFetch(`${API_URL}/api/auth/register-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
      });
      if (response.ok) {
        const user = await response.json();
        if (user.session_token) await setToken(user.session_token);
        set({ user, isAuthenticated: true, isLoading: false });
        return user;
      } else {
        const error = await response.json();
        set({ error: error.detail || 'Erreur lors de l\'inscription', isLoading: false });
        return null;
      }
    } catch (error) {
      console.error('Register error:', error);
      set({ error: 'Erreur de connexion au serveur', isLoading: false });
      return null;
    }
  },

  loginWithEmail: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      const response = await authedFetch(`${API_URL}/api/auth/login-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (response.ok) {
        const user = await response.json();
        if (user.session_token) await setToken(user.session_token);
        set({ user, isAuthenticated: true, isLoading: false });
        return user;
      } else {
        const error = await response.json();
        set({ error: error.detail || 'Email ou mot de passe incorrect', isLoading: false });
        return null;
      }
    } catch (error) {
      console.error('Login error:', error);
      set({ error: 'Erreur de connexion au serveur', isLoading: false });
      return null;
    }
  },

  logout: async () => {
    try {
      await authedFetch(`${API_URL}/api/auth/logout`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await setToken(null);
      set({ user: null, isAuthenticated: false });
    }
  },

  clearError: () => set({ error: null }),
}));
