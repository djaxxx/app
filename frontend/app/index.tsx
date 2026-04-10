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
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
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
            source={{ uri: 'https://customer-assets.emergentagent.com/job_dj-directory-fr/artifacts/rk4zakc5_Logo%20DJ%20MATCH%20avec%20%C3%A9couteurs%20stylis%C3%A9s.png' }}
            style={styles.logoImage}
            resizeMode="contain"
          />
        </View>

        <View style={styles.heroSection}>
          <Text style={styles.heroTitle}>
            Trouvez votre DJ PRO{'\n'}
            <Text style={styles.heroHighlight}>en 2 minutes chrono⏱️</Text>
          </Text>
          <Text style={styles.heroSubtitle}>
            Mariage, Anniversaire, Soiree... Trouvez votre DJ, declare, recommande pres de chez vous ! 🏅
          </Text>
        </View>

        {/* Trust Badges - 3 blocs */}
        <View style={styles.trustSection}>
          <View style={styles.trustRow3}>
            <View style={styles.trustBadge3}>
              <Text style={styles.trustEmoji}>✅</Text>
              <Text style={styles.trustText3}>DJ verifies avec SIRET et Assurance</Text>
            </View>
            <View style={styles.trustBadge3}>
              <Text style={styles.trustEmoji}>✨</Text>
              <Text style={styles.trustText3}>Avis clients Reel</Text>
            </View>
            <View style={styles.trustBadge3}>
              <Text style={styles.trustEmoji}>🛡️</Text>
              <Text style={styles.trustText3}>Reservation simple</Text>
            </View>
          </View>
        </View>

        {/* Search - GLASSMORPHISM DESIGN */}
        <View style={styles.searchSection}>
          {/* CTA Button - Neon border, neutral interior */}
          <View style={styles.ctaGlassOuter}>
            <View style={styles.ctaGlassInner}>
              <Text style={styles.ctaGlassEmoji}>🔥</Text>
              <Text style={styles.ctaGlassText} numberOfLines={1} adjustsFontSizeToFit>Trouver mon DJ maintenant</Text>
            </View>
          </View>

          {/* Search Bar - Glassmorphism */}
          <View style={styles.searchGlassOuter}>
            <View style={styles.searchGlassInner}>
              <Ionicons name="location-sharp" size={20} color="#A78BFA" style={styles.searchGlassIcon} />
              <TextInput
                style={styles.searchGlassInput}
                value={searchQuery}
                onChangeText={setSearchQuery}
                placeholder="Code postal de votre événement"
                placeholderTextColor="rgba(255,255,255,0.45)"
                keyboardType="numeric"
                maxLength={5}
                returnKeyType="search"
              />
              {searchQuery.length > 0 ? (
                <TouchableOpacity onPress={() => setSearchQuery('')} style={styles.searchGlassClearBtn}>
                  <Ionicons name="close-circle" size={22} color="#888" />
                </TouchableOpacity>
              ) : (
                <Ionicons name="search" size={20} color="#A78BFA" style={styles.searchGlassSearchIcon} />
              )}
            </View>
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
    paddingTop: 0,
  },
  topBarSpacer: {
    flex: 1,
  },
  logoContainer: {
    alignItems: 'center',
    paddingTop: 0,
    paddingBottom: 0,
    marginBottom: -50,
  },
  heroSection: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 4,
  },
  heroAnnuaire: {
    alignItems: 'center',
    marginBottom: 12,
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    paddingVertical: 8,
    paddingHorizontal: 20,
    borderRadius: 20,
    overflow: 'hidden',
  },
  heroAnnuaireText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#8B5CF6',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    textAlign: 'center',
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
  trustRow3: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  trustBadge3: {
    flex: 1,
    backgroundColor: 'rgba(139, 92, 246, 0.08)',
    borderRadius: 14,
    padding: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.15)',
  },
  trustEmoji: {
    fontSize: 24,
    marginBottom: 6,
  },
  trustText3: {
    color: '#ddd',
    fontSize: 11,
    fontWeight: '600',
    textAlign: 'center',
    lineHeight: 15,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoImage: {
    width: 850,
    height: 850,
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
    marginBottom: 16,
    gap: 12,
  },
  // CTA Button - Neon border, neutral interior
  ctaGlassOuter: {
    borderRadius: 30,
    borderWidth: 2,
    borderColor: '#A78BFA',
    backgroundColor: 'rgba(15, 15, 40, 0.85)',
    paddingVertical: 18,
    paddingHorizontal: 16,
    ...Platform.select({
      web: {
        boxShadow: '0 0 12px rgba(167, 139, 250, 0.6), 0 0 30px rgba(139, 92, 246, 0.3), 0 0 60px rgba(139, 92, 246, 0.12), inset 0 0 12px rgba(139, 92, 246, 0.08)',
      },
      default: {},
    }),
  },
  ctaGlassGradient: {
    borderRadius: 28,
    paddingVertical: 20,
    paddingHorizontal: 24,
  },
  ctaGlassInner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  ctaGlassEmoji: {
    fontSize: 22,
    marginRight: 8,
  },
  ctaGlassText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
  // Search Bar - Glassmorphism
  searchGlassOuter: {
    borderRadius: 30,
    borderWidth: 1.5,
    borderColor: 'rgba(167, 139, 250, 0.35)',
    overflow: 'hidden',
    ...Platform.select({
      web: {
        boxShadow: '0 0 18px rgba(139, 92, 246, 0.22), 0 0 40px rgba(139, 92, 246, 0.08)',
      },
      default: {},
    }),
  },
  searchGlassInner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(91, 33, 182, 0.22)',
    borderRadius: 28,
    paddingVertical: 16,
    paddingHorizontal: 20,
  },
  searchGlassIcon: {
    marginRight: 12,
  },
  searchGlassInput: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
    paddingVertical: 0,
  },
  searchGlassSearchIcon: {
    marginLeft: 12,
  },
  searchGlassClearBtn: {
    marginLeft: 8,
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
