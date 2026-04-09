import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../src/services/api';

interface BoostPlan {
  id: string;
  amount: number;
  currency: string;
  label: string;
  description: string;
  days: number;
  savings?: string;
}

export default function BoostScreen() {
  const router = useRouter();
  const [plans, setPlans] = useState<BoostPlan[]>([]);
  const [boostStatus, setBoostStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [plansData, statusData] = await Promise.all([
        api.getBoostPlans(),
        api.getBoostStatus(),
      ]);
      setPlans(plansData);
      setBoostStatus(statusData);
    } catch (error) {
      console.error('Error loading boost data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (planId: string) => {
    setPurchasing(planId);
    try {
      const originUrl = Platform.OS === 'web' ? window.location.origin : '';
      const result = await api.createBoostCheckout(planId, originUrl);
      if (result.checkout_url) {
        if (Platform.OS === 'web') {
          window.location.href = result.checkout_url;
        } else {
          Linking.openURL(result.checkout_url);
        }
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
      if (Platform.OS === 'web') {
        window.alert('Erreur lors de la création du paiement');
      }
    } finally {
      setPurchasing(null);
    }
  };

  const getStars = (planId: string) => {
    if (planId === '1_month') return '⭐⭐⭐';
    if (planId === '2_weeks') return '⭐⭐';
    return '⭐';
  };

  const getPlanColor = (planId: string) => {
    if (planId === '1_month') return '#FFD700';
    if (planId === '2_weeks') return '#C0C0C0';
    return '#CD7F32';
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#FFD700" style={styles.loader} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.title}>Booster mon profil</Text>
        </View>

        {/* Current status */}
        {boostStatus?.boost_active && (
          <View style={styles.activeBoost}>
            <Ionicons name="star" size={28} color="#FFD700" />
            <View style={styles.activeBoostInfo}>
              <Text style={styles.activeBoostTitle}>Boost actif !</Text>
              <Text style={styles.activeBoostText}>
                {boostStatus.days_remaining} jour{boostStatus.days_remaining > 1 ? 's' : ''} restant{boostStatus.days_remaining > 1 ? 's' : ''}
              </Text>
            </View>
          </View>
        )}

        {/* Hero */}
        <View style={styles.heroSection}>
          <Text style={styles.heroEmoji}>🚀</Text>
          <Text style={styles.heroTitle}>Boostez votre visibilité</Text>
          <Text style={styles.heroSubtitle}>
            Apparaissez en tête de liste avec un badge étoile doré.{"\n"}
            Les clients vous verront en premier !
          </Text>
        </View>

        {/* Benefits */}
        <View style={styles.benefitsSection}>
          <View style={styles.benefitRow}>
            <Ionicons name="pin" size={20} color="#FFD700" />
            <Text style={styles.benefitText}>Épinglé en tête des résultats</Text>
          </View>
          <View style={styles.benefitRow}>
            <Ionicons name="star" size={20} color="#FFD700" />
            <Text style={styles.benefitText}>Badge "Sponsorisé" doré visible</Text>
          </View>
          <View style={styles.benefitRow}>
            <Ionicons name="eye" size={20} color="#FFD700" />
            <Text style={styles.benefitText}>Jusqu'à 5x plus de visibilité</Text>
          </View>
          <View style={styles.benefitRow}>
            <Ionicons name="trending-up" size={20} color="#FFD700" />
            <Text style={styles.benefitText}>Plus de demandes de contact</Text>
          </View>
        </View>

        {/* Plans */}
        <Text style={styles.plansTitle}>Choisissez votre boost</Text>

        {plans.map((plan) => {
          const isBest = plan.id === '1_month';
          return (
            <TouchableOpacity
              key={plan.id}
              style={[styles.planCard, isBest && styles.planCardBest]}
              onPress={() => handlePurchase(plan.id)}
              disabled={purchasing !== null}
              activeOpacity={0.7}
            >
              {isBest && (
                <View style={styles.bestBadge}>
                  <Text style={styles.bestBadgeText}>MEILLEUR CHOIX</Text>
                </View>
              )}
              <View style={styles.planHeader}>
                <Text style={styles.planStars}>{getStars(plan.id)}</Text>
                <View style={styles.planInfo}>
                  <Text style={styles.planLabel}>{plan.label}</Text>
                  {plan.savings && (
                    <View style={styles.savingsBadge}>
                      <Text style={styles.savingsText}>{plan.savings}</Text>
                    </View>
                  )}
                </View>
                <View style={styles.planPriceContainer}>
                  <Text style={[styles.planPrice, { color: getPlanColor(plan.id) }]}>
                    {plan.amount}€
                  </Text>
                </View>
              </View>
              <View style={styles.planFooter}>
                {purchasing === plan.id ? (
                  <ActivityIndicator size="small" color="#FFD700" />
                ) : (
                  <Text style={[styles.planCTA, isBest && styles.planCTABest]}>
                    Activer le boost
                  </Text>
                )}
              </View>
            </TouchableOpacity>
          );
        })}

        <View style={styles.footer} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
  },
  scrollContent: {
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  backButton: {
    marginRight: 12,
    padding: 4,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  activeBoost: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.3)',
    borderRadius: 16,
    marginHorizontal: 20,
    padding: 16,
    marginBottom: 16,
  },
  activeBoostInfo: {
    marginLeft: 12,
  },
  activeBoostTitle: {
    color: '#FFD700',
    fontSize: 16,
    fontWeight: 'bold',
  },
  activeBoostText: {
    color: '#ccc',
    fontSize: 14,
    marginTop: 2,
  },
  heroSection: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 24,
  },
  heroEmoji: {
    fontSize: 48,
    marginBottom: 12,
  },
  heroTitle: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#FFD700',
    textAlign: 'center',
  },
  heroSubtitle: {
    fontSize: 15,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 22,
  },
  benefitsSection: {
    backgroundColor: '#12123A',
    borderRadius: 16,
    marginHorizontal: 20,
    padding: 20,
    marginBottom: 24,
  },
  benefitRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  benefitText: {
    color: '#ddd',
    fontSize: 15,
    marginLeft: 12,
    flex: 1,
  },
  plansTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  planCard: {
    backgroundColor: '#12123A',
    borderRadius: 16,
    marginHorizontal: 20,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#1E1E4A',
    overflow: 'hidden',
  },
  planCardBest: {
    borderColor: '#FFD700',
    borderWidth: 2,
  },
  bestBadge: {
    backgroundColor: '#FFD700',
    paddingVertical: 4,
    alignItems: 'center',
  },
  bestBadgeText: {
    color: '#000',
    fontSize: 11,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  planStars: {
    fontSize: 20,
    marginRight: 12,
  },
  planInfo: {
    flex: 1,
  },
  planLabel: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  savingsBadge: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 4,
  },
  savingsText: {
    color: '#10B981',
    fontSize: 12,
    fontWeight: '600',
  },
  planPriceContainer: {
    alignItems: 'flex-end',
  },
  planPrice: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  planFooter: {
    borderTopWidth: 1,
    borderTopColor: '#1E1E4A',
    padding: 14,
    alignItems: 'center',
  },
  planCTA: {
    color: '#8B5CF6',
    fontSize: 16,
    fontWeight: '600',
  },
  planCTABest: {
    color: '#FFD700',
  },
  footer: {
    height: 20,
  },
});
