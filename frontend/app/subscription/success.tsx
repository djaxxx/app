import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/stores/authStore';
import { api } from '../../src/services/api';
import { Button } from '../../src/components/Button';

export default function SubscriptionSuccessScreen() {
  const { session_id } = useLocalSearchParams<{ session_id: string }>();
  const router = useRouter();
  const { checkAuth } = useAuthStore();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [pollCount, setPollCount] = useState(0);

  useEffect(() => {
    const checkPaymentStatus = async () => {
      if (!session_id) {
        setStatus('error');
        return;
      }

      try {
        const result = await api.checkSubscriptionStatus(session_id);
        
        if (result.payment_status === 'paid') {
          setStatus('success');
          await checkAuth(); // Refresh user data
        } else if (result.status === 'expired') {
          setStatus('error');
        } else if (pollCount < 5) {
          // Continue polling
          setTimeout(() => setPollCount(c => c + 1), 2000);
        } else {
          setStatus('error');
        }
      } catch (error) {
        console.error('Payment status error:', error);
        if (pollCount < 5) {
          setTimeout(() => setPollCount(c => c + 1), 2000);
        } else {
          setStatus('error');
        }
      }
    };

    checkPaymentStatus();
  }, [session_id, pollCount]);

  if (status === 'loading') {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <ActivityIndicator size="large" color="#8B5CF6" />
          <Text style={styles.loadingText}>Vérification du paiement...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (status === 'error') {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.content}>
          <View style={styles.iconContainer}>
            <Ionicons name="close-circle" size={80} color="#EF4444" />
          </View>
          <Text style={styles.title}>Erreur de paiement</Text>
          <Text style={styles.message}>
            Nous n'avons pas pu confirmer votre paiement. Veuillez réessayer ou contacter le support.
          </Text>
          <Button
            title="Retour au tableau de bord"
            onPress={() => router.replace('/(tabs)/dashboard')}
            style={styles.button}
          />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Ionicons name="checkmark-circle" size={80} color="#10B981" />
        </View>
        <Text style={styles.title}>Paiement réussi !</Text>
        <Text style={styles.message}>
          Votre abonnement DJ Match est maintenant actif. Votre profil est visible par les clients.
        </Text>
        <View style={styles.details}>
          <View style={styles.detailRow}>
            <Ionicons name="checkmark" size={20} color="#10B981" />
            <Text style={styles.detailText}>Abonnement mensuel activé</Text>
          </View>
          <View style={styles.detailRow}>
            <Ionicons name="checkmark" size={20} color="#10B981" />
            <Text style={styles.detailText}>Profil visible sur la plateforme</Text>
          </View>
          <View style={styles.detailRow}>
            <Ionicons name="checkmark" size={20} color="#10B981" />
            <Text style={styles.detailText}>Réception des demandes clients</Text>
          </View>
        </View>
        <Button
          title="Aller au tableau de bord"
          onPress={() => router.replace('/(tabs)/dashboard')}
          style={styles.button}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0c0c0c',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  iconContainer: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: '#888',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 16,
  },
  details: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 20,
    width: '100%',
    marginBottom: 32,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  detailText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 12,
  },
  button: {
    width: '100%',
  },
});
