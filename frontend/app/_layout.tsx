import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { Platform, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuthStore } from '../src/stores/authStore';

// Error Boundary to catch any runtime crash on native
class AppErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: string}> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: '' };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message || 'Erreur inconnue' };
  }
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('App crash caught by ErrorBoundary:', error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <View style={ebStyles.container}>
          <Text style={ebStyles.icon}>⚠️</Text>
          <Text style={ebStyles.title}>DJ Match France</Text>
          <Text style={ebStyles.message}>Une erreur est survenue.</Text>
          <Text style={ebStyles.detail}>{this.state.error}</Text>
          <TouchableOpacity style={ebStyles.button} onPress={() => this.setState({ hasError: false, error: '' })}>
            <Text style={ebStyles.buttonText}>Réessayer</Text>
          </TouchableOpacity>
        </View>
      );
    }
    return this.props.children;
  }
}
const ebStyles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0B0B24', justifyContent: 'center', alignItems: 'center', padding: 32 },
  icon: { fontSize: 48, marginBottom: 16 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#fff', marginBottom: 8 },
  message: { fontSize: 16, color: '#aaa', marginBottom: 8, textAlign: 'center' },
  detail: { fontSize: 12, color: '#666', marginBottom: 24, textAlign: 'center' },
  button: { backgroundColor: '#8B5CF6', paddingHorizontal: 32, paddingVertical: 14, borderRadius: 12 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});

export default function RootLayout() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    // Skip auth check if returning from OAuth callback (web only)
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      try {
        if (window.location?.hash?.includes('session_id=')) {
          return;
        }
      } catch (_e) { /* safe fallback */ }
    }
    checkAuth();
  }, []);

  return (
    <AppErrorBoundary>
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
    </AppErrorBoundary>
  );
}
