import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/stores/authStore';
import { api } from '../../src/services/api';
import { Button } from '../../src/components/Button';
import { DJProfile } from '../../src/types';

export default function ProfileScreen() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [djProfile, setDJProfile] = useState<DJProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      if (isAuthenticated && user?.is_dj) {
        try {
          const profile = await api.getMyDJProfile();
          setDJProfile(profile);
        } catch (error) {
          console.error('Error loading profile:', error);
        }
      }
      setLoading(false);
    };

    loadProfile();
  }, [isAuthenticated, user]);

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

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Déconnexion',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/');
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#8B5CF6" style={styles.loader} />
      </SafeAreaView>
    );
  }

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.notAuthContainer}>
          <Ionicons name="person-circle" size={80} color="#444" />
          <Text style={styles.notAuthTitle}>Bienvenue sur DJ Match</Text>
          <Text style={styles.notAuthText}>
            Connectez-vous pour gérer votre profil DJ ou contacter des DJs
          </Text>
          <Button
            title="Se connecter avec Google"
            onPress={handleLogin}
            style={styles.loginButton}
          />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>Mon Profil</Text>
        </View>

        {/* User Info */}
        <View style={styles.userSection}>
          <View style={styles.avatarContainer}>
            {user?.picture ? (
              <Image source={{ uri: user.picture }} style={styles.avatar} />
            ) : (
              <Ionicons name="person-circle" size={80} color="#8B5CF6" />
            )}
          </View>
          <Text style={styles.userName}>{user?.name}</Text>
          <Text style={styles.userEmail}>{user?.email}</Text>
          {user?.is_dj && (
            <View style={styles.djBadge}>
              <Ionicons name="musical-notes" size={16} color="#fff" />
              <Text style={styles.djBadgeText}>Profil DJ</Text>
            </View>
          )}
        </View>

        {/* DJ Profile Summary */}
        {djProfile && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Mon profil DJ</Text>
            
            <View style={styles.profileCard}>
              <View style={styles.profileHeader}>
                <Text style={styles.stageName}>{djProfile.nom_de_scene}</Text>
                {djProfile.badge_verifie && (
                  <View style={styles.verifiedBadge}>
                    <Ionicons name="checkmark-circle" size={16} color="#fff" />
                    <Text style={styles.verifiedText}>Vérifié</Text>
                  </View>
                )}
              </View>
              
              <View style={styles.profileStats}>
                <View style={styles.profileStat}>
                  <Text style={styles.profileStatValue}>{djProfile.profil_complete_percent}%</Text>
                  <Text style={styles.profileStatLabel}>Complet</Text>
                </View>
                <View style={styles.profileStat}>
                  <Text style={styles.profileStatValue}>{djProfile.note_moyenne.toFixed(1)}</Text>
                  <Text style={styles.profileStatLabel}>Note</Text>
                </View>
                <View style={styles.profileStat}>
                  <Text style={styles.profileStatValue}>{djProfile.nombre_avis}</Text>
                  <Text style={styles.profileStatLabel}>Avis</Text>
                </View>
              </View>

              <View style={[
                styles.subscriptionStatus,
                djProfile.subscription_status === 'active' ? styles.subscriptionActive : styles.subscriptionInactive
              ]}>
                <Ionicons
                  name={djProfile.subscription_status === 'active' ? 'checkmark-circle' : 'alert-circle'}
                  size={20}
                  color={djProfile.subscription_status === 'active' ? '#10B981' : '#F59E0B'}
                />
                <Text style={[
                  styles.subscriptionText,
                  djProfile.subscription_status === 'active' ? styles.subscriptionTextActive : styles.subscriptionTextInactive
                ]}>
                  Abonnement {djProfile.subscription_status === 'active' ? 'actif' : 'inactif'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Actions</Text>

          {!user?.is_dj && (
            <TouchableOpacity
              style={styles.actionItem}
              onPress={() => router.push('/dj-register')}
            >
              <Ionicons name="add-circle" size={24} color="#8B5CF6" />
              <Text style={styles.actionText}>Devenir DJ</Text>
              <Ionicons name="chevron-forward" size={24} color="#666" />
            </TouchableOpacity>
          )}

          {user?.is_dj && (
            <TouchableOpacity
              style={styles.actionItem}
              onPress={() => router.push('/(tabs)/dashboard')}
            >
              <Ionicons name="stats-chart" size={24} color="#8B5CF6" />
              <Text style={styles.actionText}>Tableau de bord</Text>
              <Ionicons name="chevron-forward" size={24} color="#666" />
            </TouchableOpacity>
          )}

          <TouchableOpacity style={styles.actionItem} onPress={handleLogout}>
            <Ionicons name="log-out" size={24} color="#EF4444" />
            <Text style={[styles.actionText, { color: '#EF4444' }]}>Déconnexion</Text>
            <Ionicons name="chevron-forward" size={24} color="#666" />
          </TouchableOpacity>

          {user?.is_admin && (
            <TouchableOpacity
              style={[styles.actionItem, styles.adminAction]}
              onPress={() => router.push('/admin')}
            >
              <Ionicons name="shield-checkmark" size={24} color="#F59E0B" />
              <Text style={[styles.actionText, { color: '#F59E0B' }]}>Panel Administrateur</Text>
              <Ionicons name="chevron-forward" size={24} color="#F59E0B" />
            </TouchableOpacity>
          )}

          {user?.is_admin && (
            <TouchableOpacity
              style={[styles.actionItem, styles.adminAction]}
              onPress={() => router.push('/admin-contacts')}
            >
              <Ionicons name="people" size={24} color="#F59E0B" />
              <Text style={[styles.actionText, { color: '#F59E0B' }]}>Contacts CRM</Text>
              <Ionicons name="chevron-forward" size={24} color="#F59E0B" />
            </TouchableOpacity>
          )}
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>DJ Match France v1.0</Text>
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
  loader: {
    flex: 1,
    justifyContent: 'center',
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
  userSection: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  avatarContainer: {
    marginBottom: 16,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  userEmail: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
  djBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginTop: 12,
  },
  djBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  section: {
    paddingHorizontal: 20,
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  profileCard: {
    backgroundColor: '#12123A',
    borderRadius: 12,
    padding: 16,
  },
  profileHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  stageName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  verifiedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  verifiedText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  profileStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  profileStat: {
    alignItems: 'center',
  },
  profileStatValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#8B5CF6',
  },
  profileStatLabel: {
    fontSize: 12,
    color: '#888',
    marginTop: 4,
  },
  subscriptionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
  },
  subscriptionActive: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  subscriptionInactive: {
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
  },
  subscriptionText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  subscriptionTextActive: {
    color: '#10B981',
  },
  subscriptionTextInactive: {
    color: '#F59E0B',
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
  adminAction: {
    borderWidth: 1,
    borderColor: 'rgba(245, 158, 11, 0.3)',
    backgroundColor: 'rgba(245, 158, 11, 0.05)',
    marginTop: 12,
  },
  notAuthContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  notAuthTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 24,
    textAlign: 'center',
  },
  notAuthText: {
    fontSize: 16,
    color: '#888',
    textAlign: 'center',
    marginTop: 12,
    lineHeight: 24,
  },
  loginButton: {
    marginTop: 32,
    width: '100%',
  },
  footer: {
    padding: 40,
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
