import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { Platform } from 'react-native';
import { useAuthStore } from '../src/stores/authStore';

export default function RootLayout() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    // Skip auth check if returning from OAuth callback (web only)
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      try {
        if (window.location?.hash?.includes('session_id=')) {
          return;
        }
      } catch (_e) { /* native fallback */ }
    }
    checkAuth();
  }, []);

  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#0B0B24',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          contentStyle: {
            backgroundColor: '#0B0B24',
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
        <Stack.Screen name="edit-profile" options={{ title: 'Modifier le profil', headerShown: false }} />
        <Stack.Screen name="boost" options={{ title: 'Booster mon profil', headerShown: false }} />
        <Stack.Screen name="boost/success" options={{ title: 'Boost activé', headerShown: false }} />
        <Stack.Screen name="boost/cancel" options={{ title: 'Boost annulé', headerShown: false }} />
        <Stack.Screen name="my-contacts" options={{ title: 'Mes demandes', headerShown: false }} />
        <Stack.Screen name="zone-management" options={{ title: 'Zone d\'intervention', headerShown: false }} />
        <Stack.Screen name="zone/success" options={{ title: 'Zone ajoutée', headerShown: false }} />
        <Stack.Screen name="zone/cancel" options={{ title: 'Zone annulée', headerShown: false }} />
        <Stack.Screen name="admin-contacts" options={{ title: 'Base Contacts CRM', headerShown: false }} />
      </Stack>
    </>
  );
}
