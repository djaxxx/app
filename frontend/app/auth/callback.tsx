import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../src/stores/authStore';

export default function AuthCallback() {
  const router = useRouter();
  const exchangeSession = useAuthStore((state) => state.exchangeSession);
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double processing in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processCallback = async () => {
      try {
        // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
        // Get session_id from URL fragment (web only)
        let sessionId = '';
        
        if (Platform.OS === 'web' && typeof window !== 'undefined') {
          try {
            const hash = window.location.hash;
            const params = new URLSearchParams(hash.substring(1));
            sessionId = params.get('session_id') || '';
          } catch (e) {}
        }

        if (sessionId) {
          const user = await exchangeSession(sessionId);
          if (user) {
            // Clear the URL fragment (web only)
            if (Platform.OS === 'web' && typeof window !== 'undefined') {
              try { window.history.replaceState(null, '', window.location.pathname); } catch (e) {}
            }
            // Navigate based on user type
            if (user.has_dj_profile) {
              router.replace('/(tabs)/dashboard');
            } else {
              // New user without DJ profile → send to registration
              router.replace('/dj-register');
            }
          } else {
            router.replace('/');
          }
        } else {
          router.replace('/');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        router.replace('/');
      }
    };

    processCallback();
  }, []);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#8B5CF6" />
      <Text style={styles.text}>Connexion en cours...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    color: '#fff',
    fontSize: 16,
    marginTop: 16,
  },
});
