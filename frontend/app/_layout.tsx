import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { useAuthStore } from '../src/stores/authStore';

export default function RootLayout() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    // Skip auth check if returning from OAuth callback
    if (typeof window !== 'undefined' && window.location.hash?.includes('session_id=')) {
      return;
    }
    checkAuth();
  }, []);

  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#0c0c0c',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          contentStyle: {
            backgroundColor: '#0c0c0c',
          },
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="auth/callback" options={{ headerShown: false }} />
        <Stack.Screen name="dj/[id]" options={{ title: 'Profil DJ' }} />
        <Stack.Screen name="contact/[djId]" options={{ title: 'Contacter' }} />
        <Stack.Screen name="dj-register" options={{ title: 'Inscription DJ' }} />
        <Stack.Screen name="subscription/success" options={{ title: 'Paiement' }} />
        <Stack.Screen name="subscription/cancel" options={{ title: 'Paiement annulé' }} />
      </Stack>
    </>
  );
}
