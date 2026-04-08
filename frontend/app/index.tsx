import React, { useEffect, useState } from 'react';
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

  const loadData = async () => {
    try {
      const [djsResult, typesResult] = await Promise.all([
        api.searchDJs({
          ville: searchQuery || undefined,
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

  const handleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = typeof window !== 'undefined' 
      ? `${window.location.origin}/auth/callback`
      : '';
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
    
    if (typeof window !== 'undefined') {
      window.location.href = authUrl;
    }
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
            <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
              <Text style={styles.loginButtonText}>Connexion</Text>
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
          <Text style={styles.heroTitle}>
            Trouvez le DJ parfait{'\n'}
            <Text style={styles.heroHighlight}>pour votre événement</Text>
          </Text>
          <Text style={styles.heroSubtitle}>
            DJs professionnels vérifiés pour mariages, anniversaires, soirées privées et entreprises
          </Text>
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
          <Text style={styles.sectionTitle}>DJs Disponibles</Text>
          
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
    backgroundColor: '#0c0c0c',
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
    color: '#888',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20,
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
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#2a2a2a',
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
    backgroundColor: '#1a1a1a',
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
