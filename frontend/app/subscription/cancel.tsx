import React from 'react';
import {
  View,
  Text,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '../../src/components/Button';

export default function SubscriptionCancelScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Ionicons name="close-circle" size={80} color="#F59E0B" />
        </View>
        <Text style={styles.title}>Paiement annulé</Text>
        <Text style={styles.message}>
          Votre paiement a été annulé. Vous pouvez réessayer à tout moment depuis votre tableau de bord.
        </Text>
        <View style={styles.infoBox}>
          <Ionicons name="information-circle" size={24} color="#8B5CF6" />
          <Text style={styles.infoText}>
            L'abonnement DJ Match coûte seulement 8€/mois ou 80€/an et vous permet d'être visible par des milliers de clients potentiels.
          </Text>
        </View>
        <Button
          title="Retour au tableau de bord"
          onPress={() => router.replace('/(tabs)/dashboard')}
          style={styles.button}
        />
        <Button
          title="Réessayer le paiement"
          onPress={() => router.replace('/(tabs)/dashboard')}
          variant="outline"
          style={styles.retryButton}
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
  infoBox: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 32,
  },
  infoText: {
    color: '#ccc',
    fontSize: 14,
    marginLeft: 12,
    flex: 1,
    lineHeight: 20,
  },
  button: {
    width: '100%',
    marginBottom: 12,
  },
  retryButton: {
    width: '100%',
  },
});
