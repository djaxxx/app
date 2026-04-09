import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/stores/authStore';
import { api } from '../../src/services/api';
import { DJCard } from '../../src/components/DJCard';
import { SearchBar } from '../../src/components/SearchBar';
import { DJProfile, EventType } from '../../src/types';

export default function TabHomeScreen() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [djs, setDjs] = useState<DJProfile[]>([]);
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [selectedEventType, setSelectedEventType] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [djsResult, typesResult] = await Promise.all([
        api.searchDJs({
          code_postal: searchQuery || undefined,
          type_evenement: selectedEventType || undefined,
        }),
        api.getEventTypes(),
      ]);
      setDjs(djsResult.djs);
      setEventTypes(typesResult);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [searchQuery, selectedEventType]);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const handleDJPress = (djId: string) => {
    router.push(`/dj/${djId}`);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#8B5CF6" />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>DJ Match</Text>
          <Text style={styles.subtitle}>Trouvez votre DJ</Text>
        </View>

        {/* Search */}
        <View style={styles.searchSection}>
          <SearchBar
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Rechercher par ville..."
          />
        </View>

        {/* Event Type Filters */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.filtersScroll}
          contentContainerStyle={styles.filtersContainer}
        >
          <TouchableOpacity
            style={[styles.filterChip, !selectedEventType && styles.filterChipActive]}
            onPress={() => setSelectedEventType(null)}
          >
            <Text style={[styles.filterChipText, !selectedEventType && styles.filterChipTextActive]}>
              Tous
            </Text>
          </TouchableOpacity>
          {eventTypes.map((type) => (
            <TouchableOpacity
              key={type.id}
              style={[styles.filterChip, selectedEventType === type.id && styles.filterChipActive]}
              onPress={() => setSelectedEventType(type.id)}
            >
              <Text style={[styles.filterChipText, selectedEventType === type.id && styles.filterChipTextActive]}>
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* DJ List */}
        <View style={styles.djListSection}>
          {loading ? (
            <ActivityIndicator size="large" color="#8B5CF6" style={styles.loader} />
          ) : djs.length > 0 ? (
            djs.map((dj) => (
              <DJCard key={dj.user_id} dj={dj} onPress={() => handleDJPress(dj.user_id)} />
            ))
          ) : (
            <View style={styles.emptyState}>
              <Ionicons name="musical-notes-outline" size={64} color="#444" />
              <Text style={styles.emptyStateText}>Aucun DJ trouvé</Text>
              <Text style={styles.emptyStateSubtext}>
                Essayez de modifier vos filtres
              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#8B5CF6',
    fontWeight: '600',
    marginTop: 2,
  },
  searchSection: {
    paddingHorizontal: 20,
  },
  filtersScroll: {
    marginVertical: 16,
  },
  filtersContainer: {
    paddingHorizontal: 20,
  },
  filterChip: {
    backgroundColor: '#12123A',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  filterChipActive: {
    backgroundColor: '#8B5CF6',
    borderColor: '#8B5CF6',
  },
  filterChipText: {
    color: '#888',
    fontSize: 14,
  },
  filterChipTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  djListSection: {
    paddingHorizontal: 20,
    paddingTop: 8,
  },
  loader: {
    marginVertical: 40,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyStateText: {
    fontSize: 18,
    color: '#666',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#444',
    marginTop: 8,
    textAlign: 'center',
  },
});
