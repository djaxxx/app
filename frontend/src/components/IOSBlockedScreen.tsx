import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

interface IOSBlockedScreenProps {
  title?: string;
  message?: string;
  showBackButton?: boolean;
}

/**
 * Apple App Store compliance screen.
 * Apple guideline 3.1.1: digital subscriptions must use In-App Purchase.
 * Since we use Stripe for the web, we block subscription/payment UI on iOS.
 * We do NOT mention the external website (anti-steering rules).
 */
export default function IOSBlockedScreen({
  title = 'Fonctionnalité indisponible',
  message = 'Cette fonctionnalité n\'est pas disponible sur l\'application iOS pour le moment. Vous pouvez accéder à toutes les fonctionnalités depuis un navigateur sur ordinateur.',
  showBackButton = true,
}: IOSBlockedScreenProps) {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {showBackButton && (
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#1F2937" />
          </TouchableOpacity>
        </View>
      )}
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.iconWrapper}>
          <Ionicons name="information-circle-outline" size={80} color="#6366F1" />
        </View>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.message}>{message}</Text>
        <View style={styles.divider} />
        <View style={styles.infoBox}>
          <Ionicons name="laptop-outline" size={28} color="#6366F1" style={{ marginBottom: 8 }} />
          <Text style={styles.infoTitle}>Accédez via votre navigateur</Text>
          <Text style={styles.infoText}>
            Toutes les fonctionnalités professionnelles (inscription DJ, abonnement, gestion d'annonce, etc.) sont disponibles depuis un navigateur web.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  backButton: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'flex-start',
  },
  content: {
    flexGrow: 1,
    padding: 24,
    paddingTop: 40,
    alignItems: 'center',
  },
  iconWrapper: {
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: '#4B5563',
    textAlign: 'center',
    lineHeight: 24,
    maxWidth: 380,
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    width: '60%',
    marginVertical: 32,
  },
  infoBox: {
    backgroundColor: '#F3F4F6',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    maxWidth: 400,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  infoText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 20,
  },
});
