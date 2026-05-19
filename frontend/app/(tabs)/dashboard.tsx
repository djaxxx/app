import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/stores/authStore';
import { api } from '../../src/services/api';
import { Button } from '../../src/components/Button';

export default function DashboardScreen() {
  const { user, isAuthenticated } = useAuthStore();
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'annual'>('monthly');
  const [subscribing, setSubscribing] = useState(false);

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

  // Refresh dashboard on mount and when auth state changes
  useEffect(() => {
    loadDashboard();
  }, [isAuthenticated, user]);

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  const handleSubscribe = async (plan: 'monthly' | 'annual') => {
    try {
      setSubscribing(true);
      // On web: use current origin. On native (Android): use public web URL as Stripe redirect base.
      const PUBLIC_WEB_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://dj-directory-fr.preview.emergentagent.com';
      const originUrl = Platform.OS === 'web' && typeof window !== 'undefined'
        ? window.location.origin
        : PUBLIC_WEB_URL;
      const result = await api.createSubscriptionCheckout(originUrl, plan);
      if (Platform.OS === 'web' && typeof window !== 'undefined' && result.checkout_url) {
        window.location.href = result.checkout_url;
      } else if (result.checkout_url) {
        const Linking = require('expo-linking');
        Linking.openURL(result.checkout_url);
      }
    } catch (error: any) {
      console.error('Subscription error:', error);
      const Alert = require('react-native').Alert;
      Alert.alert('Erreur paiement', error?.message || 'Impossible de démarrer le paiement. Réessayez ou contactez le support.');
    } finally {
      setSubscribing(false);
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

        {/* Lock Screen for Expired Trial DJs */}
        {dashboard?.is_locked ? (
          <View style={styles.lockedContainer}>
            <View style={styles.lockIconContainer}>
              <Ionicons name="time-outline" size={48} color="#F59E0B" />
            </View>
            <Text style={styles.lockedTitle}>Essai gratuit termine</Text>
            <Text style={styles.lockedMessage}>
              {dashboard.lock_message || "Votre essai gratuit de 15 jours est termine. Choisissez une formule pour rester visible sur la plateforme."}
            </Text>

            <View style={styles.lockedBenefits}>
              <View style={styles.benefitRow}>
                <Ionicons name="checkmark-circle" size={20} color="#8B5CF6" />
                <Text style={styles.benefitText}>Visible sur la carte et dans les recherches</Text>
              </View>
              <View style={styles.benefitRow}>
                <Ionicons name="checkmark-circle" size={20} color="#8B5CF6" />
                <Text style={styles.benefitText}>Recevez des demandes de contact clients</Text>
              </View>
              <View style={styles.benefitRow}>
                <Ionicons name="checkmark-circle" size={20} color="#8B5CF6" />
                <Text style={styles.benefitText}>Statistiques détaillées de votre profil</Text>
              </View>
              <View style={styles.benefitRow}>
                <Ionicons name="checkmark-circle" size={20} color="#8B5CF6" />
                <Text style={styles.benefitText}>Badge vérifié et mise en avant</Text>
              </View>
            </View>

            {Platform.OS === 'ios' ? (
              <View style={styles.iosNoticeBox}>
                <Ionicons name="information-circle" size={24} color="#6366F1" />
                <Text style={styles.iosNoticeText}>
                  L'abonnement n'est pas disponible depuis l'application iOS. Vous pouvez gérer votre abonnement depuis un navigateur sur ordinateur.
                </Text>
              </View>
            ) : (
            <View style={styles.subscriptionSection}>
              <Text style={styles.subscriptionChoiceTitle}>Choisissez votre formule</Text>

              <View style={styles.plansContainer}>
                <TouchableOpacity
                  style={[
                    styles.planCard,
                    selectedPlan === 'monthly' && styles.planCardSelected,
                  ]}
                  onPress={() => setSelectedPlan('monthly')}
                >
                  <View style={styles.planHeader}>
                    <Text style={styles.planName}>Mensuel</Text>
                    {selectedPlan === 'monthly' && (
                      <Ionicons name="checkmark-circle" size={20} color="#8B5CF6" />
                    )}
                  </View>
                  <Text style={styles.planPrice}>8€</Text>
                  <Text style={styles.planPeriod}>par mois</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[
                    styles.planCard,
                    selectedPlan === 'annual' && styles.planCardSelected,
                  ]}
                  onPress={() => setSelectedPlan('annual')}
                >
                  <View style={styles.planBadge}>
                    <Text style={styles.planBadgeText}>-17%</Text>
                  </View>
                  <View style={styles.planHeader}>
                    <Text style={styles.planName}>Annuel</Text>
                    {selectedPlan === 'annual' && (
                      <Ionicons name="checkmark-circle" size={20} color="#8B5CF6" />
                    )}
                  </View>
                  <Text style={styles.planPrice}>80€</Text>
                  <Text style={styles.planPeriod}>par an</Text>
                  <Text style={styles.planSaving}>Économisez 16€</Text>
                </TouchableOpacity>
              </View>

              <Button
                title={subscribing ? 'Chargement...' : `S'abonner (${selectedPlan === 'monthly' ? '8€/mois' : '80€/an'})`}
                onPress={() => handleSubscribe(selectedPlan)}
                loading={subscribing}
                style={styles.subscribeButton}
              />
            </View>
            )}

            {/* Limited: Edit Profile only */}
            <TouchableOpacity
              style={styles.editProfileLocked}
              onPress={() => router.push('/edit-profile')}
            >
              <Ionicons name="create-outline" size={20} color="#8B5CF6" />
              <Text style={styles.editProfileLockedText}>Modifier mon profil</Text>
              <Ionicons name="chevron-forward" size={20} color="#666" />
            </TouchableOpacity>
          </View>
        ) : (
          <>
            {/* Trial Banner */}
            {dashboard?.is_trial ? (
              <>
                {/* Urgent warning for last 5 days */}
                {dashboard.trial_days_remaining <= 5 ? (
                  <View style={styles.trialUrgentBanner}>
                    <View style={styles.trialUrgentTop}>
                      <Ionicons name="warning" size={24} color="#F59E0B" />
                      <Text style={styles.trialUrgentTitle}>
                        {dashboard.trial_days_remaining <= 1
                          ? "Dernier jour d'essai !"
                          : dashboard.trial_days_remaining <= 3
                          ? `Plus que ${dashboard.trial_days_remaining} jours !`
                          : `${dashboard.trial_days_remaining} jours restants`}
                      </Text>
                    </View>
                    <Text style={styles.trialUrgentMessage}>
                      Votre essai gratuit se termine bientot. Choisissez votre forfait maintenant pour rester visible et ne perdre aucune demande client.
                    </Text>
                    {Platform.OS === 'ios' ? (
                      <View style={styles.iosNoticeBox}>
                        <Ionicons name="information-circle" size={20} color="#6366F1" />
                        <Text style={styles.iosNoticeText}>
                          Pour gérer votre abonnement, utilisez un navigateur sur ordinateur.
                        </Text>
                      </View>
                    ) : (
                    <View style={styles.trialUrgentPlans}>
                      <TouchableOpacity
                        style={styles.trialUrgentPlanBtn}
                        onPress={() => {
                          setSelectedPlan('monthly');
                          handleSubscribe('monthly');
                        }}
                      >
                        <Text style={styles.trialUrgentPlanPrice}>8€/mois</Text>
                        <Text style={styles.trialUrgentPlanLabel}>Mensuel</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={[styles.trialUrgentPlanBtn, styles.trialUrgentPlanBtnBest]}
                        onPress={() => {
                          setSelectedPlan('annual');
                          handleSubscribe('annual');
                        }}
                      >
                        <View style={styles.trialUrgentBestBadge}>
                          <Text style={styles.trialUrgentBestBadgeText}>-17%</Text>
                        </View>
                        <Text style={styles.trialUrgentPlanPrice}>80€/an</Text>
                        <Text style={styles.trialUrgentPlanLabel}>Meilleure offre</Text>
                      </TouchableOpacity>
                    </View>
                    )}
                  </View>
                ) : (
                  <>
                  <View style={styles.trialBanner}>
                    <View style={styles.trialBannerIcon}>
                      <Ionicons name="gift-outline" size={24} color="#8B5CF6" />
                    </View>
                    <View style={styles.trialBannerContent}>
                      <Text style={styles.trialBannerTitle}>Essai gratuit en cours</Text>
                      <Text style={styles.trialBannerDays}>
                        {dashboard.trial_days_remaining} jours restants
                      </Text>
                      <Text style={styles.trialBannerSubtext}>
                        Votre profil est visible gratuitement pendant 15 jours
                      </Text>
                    </View>
                  </View>

                  {Platform.OS !== 'ios' && (
                  <View style={styles.earlySubscribeCard}>
                    <View style={styles.earlySubscribeHeader}>
                      <Ionicons name="flash" size={20} color="#8B5CF6" />
                      <Text style={styles.earlySubscribeTitle}>Activer mon compte maintenant</Text>
                    </View>
                    <Text style={styles.earlySubscribeSubtext}>
                      Passez en abonnement pour rester actif sans attendre la fin de l'essai
                    </Text>
                    <View style={styles.earlySubscribePlans}>
                      <TouchableOpacity
                        style={styles.earlyPlanBtn}
                        onPress={() => handleSubscribe('monthly')}
                      >
                        <Text style={styles.earlyPlanPrice}>8€/mois</Text>
                        <Text style={styles.earlyPlanLabel}>Mensuel</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={[styles.earlyPlanBtn, styles.earlyPlanBtnBest]}
                        onPress={() => handleSubscribe('annual')}
                      >
                        <View style={styles.earlyBestBadge}>
                          <Text style={styles.earlyBestBadgeText}>-17%</Text>
                        </View>
                        <Text style={styles.earlyPlanPrice}>80€/an</Text>
                        <Text style={styles.earlyPlanLabel}>Économisez 16€</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                  )}
                  </>
                )}
              </>
            ) : (
              <View style={styles.activeSubBanner}>
                <Ionicons name="checkmark-circle" size={20} color="#10B981" />
                <Text style={styles.activeSubText}>Abonnement actif — Profil visible</Text>
              </View>
            )}

            {/* Stats Cards */}
            <View style={styles.statsGrid}>
              <View style={styles.statCard}>
                <Ionicons name="eye" size={32} color="#8B5CF6" />
                <Text style={styles.statValue}>{dashboard?.nombre_vues || 0}</Text>
                <Text style={styles.statLabel}>Vues du profil</Text>
              </View>

              <TouchableOpacity
                style={styles.statCard}
                onPress={() => router.push('/my-contacts')}
                activeOpacity={0.7}
              >
                <Ionicons name="mail" size={32} color="#10B981" />
                <Text style={styles.statValue}>{dashboard?.nombre_demandes || 0}</Text>
                <Text style={styles.statLabel}>Demandes</Text>
                {(dashboard?.demandes_non_lues ?? 0) > 0 && (
                  <View style={styles.notificationBadge}>
                    <Text style={styles.notificationText}>{dashboard?.demandes_non_lues}</Text>
                  </View>
                )}
              </TouchableOpacity>

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
                onPress={() => router.push('/edit-profile')}
              >
                <Ionicons name="person" size={24} color="#8B5CF6" />
                <Text style={styles.actionText}>Éditer mon profil</Text>
                <Ionicons name="chevron-forward" size={24} color="#666" />
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionItem}
                onPress={() => router.push('/my-contacts')}
              >
                <Ionicons name="mail" size={24} color="#10B981" />
                <Text style={styles.actionText}>Mes demandes de contact</Text>
                {(dashboard?.demandes_non_lues ?? 0) > 0 && (
                  <View style={styles.notificationBadge}>
                    <Text style={styles.notificationText}>{dashboard.demandes_non_lues}</Text>
                  </View>
                )}
                <Ionicons name="chevron-forward" size={24} color="#666" />
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionItem}
                onPress={() => router.push('/zone-management')}
              >
                <Ionicons name="map" size={24} color="#3B82F6" />
                <Text style={styles.actionText}>Zone d'intervention</Text>
                <Ionicons name="chevron-forward" size={24} color="#666" />
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionItem}
                onPress={() => router.push('/manage-reviews')}
              >
                <Ionicons name="star" size={24} color="#F59E0B" />
                <Text style={styles.actionText}>Mes avis clients</Text>
                {(dashboard?.pending_reviews_count ?? 0) > 0 && (
                  <View style={styles.notificationBadge}>
                    <Text style={styles.notificationText}>{dashboard.pending_reviews_count}</Text>
                  </View>
                )}
                <Ionicons name="chevron-forward" size={24} color="#666" />
              </TouchableOpacity>

              {Platform.OS !== 'ios' && (
              <TouchableOpacity
                style={[styles.actionItem, styles.boostActionItem]}
                onPress={() => router.push('/boost')}
              >
                <Ionicons name="rocket" size={24} color="#FFD700" />
                <Text style={[styles.actionText, { color: '#FFD700' }]}>Booster mon profil</Text>
                <View style={styles.boostNewBadge}>
                  <Text style={styles.boostNewBadgeText}>NOUVEAU</Text>
                </View>
                <Ionicons name="chevron-forward" size={24} color="#FFD700" />
              </TouchableOpacity>
              )}
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
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  iosNoticeBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    backgroundColor: '#EEF2FF',
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#C7D2FE',
    marginTop: 12,
  },
  iosNoticeText: {
    flex: 1,
    fontSize: 13,
    color: '#3730A3',
    lineHeight: 18,
  },
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
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
    backgroundColor: '#12123A',
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
  subscriptionSection: {
    backgroundColor: '#12123A',
    marginHorizontal: 20,
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  subscriptionChoiceTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    textAlign: 'center',
  },
  subscriptionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  subscriptionTitle: {
    color: '#F59E0B',
    fontSize: 18,
    fontWeight: '700',
    marginLeft: 8,
  },
  subscriptionSubtitle: {
    color: '#888',
    fontSize: 14,
    marginBottom: 16,
  },
  plansContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  planCard: {
    width: '48%',
    backgroundColor: '#0B0B24',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#1E1E4A',
    position: 'relative',
  },
  planCardSelected: {
    borderColor: '#8B5CF6',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
  },
  planBadge: {
    position: 'absolute',
    top: -10,
    right: -10,
    backgroundColor: '#10B981',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  planBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  planName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 4,
  },
  planPrice: {
    color: '#8B5CF6',
    fontSize: 32,
    fontWeight: 'bold',
  },
  planPeriod: {
    color: '#888',
    fontSize: 14,
  },
  planSaving: {
    color: '#10B981',
    fontSize: 12,
    marginTop: 4,
    fontWeight: '600',
  },
  subscribeButton: {
    marginTop: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    marginTop: 20,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#12123A',
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
    backgroundColor: '#12123A',
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
  boostActionItem: {
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.3)',
    backgroundColor: 'rgba(255, 215, 0, 0.05)',
  },
  boostNewBadge: {
    backgroundColor: '#FFD700',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    marginRight: 8,
  },
  boostNewBadgeText: {
    color: '#000',
    fontSize: 10,
    fontWeight: 'bold',
  },
  reviewCard: {
    backgroundColor: '#12123A',
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
  lockedContainer: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  lockIconContainer: {
    alignItems: 'center',
    marginBottom: 16,
    marginTop: 8,
  },
  lockedTitle: {
    color: '#F59E0B',
    fontSize: 22,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  lockedMessage: {
    color: '#888',
    fontSize: 15,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  lockedBenefits: {
    backgroundColor: '#12123A',
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
  },
  benefitRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
  },
  benefitText: {
    color: '#ccc',
    fontSize: 14,
    marginLeft: 12,
    flex: 1,
  },
  editProfileLocked: {
    backgroundColor: '#12123A',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
  },
  editProfileLockedText: {
    flex: 1,
    color: '#8B5CF6',
    fontSize: 16,
    marginLeft: 12,
    fontWeight: '600',
  },
  activeSubBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    marginHorizontal: 20,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.3)',
  },
  activeSubText: {
    color: '#10B981',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  trialBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    marginHorizontal: 20,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)',
    marginBottom: 8,
  },
  trialBannerIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(139, 92, 246, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  trialBannerContent: {
    flex: 1,
  },
  trialBannerTitle: {
    color: '#8B5CF6',
    fontSize: 16,
    fontWeight: '700',
  },
  trialBannerDays: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 2,
  },
  trialBannerSubtext: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  trialUrgentBanner: {
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    marginHorizontal: 20,
    padding: 18,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'rgba(245, 158, 11, 0.4)',
    marginBottom: 8,
  },
  trialUrgentTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 8,
  },
  trialUrgentTitle: {
    color: '#F59E0B',
    fontSize: 18,
    fontWeight: 'bold',
  },
  trialUrgentMessage: {
    color: '#ccc',
    fontSize: 13,
    lineHeight: 19,
    marginBottom: 16,
  },
  trialUrgentPlans: {
    flexDirection: 'row',
    gap: 10,
  },
  trialUrgentPlanBtn: {
    flex: 1,
    backgroundColor: 'rgba(139, 92, 246, 0.15)',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)',
  },
  trialUrgentPlanBtnBest: {
    backgroundColor: 'rgba(139, 92, 246, 0.25)',
    borderColor: '#8B5CF6',
    borderWidth: 2,
  },
  trialUrgentBestBadge: {
    position: 'absolute',
    top: -10,
    right: 10,
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  trialUrgentBestBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  trialUrgentPlanPrice: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  trialUrgentPlanLabel: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 2,
  },
  // Early Subscribe Section (during trial, from day 1)
  earlySubscribeCard: {
    backgroundColor: '#12123A',
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)',
  },
  earlySubscribeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  earlySubscribeTitle: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  earlySubscribeSubtext: {
    color: '#888',
    fontSize: 13,
    marginBottom: 16,
    lineHeight: 18,
  },
  earlySubscribePlans: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  earlyPlanBtn: {
    flex: 1,
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.2)',
  },
  earlyPlanBtnBest: {
    backgroundColor: 'rgba(139, 92, 246, 0.2)',
    borderColor: '#8B5CF6',
    borderWidth: 2,
  },
  earlyBestBadge: {
    position: 'absolute',
    top: -10,
    right: 10,
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  earlyBestBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  earlyPlanPrice: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
  },
  earlyPlanLabel: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 4,
  },
});
