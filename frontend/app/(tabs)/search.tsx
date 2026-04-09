import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../src/services/api';
import { DJCard } from '../../src/components/DJCard';
import { SearchBar } from '../../src/components/SearchBar';
import { Button } from '../../src/components/Button';
import { DJProfile, EventType } from '../../src/types';

export default function SearchScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [djs, setDjs] = useState<DJProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    verifie_uniquement: false,
    note_min: 0,
  });

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const result = await api.searchDJs({
        ville: searchQuery,
        verifie_uniquement: filters.verifie_uniquement,
        note_min: filters.note_min > 0 ? filters.note_min : undefined,
      });
      setDjs(result.djs);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDJPress = (djId: string) => {
    router.push(`/dj/${djId}`);
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Rechercher un DJ</Text>
      </View>

      <View style={styles.searchSection}>
        <SearchBar
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Ville, département..."
          onFilter={() => setShowFilters(!showFilters)}
        />
        
        <Button
          title="Rechercher"
          onPress={handleSearch}
          loading={loading}
          style={styles.searchButton}
        />
      </View>

      {showFilters && (
        <View style={styles.filtersSection}>
          <TouchableOpacity
            style={styles.filterOption}
            onPress={() => setFilters(f => ({ ...f, verifie_uniquement: !f.verifie_uniquement }))}
          >
            <Ionicons
              name={filters.verifie_uniquement ? 'checkbox' : 'square-outline'}
              size={24}
              color="#8B5CF6"
            />
            <Text style={styles.filterOptionText}>DJs vérifiés uniquement</Text>
          </TouchableOpacity>

          <View style={styles.ratingFilter}>
            <Text style={styles.filterLabel}>Note minimum:</Text>
            <View style={styles.ratingButtons}>
              {[0, 3, 4, 4.5].map((rating) => (
                <TouchableOpacity
                  key={rating}
                  style={[
                    styles.ratingButton,
                    filters.note_min === rating && styles.ratingButtonActive,
                  ]}
                  onPress={() => setFilters(f => ({ ...f, note_min: rating }))}
                >
                  <Text style={[
                    styles.ratingButtonText,
                    filters.note_min === rating && styles.ratingButtonTextActive,
                  ]}>
                    {rating === 0 ? 'Tous' : `${rating}+`}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
      )}

      <ScrollView style={styles.results}>
        {loading ? (
          <ActivityIndicator size="large" color="#8B5CF6" style={styles.loader} />
        ) : djs.length > 0 ? (
          <View style={styles.djList}>
            <Text style={styles.resultsCount}>{djs.length} résultat(s)</Text>
            {djs.map((dj) => (
              <DJCard key={dj.user_id} dj={dj} onPress={() => handleDJPress(dj.user_id)} />
            ))}
          </View>
        ) : searchQuery ? (
          <View style={styles.emptyState}>
            <Ionicons name="search" size={64} color="#444" />
            <Text style={styles.emptyStateText}>Aucun résultat</Text>
            <Text style={styles.emptyStateSubtext}>
              Essayez une autre recherche
            </Text>
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Ionicons name="location" size={64} color="#444" />
            <Text style={styles.emptyStateText}>Recherchez par ville</Text>
            <Text style={styles.emptyStateSubtext}>
              Entrez une ville pour trouver des DJs
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  searchSection: {
    paddingHorizontal: 20,
  },
  searchButton: {
    marginTop: 12,
  },
  filtersSection: {
    backgroundColor: '#12123A',
    marginHorizontal: 20,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
  },
  filterOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  filterOptionText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 12,
  },
  ratingFilter: {
    marginTop: 16,
  },
  filterLabel: {
    color: '#888',
    fontSize: 14,
    marginBottom: 8,
  },
  ratingButtons: {
    flexDirection: 'row',
  },
  ratingButton: {
    backgroundColor: '#1E1E4A',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    marginRight: 8,
  },
  ratingButtonActive: {
    backgroundColor: '#8B5CF6',
  },
  ratingButtonText: {
    color: '#888',
    fontSize: 14,
  },
  ratingButtonTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  results: {
    flex: 1,
    marginTop: 16,
  },
  djList: {
    paddingHorizontal: 20,
  },
  resultsCount: {
    color: '#888',
    fontSize: 14,
    marginBottom: 16,
  },
  loader: {
    marginTop: 40,
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
