import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../src/services/api';
import { useAuthStore } from '../src/stores/authStore';

const EVENT_TYPES = [
  { id: 'mariage', label: 'Mariage' },
  { id: 'anniversaire', label: 'Anniversaire' },
  { id: 'entreprise', label: 'Entreprise' },
  { id: 'soiree_privee', label: 'Soirée privée' },
  { id: 'bar_mitzvah', label: 'Bar/Bat Mitzvah' },
  { id: 'festival', label: 'Festival' },
  { id: 'club', label: 'Club' },
  { id: 'autre', label: 'Autre' },
];

export default function AdminScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [djs, setDJs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    nom_de_scene: '',
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    ville: '',
    description: '',
    tarif_indicatif: '800',
    types_evenements: [] as string[],
    instagram: '',
    youtube: '',
    google_page: '',
    site_internet: '',
  });

  const loadDJs = async () => {
    try {
      const result = await api.adminListDJs();
      setDJs(result.djs);
    } catch (error: any) {
      if (error.message?.includes('403') || error.message?.includes('admin')) {
        showAlert('Accès refusé', 'Vous n\'avez pas les droits administrateur.');
        router.back();
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDJs();
  }, []);

  const showAlert = (title: string, message: string) => {
    if (Platform.OS === 'web') {
      window.alert(`${title}: ${message}`);
    } else {
      Alert.alert(title, message);
    }
  };

  const handleToggleSubscription = async (userId: string, currentStatus: string) => {
    try {
      const result = await api.adminToggleSubscription(userId);
      showAlert('Succès', result.message);
      loadDJs();
    } catch (error: any) {
      showAlert('Erreur', error.message);
    }
  };

  const handleToggleBoost = async (userId: string) => {
    try {
      const result = await api.adminToggleBoost(userId);
      showAlert('Succès', result.message);
      loadDJs();
    } catch (error: any) {
      showAlert('Erreur', error.message);
    }
  };

  const handleDeleteDJ = async (userId: string, name: string) => {
    const doDelete = async () => {
      try {
        await api.adminDeleteDJ(userId);
        showAlert('Succès', 'DJ supprimé');
        loadDJs();
      } catch (error: any) {
        showAlert('Erreur', error.message);
      }
    };

    if (Platform.OS === 'web') {
      if (window.confirm(`Supprimer ${name} ? Cette action est irréversible.`)) {
        doDelete();
      }
    } else {
      Alert.alert('Confirmer', `Supprimer ${name} ?`, [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Supprimer', style: 'destructive', onPress: doDelete },
      ]);
    }
  };

  const toggleEventType = (id: string) => {
    setFormData(prev => ({
      ...prev,
      types_evenements: prev.types_evenements.includes(id)
        ? prev.types_evenements.filter(t => t !== id)
        : [...prev.types_evenements, id],
    }));
  };

  const handleCreateDJ = async () => {
    if (!formData.nom_de_scene.trim()) {
      showAlert('Erreur', 'Le nom de scène est requis');
      return;
    }
    if (!formData.ville.trim()) {
      showAlert('Erreur', 'La ville est requise');
      return;
    }

    setCreating(true);
    try {
      const result = await api.adminCreateDJ(formData);
      showAlert('Succès', result.message);
      setShowCreateForm(false);
      setFormData({
        nom_de_scene: '', nom: '', prenom: '', email: '', telephone: '',
        ville: '', description: '', tarif_indicatif: '800',
        types_evenements: [], instagram: '', youtube: '', google_page: '', site_internet: '',
      });
      loadDJs();
    } catch (error: any) {
      showAlert('Erreur', error.message);
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#8B5CF6" style={{ marginTop: 100 }} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadDJs(); }} tintColor="#8B5CF6" />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Panel Admin</Text>
            <Text style={styles.subtitle}>{djs.length} DJ(s) enregistrés</Text>
          </View>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setShowCreateForm(!showCreateForm)}
          >
            <Ionicons name={showCreateForm ? 'close' : 'add'} size={24} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Create DJ Form */}
        {showCreateForm && (
          <View style={styles.formContainer}>
            <Text style={styles.formTitle}>Ajouter un DJ (gratuit)</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Nom de scène *</Text>
              <TextInput
                style={styles.input}
                value={formData.nom_de_scene}
                onChangeText={t => setFormData({ ...formData, nom_de_scene: t })}
                placeholder="Ex: DJ Phoenix"
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, { flex: 1, marginRight: 8 }]}>
                <Text style={styles.label}>Nom</Text>
                <TextInput
                  style={styles.input}
                  value={formData.nom}
                  onChangeText={t => setFormData({ ...formData, nom: t })}
                  placeholder="Nom"
                  placeholderTextColor="#666"
                />
              </View>
              <View style={[styles.inputGroup, { flex: 1, marginLeft: 8 }]}>
                <Text style={styles.label}>Prénom</Text>
                <TextInput
                  style={styles.input}
                  value={formData.prenom}
                  onChangeText={t => setFormData({ ...formData, prenom: t })}
                  placeholder="Prénom"
                  placeholderTextColor="#666"
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Email</Text>
              <TextInput
                style={styles.input}
                value={formData.email}
                onChangeText={t => setFormData({ ...formData, email: t })}
                placeholder="email@example.com"
                placeholderTextColor="#666"
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Téléphone</Text>
              <TextInput
                style={styles.input}
                value={formData.telephone}
                onChangeText={t => setFormData({ ...formData, telephone: t })}
                placeholder="06 XX XX XX XX"
                placeholderTextColor="#666"
                keyboardType="phone-pad"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Ville *</Text>
              <TextInput
                style={styles.input}
                value={formData.ville}
                onChangeText={t => setFormData({ ...formData, ville: t })}
                placeholder="Paris, Lyon, Marseille..."
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Tarif indicatif (€)</Text>
              <TextInput
                style={styles.input}
                value={formData.tarif_indicatif}
                onChangeText={t => setFormData({ ...formData, tarif_indicatif: t })}
                placeholder="800"
                placeholderTextColor="#666"
                keyboardType="numeric"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Description</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={formData.description}
                onChangeText={t => setFormData({ ...formData, description: t })}
                placeholder="Présentation du DJ..."
                placeholderTextColor="#666"
                multiline
                numberOfLines={4}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Types d'événements</Text>
              <View style={styles.chipsContainer}>
                {EVENT_TYPES.map(type => (
                  <TouchableOpacity
                    key={type.id}
                    style={[
                      styles.chip,
                      formData.types_evenements.includes(type.id) && styles.chipActive,
                    ]}
                    onPress={() => toggleEventType(type.id)}
                  >
                    <Text style={[
                      styles.chipText,
                      formData.types_evenements.includes(type.id) && styles.chipTextActive,
                    ]}>
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Instagram</Text>
              <TextInput
                style={styles.input}
                value={formData.instagram}
                onChangeText={t => setFormData({ ...formData, instagram: t })}
                placeholder="@pseudo"
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Page Google</Text>
              <TextInput
                style={styles.input}
                value={formData.google_page}
                onChangeText={t => setFormData({ ...formData, google_page: t })}
                placeholder="https://g.page/..."
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Site Internet</Text>
              <TextInput
                style={styles.input}
                value={formData.site_internet}
                onChangeText={t => setFormData({ ...formData, site_internet: t })}
                placeholder="https://www...."
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
            </View>

            <TouchableOpacity
              style={[styles.createButton, creating && styles.buttonDisabled]}
              onPress={handleCreateDJ}
              disabled={creating}
            >
              {creating ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text style={styles.createButtonText}>Créer le DJ (abonnement gratuit)</Text>
              )}
            </TouchableOpacity>
          </View>
        )}

        {/* DJ List */}
        <View style={styles.listContainer}>
          <Text style={styles.sectionTitle}>Tous les DJs</Text>
          
          {djs.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="musical-notes" size={48} color="#666" />
              <Text style={styles.emptyText}>Aucun DJ enregistré</Text>
              <Text style={styles.emptySubtext}>Cliquez sur + pour ajouter le premier DJ</Text>
            </View>
          ) : (
            djs.map((dj) => (
              <View key={dj.user_id} style={styles.djCard}>
                <View style={styles.djCardHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.djName}>{dj.nom_de_scene || `${dj.prenom} ${dj.nom}`}</Text>
                    <Text style={styles.djCity}>
                      <Ionicons name="location" size={12} color="#888" /> {dj.ville || 'Non renseigné'}
                      {dj.department_name ? ` — ${dj.department_name}` : ''}
                    </Text>
                  </View>
                  <View style={[
                    styles.statusBadge,
                    dj.subscription_status === 'active' ? styles.statusActive : styles.statusInactive,
                  ]}>
                    <Text style={styles.statusText}>
                      {dj.subscription_status === 'active' ? 'Actif' : 'Inactif'}
                    </Text>
                  </View>
                </View>

                <View style={styles.djMeta}>
                  {dj.tarif_indicatif && (
                    <Text style={styles.djMetaText}>{dj.tarif_indicatif}€</Text>
                  )}
                  {dj.subscription_plan && (
                    <Text style={styles.djMetaText}>
                      {dj.subscription_plan === 'admin_free' ? 'Gratuit (admin)' : dj.subscription_plan}
                    </Text>
                  )}
                  {dj.added_by_admin && (
                    <View style={styles.adminBadge}>
                      <Text style={styles.adminBadgeText}>Ajouté par admin</Text>
                    </View>
                  )}
                  {dj.boost_active && (
                    <View style={styles.boostBadge}>
                      <Ionicons name="star" size={11} color="#000" />
                      <Text style={styles.boostBadgeText}>Boosté</Text>
                    </View>
                  )}
                </View>

                <View style={styles.djActions}>
                  <TouchableOpacity
                    style={[
                      styles.actionButton,
                      dj.subscription_status === 'active' ? styles.deactivateButton : styles.activateButton,
                    ]}
                    onPress={() => handleToggleSubscription(dj.user_id, dj.subscription_status)}
                  >
                    <Ionicons
                      name={dj.subscription_status === 'active' ? 'eye-off' : 'eye'}
                      size={16}
                      color="#fff"
                    />
                    <Text style={styles.actionButtonText}>
                      {dj.subscription_status === 'active' ? 'Désactiver' : 'Activer'}
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.actionButton, dj.boost_active ? styles.deactivateButton : styles.boostButton]}
                    onPress={() => handleToggleBoost(dj.user_id)}
                  >
                    <Ionicons name="star" size={16} color={dj.boost_active ? '#fff' : '#000'} />
                    <Text style={[styles.actionButtonText, !dj.boost_active && { color: '#000' }]}>
                      {dj.boost_active ? 'Retirer boost' : 'Booster'}
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.actionButton, styles.deleteButton]}
                    onPress={() => handleDeleteDJ(dj.user_id, dj.nom_de_scene || dj.nom)}
                  >
                    <Ionicons name="trash" size={16} color="#fff" />
                    <Text style={styles.actionButtonText}>Supprimer</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))
          )}
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  backButton: {
    width: 44,
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 13,
    color: '#888',
    marginTop: 2,
  },
  addButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#8B5CF6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  formContainer: {
    marginHorizontal: 20,
    backgroundColor: '#1a1a1a',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#8B5CF6',
  },
  formTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#8B5CF6',
    marginBottom: 16,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 14,
  },
  label: {
    color: '#ccc',
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#111',
    borderRadius: 10,
    padding: 12,
    color: '#fff',
    fontSize: 15,
    borderWidth: 1,
    borderColor: '#2a2a2a',
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    backgroundColor: '#222',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#333',
  },
  chipActive: {
    backgroundColor: '#8B5CF6',
    borderColor: '#8B5CF6',
  },
  chipText: {
    color: '#888',
    fontSize: 13,
  },
  chipTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  createButton: {
    backgroundColor: '#8B5CF6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    color: '#888',
    fontSize: 16,
    marginTop: 12,
  },
  emptySubtext: {
    color: '#666',
    fontSize: 13,
    marginTop: 4,
  },
  djCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2a2a2a',
  },
  djCardHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
  },
  djName: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#fff',
  },
  djCity: {
    fontSize: 13,
    color: '#888',
    marginTop: 4,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusActive: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
  },
  statusInactive: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#fff',
  },
  djMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    gap: 10,
    flexWrap: 'wrap',
  },
  djMetaText: {
    color: '#888',
    fontSize: 12,
    backgroundColor: '#222',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  adminBadge: {
    backgroundColor: 'rgba(139, 92, 246, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  adminBadgeText: {
    color: '#8B5CF6',
    fontSize: 11,
    fontWeight: '600',
  },
  djActions: {
    flexDirection: 'row',
    marginTop: 12,
    gap: 10,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    gap: 6,
  },
  activateButton: {
    backgroundColor: '#10B981',
  },
  deactivateButton: {
    backgroundColor: '#F59E0B',
  },
  deleteButton: {
    backgroundColor: '#EF4444',
  },
  boostButton: {
    backgroundColor: '#FFD700',
  },
  boostBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFD700',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    gap: 3,
  },
  boostBadgeText: {
    color: '#000',
    fontSize: 11,
    fontWeight: 'bold',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
  },
});
