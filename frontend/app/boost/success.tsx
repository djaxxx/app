import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../src/services/api';

export default function BoostSuccessScreen() {
  const router = useRouter();
  const { session_id } = useLocalSearchParams();
  const [verifying, setVerifying] = useState(!!session_id);
  const [paid, setPaid] = useState(false);

  useEffect(() => {
    if (session_id) {
      api.verifyBoostPayment(session_id as string)
        .then(res => { setPaid(res.payment_status === 'paid'); })
        .catch(() => {})
        .finally(() => setVerifying(false));
    }
  }, [session_id]);

  if (verifying) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#FFD700" />
        <Text style={{ color: '#fff', marginTop: 16 }}>Verification du paiement...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconCircle}>
          <Ionicons name="star" size={48} color="#FFD700" />
        </View>
        <Text style={styles.title}>Boost activé !</Text>
        <Text style={styles.subtitle}>
          Votre profil est maintenant épinglé en tête de liste avec un badge doré.{"\n"}
          Les clients vous verront en premier !
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.replace('/(tabs)/dashboard')}
        >
          <Text style={styles.buttonText}>Retour au Dashboard</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
    justifyContent: 'center',
  },
  content: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  iconCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: 'rgba(255, 215, 0, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFD700',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  button: {
    backgroundColor: '#FFD700',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  buttonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
