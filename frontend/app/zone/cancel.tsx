import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function ZoneCancelScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconCircle}>
          <Ionicons name="close-circle" size={48} color="#EF4444" />
        </View>
        <Text style={styles.title}>Paiement annulé</Text>
        <Text style={styles.subtitle}>
          L'extension de zone a été annulée.{"\n"}
          Vous pouvez réessayer quand vous le souhaitez.
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.replace('/zone-management')}
        >
          <Text style={styles.buttonText}>Retour à ma zone</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0B0B24', justifyContent: 'center' },
  content: { alignItems: 'center', paddingHorizontal: 40 },
  iconCircle: { width: 96, height: 96, borderRadius: 48, backgroundColor: 'rgba(239,68,68,0.15)', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#EF4444', textAlign: 'center', marginBottom: 12 },
  subtitle: { fontSize: 16, color: '#999', textAlign: 'center', lineHeight: 24, marginBottom: 32 },
  button: { backgroundColor: '#8B5CF6', paddingHorizontal: 32, paddingVertical: 16, borderRadius: 12 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
