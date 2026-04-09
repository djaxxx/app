import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function ZoneSuccessScreen() {
  const router = useRouter();
  const { dept } = useLocalSearchParams();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconCircle}>
          <Ionicons name="map" size={48} color="#10B981" />
        </View>
        <Text style={styles.title}>Zone étendue !</Text>
        <Text style={styles.subtitle}>
          Le département {dept || ''} a été ajouté à votre zone d'intervention.{"\n"}
          Vous apparaissez maintenant dans les recherches de ce département.
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.replace('/zone-management')}
        >
          <Text style={styles.buttonText}>Voir ma zone</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0B0B24', justifyContent: 'center' },
  content: { alignItems: 'center', paddingHorizontal: 40 },
  iconCircle: { width: 96, height: 96, borderRadius: 48, backgroundColor: 'rgba(16,185,129,0.15)', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#10B981', textAlign: 'center', marginBottom: 12 },
  subtitle: { fontSize: 16, color: '#999', textAlign: 'center', lineHeight: 24, marginBottom: 32 },
  button: { backgroundColor: '#8B5CF6', paddingHorizontal: 32, paddingVertical: 16, borderRadius: 12 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
