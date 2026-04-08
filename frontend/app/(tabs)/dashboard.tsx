import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/stores/authStore';
import { api } from '../../src/services/api';
import { Button } from '../../src/components/Button';

export default function DashboardScreen() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboard = async () => {
    if (!isAuthenticated || !user?.is_dj) {
      setLoading(false);
      return;
    }

    try {
      const data = await api.getDJDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [isAuthenticated, user]);

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  const handleSubscribe = async () => {
    try {
      const originUrl = typeof window !== 'undefined' ? window.location.origin : '';
      const result = await api.createSubscriptionCheckout(originUrl);
      if (typeof window !== 'undefined' && result.checkout_url) {
        window.location.href = result.checkout_url;
      }
    } catch (error) {
      console.error('Subscription error:', error);
    }
  };

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.notAuthContainer}>
          <Ionicons name="lock-closed" size={64} color="#444" />
          <Text style={styles.notAuthText}>Connexion requise</Text>
          <Text style={styles.notAuthSubtext}>
            Connectez-vous pour accéder au tableau de bord
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!user?.is_dj) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.notAuthContainer}>
          <Ionicons name="musical-notes" size={64} color="#444" />
          <Text style={styles.notAuthText}>Profil DJ requis</Text>
          <Text style={styles.notAuthSubtext}>
            Créez votre profil DJ pour accéder au tableau de bord
          </Text>
          <Button
            title="Créer mon profil"
            onPress={() => router.push('/dj-register')}
            style={styles.createButton}
          />
        </View>
      </SafeAreaView>
    );
  }

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#8B5CF6" style={styles.loader} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#8B5CF6" />
        }
      >
        <View style={styles.header}>
          <Text style={styles.title}>Tableau de bord</Text>
          {dashboard?.badge_verifie && (
            <View style={styles.badge}>
              <Ionicons name="checkmark-circle" size={16} color="#fff" />
              <Text style={styles.badgeText}>Vérifié</Text>
            </View>
          )}
        </View>

        {/* Subscription Status */}
        {dashboard?.subscription_status !== 'active' && (
          <View style={styles.subscriptionAlert}>
            <Ionicons name="warning" size={24} color="#F59E0B" />
            <View style={styles.subscriptionAlertContent}>
              <Text style={styles.subscriptionAlertTitle}>Abonnement inactif</Text>
              <Text style={styles.subscriptionAlertText}>
                Votre profil n'est pas visible. Activez votre abonnement (5€/mois)
              </Text>
            </View>
            <Button
              title="S'abonner"
              onPress={handleSubscribe}
              style={styles.subscribeButton}
            />
          </View>
        )}

        {/* Stats Cards */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Ionicons name="eye" size={32} color="#8B5CF6" />
            <Text style={styles.statValue}>{dashboard?.nombre_vues || 0}</Text>
            <Text style={styles.statLabel}>Vues du profil</Text>
          </View>

          <View style={styles.statCard}>
            <Ionicons name="mail" size={32} color="#10B981" />
            <Text style={styles.statValue}>{dashboard?.nombre_demandes || 0}</Text>
            <Text style={styles.statLabel}>Demandes</Text>
            {dashboard?.demandes_non_lues > 0 && (
              <View style={styles.notificationBadge}>
                <Text style={styles.notificationText}>{dashboard.demandes_non_lues}</Text>
              </View>
            )}
          </View>

          <View style={styles.statCard}>
            <Ionicons name="star" size={32} color="#F59E0B" />
            <Text style={styles.statValue}>{dashboard?.note_moyenne?.toFixed(1) || '0.0'}</Text>
            <Text style={styles.statLabel}>{dashboard?.nombre_avis || 0} avis</Text>
          </View>

          <View style={styles.statCard}>
            <Ionicons name="checkmark-circle" size={32} color="#3B82F6" />
            <Text style={styles.statValue}>{dashboard?.profil_complete_percent || 0}%</Text>
            <Text style={styles.statLabel}>Profil complet</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Actions rapides</Text>
          
          <TouchableOpacity
            style={styles.actionItem}
            onPress={() => router.push('/(tabs)/profile')}
          >
            <Ionicons name="person" size={24} color="#8B5CF6" />
            <Text style={styles.actionText}>Éditer mon profil</Text>
            <Ionicons name="chevron-forward" size={24} color="#666" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="mail" size={24} color="#10B981" />
            <Text style={styles.actionText}>Mes demandes de contact</Text>
            <Ionicons name="chevron-forward" size={24} color="#666" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionItem}>
            <Ionicons name="star" size={24} color="#F59E0B" />
            <Text style={styles.actionText}>Mes avis clients</Text>
            <Ionicons name="chevron-forward" size={24} color="#666" />
          </TouchableOpacity>
        </View>

        {/* Recent Reviews */}
        {dashboard?.recent_reviews && dashboard.recent_reviews.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Derniers avis</Text>
            {dashboard.recent_reviews.map((review: any) => (
              <View key={review.review_id} style={styles.reviewCard}>
                <View style={styles.reviewHeader}>
                  <Text style={styles.reviewAuthor}>{review.client_nom}</Text>
                  <View style={styles.reviewStars}>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Ionicons
                        key={star}
                        name={star <= review.note ? 'star' : 'star-outline'}
                        size={14}
                        color="#FFD700"
                      />
                    ))}
                  </View>
                </View>
                <Text style={styles.reviewText} numberOfLines={2}>
                  {review.commentaire}
                </Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0c0c0c',
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  badge: {
    backgroundColor: '#8B5CF6',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  subscriptionAlert: {
    backgroundColor: '#1a1a1a',
    marginHorizontal: 20,
    padding: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F59E0B',
  },
  subscriptionAlertContent: {
    flex: 1,
    marginLeft: 12,
  },
  subscriptionAlertTitle: {
    color: '#F59E0B',
    fontSize: 16,
    fontWeight: '600',
  },
  subscriptionAlertText: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  subscribeButton: {
    paddingHorizontal: 16,
    height: 40,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    marginTop: 20,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    marginHorizontal: '1%',
    alignItems: 'center',
    position: 'relative',
  },
  statValue: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  notificationBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#EF4444',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  section: {
    paddingHorizontal: 20,
    marginTop: 24,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  actionItem: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  actionText: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    marginLeft: 12,
  },
  reviewCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
  },
  reviewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  reviewAuthor: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  reviewStars: {
    flexDirection: 'row',
  },
  reviewText: {
    color: '#888',
    fontSize: 14,
    lineHeight: 20,
  },
  notAuthContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  notAuthText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
    marginTop: 16,
  },
  notAuthSubtext: {
    color: '#888',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
  },
  createButton: {
    marginTop: 24,
    width: '100%',
  },
});
