import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  Image,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
// LinearGradient removed for simplicity
import { useAuthStore } from '../src/stores/authStore';
import { api } from '../src/services/api';
import { DJCard } from '../src/components/DJCard';
import { SearchBar } from '../src/components/SearchBar';
import { Button } from '../src/components/Button';
import { DJProfile, EventType } from '../src/types';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [djs, setDjs] = useState<DJProfile[]>([]);
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [selectedEventType, setSelectedEventType] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const requestIdRef = useRef(0);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadData = async (query?: string, eventType?: string | null) => {
    const currentRequestId = ++requestIdRef.current;
    try {
      const effectiveQuery = query !== undefined ? query : searchQuery;
      const effectiveEventType = eventType !== undefined ? eventType : selectedEventType;
      const [djsResult, typesResult] = await Promise.all([
        api.searchDJs({
          code_postal: effectiveQuery || undefined,
          type_evenement: effectiveEventType || undefined,
        }),
        api.getEventTypes(),
      ]);
      // Only update state if this is still the latest request
      if (currentRequestId === requestIdRef.current) {
        setDjs(djsResult.djs);
        setEventTypes(typesResult);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      if (currentRequestId === requestIdRef.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  };

  // Initial load
  useEffect(() => {
    loadData('', null);
  }, []);

  // Debounced search when query changes, instant for event type filter
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    setLoading(true);
    // Instant search for event type changes, debounced for text input
    const delay = searchQuery.length > 0 ? 500 : 0;
    debounceTimerRef.current = setTimeout(() => {
      loadData(searchQuery, selectedEventType);
    }, delay);
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchQuery, selectedEventType]);

  const onRefresh = () => {
    setRefreshing(true);
    loadData(searchQuery, selectedEventType);
  };

  const handleLogin = () => {
    router.push('/auth/login');
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
        <View style={styles.topBar}>
          <View style={styles.topBarSpacer} />
          {isAuthenticated ? (
            <TouchableOpacity onPress={() => router.push('/(tabs)/profile')}>
              <View style={styles.avatarContainer}>
                <Ionicons name="person-circle" size={40} color="#8B5CF6" />
              </View>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.djRegisterButton} onPress={handleLogin}>
              <Text style={styles.djRegisterButtonText}>🎧 S'inscrire comme DJ</Text>
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.logoContainer}>
          <Image
            source={{ uri: 'https://customer-assets.emergentagent.com/job_dj-directory-fr/artifacts/3rs1w5vv_Logo%20vibrant%20de%20DJ%20Match.png' }}
            style={styles.logoImage}
            resizeMode="contain"
          />
        </View>

        <View style={styles.heroSection}>
          <Text style={styles.heroAnnuaire}>
            L'annuaire des DJ professionnels en France
          </Text>
          <Text style={styles.heroTitle}>
            Trouvez le DJ parfait{'\n'}
            <Text style={styles.heroHighlight}>pour votre evenement</Text>
          </Text>
          <Text style={styles.heroSubtitle}>
            Une plateforme dediee aux DJ declares, assures et experimentes.{'\n'}
            Un gage de qualite pour des prestations a la hauteur de vos attentes.
          </Text>
        </View>

        {/* Trust Badges */}
        <View style={styles.trustSection}>
          <View style={styles.trustRow}>
            <View style={styles.trustBadge}>
              <Text style={styles.trustEmoji}>⭐</Text>
              <Text style={styles.trustText}>Note moyenne{'\n'}5/5</Text>
            </View>
            <View style={styles.trustBadge}>
              <Text style={styles.trustEmoji}>✅</Text>
              <Text style={styles.trustText}>DJ Pro Vérifiés{'\n'}SIRET / ASSURANCE</Text>
            </View>
          </View>
          <View style={styles.trustRow}>
            <View style={styles.trustBadge}>
              <Text style={styles.trustEmoji}>🎉</Text>
              <Text style={styles.trustText}>Annuaire Gratuit{'\n'}pour client</Text>
            </View>
            <View style={styles.trustBadge}>
              <Text style={styles.trustEmoji}>🔒</Text>
              <Text style={styles.trustText}>Paiement{'\n'}sécurisé</Text>
            </View>
          </View>
        </View>

        {/* Search - PROMINENT */}
        <View style={styles.searchSection}>
          <View style={styles.searchLabel}>
            <Ionicons name="location" size={20} color="#8B5CF6" />
            <Text style={styles.searchLabelText}>Trouvez votre DJ</Text>
          </View>
          <View style={styles.searchBoxWrapper}>
            <View style={styles.searchIconCircle}>
              <Ionicons name="search" size={22} color="#fff" />
            </View>
            <TextInput
              style={styles.searchBoxInput}
              value={searchQuery}
              onChangeText={setSearchQuery}
              placeholder="Indiquez le code postal de votre evenement"
              placeholderTextColor="#9CA3AF"
              keyboardType="numeric"
              maxLength={5}
              returnKeyType="search"
            />
            {searchQuery.length > 0 && (
              <TouchableOpacity onPress={() => setSearchQuery('')} style={styles.searchClearBtn}>
                <Ionicons name="close-circle" size={22} color="#888" />
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Map CTA Button */}
        <TouchableOpacity
          style={styles.mapCTAButton}
          onPress={() => router.push('/(tabs)/map')}
          activeOpacity={0.8}
        >
          <View style={styles.mapCTAContent}>
            <Ionicons name="map" size={24} color="#fff" />
            <View style={styles.mapCTATextContainer}>
              <Text style={styles.mapCTATitle}>Carte de France des DJs</Text>
              <Text style={styles.mapCTASubtitle}>Voir tous les DJs près de chez vous</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color="#fff" />
          </View>
        </TouchableOpacity>

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
          <Text style={styles.sectionTitle}>DJs disponibles près de chez vous !</Text>
          
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
                Essayez de modifier vos filtres ou revenez plus tard
              </Text>
            </View>
          )}
        </View>

        {/* CTA for DJs */}
        {!user?.is_dj && (
          <View style={styles.ctaSection}>
            <Text style={styles.ctaTitle}>Vous êtes DJ professionnel ?</Text>
            <Text style={styles.ctaSubtitle}>
              Rejoignez la plateforme et trouvez de nouveaux clients
            </Text>
            <Button
              title="Créer mon profil DJ"
              onPress={() => isAuthenticated ? router.push('/dj-register') : handleLogin()}
              style={styles.ctaButton}
            />
          </View>
        )}

        <View style={styles.footer}>
          <Text style={styles.footerText}>© 2025 DJ Match France</Text>
          <Text style={styles.footerCredit}>Créé par Adrien SEBERT</Text>
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
    paddingVertical: 12,
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 12,
  },
  topBarSpacer: {
    flex: 1,
  },
  logoContainer: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  heroSection: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  heroAnnuaire: {
    fontSize: 13,
    fontWeight: '700',
    color: '#8B5CF6',
    textTransform: 'uppercase',
    letterSpacing: 1.5,
    marginBottom: 12,
    textAlign: 'center',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    paddingVertical: 6,
    paddingHorizontal: 16,
    borderRadius: 20,
    overflow: 'hidden',
  },
  heroTitle: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    lineHeight: 34,
  },
  heroHighlight: {
    color: '#8B5CF6',
  },
  heroSubtitle: {
    fontSize: 14,
    color: '#aaa',
    textAlign: 'center',
    marginTop: 10,
    lineHeight: 22,
    paddingHorizontal: 10,
  },
  trustSection: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  trustRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  trustBadge: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12123A',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 12,
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  trustEmoji: {
    fontSize: 22,
    marginRight: 8,
  },
  trustText: {
    color: '#ccc',
    fontSize: 12,
    fontWeight: '600',
    lineHeight: 16,
    flex: 1,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoImage: {
    width: 320,
    height: 320,
    borderRadius: 32,
  },
  logo: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#8B5CF6',
    fontWeight: '600',
  },
  avatarContainer: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginButton: {
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  loginButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  djRegisterButton: {
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 24,
  },
  djRegisterButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 15,
  },
  searchSection: {
    paddingHorizontal: 20,
    marginBottom: 4,
  },
  searchLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 10,
  },
  searchLabelText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '800',
  },
  searchBoxWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(139, 92, 246, 0.08)',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#8B5CF6',
    paddingHorizontal: 4,
    height: 58,
  },
  searchIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#8B5CF6',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  searchBoxInput: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
    height: '100%',
  },
  searchClearBtn: {
    padding: 8,
  },
  mapCTAButton: {
    marginHorizontal: 20,
    marginTop: 16,
    backgroundColor: '#8B5CF6',
    borderRadius: 16,
    overflow: 'hidden',
  },
  mapCTAContent: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
  },
  mapCTATextContainer: {
    flex: 1,
    marginLeft: 12,
  },
  mapCTATitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  mapCTASubtitle: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 12,
    marginTop: 2,
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
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
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
  ctaSection: {
    backgroundColor: '#12123A',
    marginHorizontal: 20,
    marginVertical: 24,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  ctaTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  ctaSubtitle: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  ctaButton: {
    width: '100%',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    color: '#444',
    fontSize: 12,
  },
  footerCredit: {
    color: '#8B5CF6',
    fontSize: 11,
    marginTop: 4,
  },
});
