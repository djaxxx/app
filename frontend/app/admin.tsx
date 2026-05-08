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

type TabType = 'djs' | 'contacts' | 'stats';

export default function AdminScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [djs, setDJs] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('djs');
  const [expandedDJ, setExpandedDJ] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = async () => {
    try {
      const [djResult, statsResult, contactsResult] = await Promise.all([
        api.adminListDJs(),
        api.adminGetStats(),
        api.adminGetContactRequests(),
      ]);
      setDJs(djResult.djs);
      setStats(statsResult);
      setContacts(contactsResult.requests);
    } catch (error: any) {
      if (error.message?.includes('403') || error.message?.includes('admin') || error.message?.includes('401')) {
        showAlert('Acces refuse', 'Vous n\'avez pas les droits administrateur.');
        router.back();
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const showAlert = (title: string, message: string) => {
    if (Platform.OS === 'web') {
      window.alert(`${title}: ${message}`);
    } else {
      Alert.alert(title, message);
    }
  };

  const handleToggleSubscription = async (userId: string) => {
    try {
      const result = await api.adminToggleSubscription(userId);
      showAlert('Succes', result.message);
      loadData();
    } catch (error: any) {
      showAlert('Erreur', error.message);
    }
  };

  const handleToggleBoost = async (userId: string) => {
    try {
      const result = await api.adminToggleBoost(userId);
      showAlert('Succes', result.message);
      loadData();
    } catch (error: any) {
      showAlert('Erreur', error.message);
    }
  };

  const handleDeleteDJ = async (userId: string, name: string) => {
    const doDelete = async () => {
      try {
        await api.adminDeleteDJ(userId);
        showAlert('Succes', 'DJ supprime');
        loadData();
      } catch (error: any) {
        showAlert('Erreur', error.message);
      }
    };
    if (Platform.OS === 'web') {
      if (window.confirm(`Supprimer ${name} ? Cette action est irreversible.`)) doDelete();
    } else {
      Alert.alert('Confirmer', `Supprimer ${name} ?`, [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Supprimer', style: 'destructive', onPress: doDelete },
      ]);
    }
  };

  const handleSendReminder = async (userId: string, name: string) => {
    try {
      const result = await api.adminSendReminder(userId);
      showAlert('Email envoye', result.message);
    } catch (error: any) {
      showAlert('Erreur', error.message);
    }
  };

  const handleSendAllReminders = async () => {
    const expiredCount = djs.filter(d => d.subscription_status === 'expired').length;
    const doSend = async () => {
      try {
        const result = await api.adminSendAllReminders();
        showAlert('Relance envoyee', result.message);
      } catch (error: any) {
        showAlert('Erreur', error.message);
      }
    };
    if (Platform.OS === 'web') {
      if (window.confirm(`Envoyer un email de relance a tous les DJs expires (${expiredCount}) ?`)) doSend();
    } else {
      Alert.alert('Relance globale', `Envoyer un email a ${expiredCount} DJs expires ?`, [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Envoyer', onPress: doSend },
      ]);
    }
  };

  const handleDeleteContacts = async (type: 'read' | 'unread' | 'all') => {
    const labels = { read: 'lues', unread: 'non lues', all: 'toutes les' };
    const counts = {
      read: contacts.filter(c => c.read).length,
      unread: contacts.filter(c => !c.read).length,
      all: contacts.length,
    };
    const doDelete = async () => {
      try {
        let result;
        if (type === 'read') result = await api.adminDeleteReadContacts();
        else if (type === 'unread') result = await api.adminDeleteUnreadContacts();
        else result = await api.adminDeleteAllContacts();
        showAlert('Supprime', result.message);
        loadData();
      } catch (error: any) {
        showAlert('Erreur', error.message);
      }
    };
    const msg = `Supprimer ${labels[type]} demandes (${counts[type]}) ?`;
    if (Platform.OS === 'web') {
      if (window.confirm(msg)) doDelete();
    } else {
      Alert.alert('Confirmer', msg, [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Supprimer', style: 'destructive', onPress: doDelete },
      ]);
    }
  };

  const [statusFilter, setStatusFilter] = useState<string>('all');

  const getStatusInfo = (dj: any) => {
    const status = dj.subscription_status || 'inactive';
    if (status === 'active') return { label: 'Actif', color: '#10B981', bg: 'rgba(16,185,129,0.15)' };
    if (status === 'trial') {
      const trialEnd = dj.trial_end ? new Date(dj.trial_end) : null;
      const daysLeft = trialEnd ? Math.max(0, Math.ceil((trialEnd.getTime() - Date.now()) / 86400000)) : 0;
      return { label: `Essai (${daysLeft}j)`, color: '#8B5CF6', bg: 'rgba(139,92,246,0.15)' };
    }
    if (status === 'expired') return { label: 'Expire', color: '#EF4444', bg: 'rgba(239,68,68,0.15)' };
    return { label: 'Inactif', color: '#6B7280', bg: 'rgba(107,114,128,0.15)' };
  };

  const filteredDJs = djs.filter(dj => {
    // Filter by status
    if (statusFilter !== 'all' && dj.subscription_status !== statusFilter) return false;
    // Filter by search
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (dj.nom_de_scene || '').toLowerCase().includes(q) ||
      (dj.email || '').toLowerCase().includes(q) ||
      (dj.ville || '').toLowerCase().includes(q) ||
      (dj.telephone || '').includes(q)
    );
  });

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
          <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} tintColor="#8B5CF6" />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Panel Administrateur</Text>
            <Text style={styles.subtitle}>DJ Match — Gestion complete</Text>
          </View>
        </View>

        {/* Stats Cards */}
        {stats && (
          <View style={styles.statsRow}>
            <View style={[styles.statCard, { borderLeftColor: '#8B5CF6' }]}>
              <Text style={styles.statNumber}>{stats.total_djs}</Text>
              <Text style={styles.statLabel}>DJs inscrits</Text>
            </View>
            <View style={[styles.statCard, { borderLeftColor: '#10B981' }]}>
              <Text style={styles.statNumber}>{stats.active_djs}</Text>
              <Text style={styles.statLabel}>Actifs</Text>
            </View>
            <View style={[styles.statCard, { borderLeftColor: '#F59E0B' }]}>
              <Text style={styles.statNumber}>{stats.trial_djs}</Text>
              <Text style={styles.statLabel}>En essai</Text>
            </View>
            <View style={[styles.statCard, { borderLeftColor: '#EF4444' }]}>
              <Text style={styles.statNumber}>{stats.expired_djs}</Text>
              <Text style={styles.statLabel}>Expires</Text>
            </View>
          </View>
        )}

        {/* Tabs */}
        <View style={styles.tabBar}>
          {(['djs', 'contacts', 'stats'] as TabType[]).map(tab => (
            <TouchableOpacity
              key={tab}
              style={[styles.tab, activeTab === tab && styles.tabActive]}
              onPress={() => setActiveTab(tab)}
            >
              <Ionicons
                name={tab === 'djs' ? 'people' : tab === 'contacts' ? 'mail' : 'bar-chart'}
                size={18}
                color={activeTab === tab ? '#8B5CF6' : '#666'}
              />
              <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
                {tab === 'djs' ? `DJs (${djs.length})` : tab === 'contacts' ? `Demandes (${contacts.length})` : 'Stats'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* TAB: DJs */}
        {activeTab === 'djs' && (
          <View style={styles.section}>
            {/* Search */}
            <View style={styles.searchBar}>
              <Ionicons name="search" size={18} color="#666" />
              <TextInput
                style={styles.searchInput}
                placeholder="Chercher un DJ (nom, email, ville...)"
                placeholderTextColor="#666"
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
              {searchQuery ? (
                <TouchableOpacity onPress={() => setSearchQuery('')}>
                  <Ionicons name="close-circle" size={20} color="#666" />
                </TouchableOpacity>
              ) : null}
            </View>

            {/* CRM link */}
            <TouchableOpacity style={styles.crmLink} onPress={() => router.push('/admin-contacts')}>
              <Ionicons name="download" size={18} color="#8B5CF6" />
              <Text style={styles.crmLinkText}>Exporter les contacts (CSV)</Text>
              <Ionicons name="chevron-forward" size={18} color="#8B5CF6" />
            </TouchableOpacity>

            {/* Status Filters */}
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginHorizontal: 16, marginBottom: 12 }}>
              {[
                { id: 'all', label: 'Tous', count: djs.length, color: '#8B5CF6' },
                { id: 'active', label: 'Actifs', count: djs.filter(d => d.subscription_status === 'active').length, color: '#10B981' },
                { id: 'trial', label: 'Essai', count: djs.filter(d => d.subscription_status === 'trial').length, color: '#F59E0B' },
                { id: 'expired', label: 'Expires', count: djs.filter(d => d.subscription_status === 'expired').length, color: '#EF4444' },
                { id: 'inactive', label: 'Inactifs', count: djs.filter(d => !d.subscription_status || d.subscription_status === 'inactive').length, color: '#6B7280' },
              ].map(f => (
                <TouchableOpacity
                  key={f.id}
                  onPress={() => setStatusFilter(f.id)}
                  style={{
                    paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, marginRight: 8,
                    backgroundColor: statusFilter === f.id ? f.color : 'rgba(255,255,255,0.05)',
                    borderWidth: 1, borderColor: statusFilter === f.id ? f.color : 'rgba(255,255,255,0.1)',
                  }}
                >
                  <Text style={{ color: statusFilter === f.id ? '#fff' : '#aaa', fontSize: 13, fontWeight: '600' }}>
                    {f.label} ({f.count})
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* Bulk Reminder Button (when filtering expired) */}
            {(statusFilter === 'expired' || statusFilter === 'all') && djs.filter(d => d.subscription_status === 'expired').length > 0 && (
              <TouchableOpacity
                style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#EF4444', marginHorizontal: 16, marginBottom: 12, paddingVertical: 12, borderRadius: 10 }}
                onPress={handleSendAllReminders}
              >
                <Ionicons name="mail" size={18} color="#fff" />
                <Text style={{ color: '#fff', fontSize: 14, fontWeight: '700', marginLeft: 8 }}>
                  Relancer tous les expires ({djs.filter(d => d.subscription_status === 'expired').length})
                </Text>
              </TouchableOpacity>
            )}

            {filteredDJs.map((dj) => {
              const statusInfo = getStatusInfo(dj);
              const isExpanded = expandedDJ === dj.user_id;
              return (
                <View key={dj.user_id} style={styles.djCard}>
                  {/* Card Header - clickable */}
                  <TouchableOpacity
                    style={styles.djCardHeader}
                    onPress={() => setExpandedDJ(isExpanded ? null : dj.user_id)}
                    activeOpacity={0.7}
                  >
                    <View style={{ flex: 1 }}>
                      <View style={styles.djNameRow}>
                        <Text style={styles.djName}>{dj.nom_de_scene || `${dj.prenom || ''} ${dj.nom || ''}`}</Text>
                        {dj.boost_active && (
                          <View style={styles.boostBadge}>
                            <Ionicons name="star" size={10} color="#000" />
                          </View>
                        )}
                      </View>
                      <Text style={styles.djCity}>
                        {dj.ville || 'Non renseigne'} {dj.department_name ? `(${dj.department_code})` : ''}
                      </Text>
                    </View>
                    <View style={[styles.statusBadge, { backgroundColor: statusInfo.bg }]}>
                      <Text style={[styles.statusText, { color: statusInfo.color }]}>{statusInfo.label}</Text>
                    </View>
                    <Ionicons name={isExpanded ? 'chevron-up' : 'chevron-down'} size={20} color="#666" style={{ marginLeft: 8 }} />
                  </TouchableOpacity>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <View style={styles.djDetails}>
                      <View style={styles.detailRow}>
                        <Ionicons name="mail" size={14} color="#888" />
                        <Text style={styles.detailText}>{dj.email || 'Pas d\'email'}</Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="call" size={14} color="#888" />
                        <Text style={styles.detailText}>{dj.telephone || 'Pas de telephone'}</Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="document-text" size={14} color="#888" />
                        <Text style={styles.detailText}>SIRET: {dj.siret || 'Non renseigne'}</Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="shield-checkmark" size={14} color="#888" />
                        <Text style={styles.detailText}>
                          Assurance: {dj.assurance_rc_organisme ? `${dj.assurance_rc_organisme} (${dj.assurance_rc_numero || ''})` : 'Non renseignee'}
                        </Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="map" size={14} color="#888" />
                        <Text style={styles.detailText}>
                          Zones: {(dj.departments_zones || []).join(', ') || 'Aucune'}
                        </Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="cash" size={14} color="#888" />
                        <Text style={styles.detailText}>Tarif: {dj.tarif_indicatif || '?'}€</Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="calendar" size={14} color="#888" />
                        <Text style={styles.detailText}>
                          Inscrit le: {dj.created_at ? new Date(dj.created_at).toLocaleDateString('fr-FR') : '?'}
                        </Text>
                      </View>
                      <View style={styles.detailRow}>
                        <Ionicons name="eye" size={14} color="#888" />
                        <Text style={styles.detailText}>Vues: {dj.nombre_vues || 0} | Avis: {dj.nombre_avis || 0} | Note: {dj.note_moyenne || 0}/5</Text>
                      </View>

                      {/* Actions */}
                      <View style={styles.djActions}>
                        <TouchableOpacity
                          style={[styles.actionBtn, statusInfo.label.includes('Actif') || statusInfo.label.includes('Essai') ? styles.btnDanger : styles.btnSuccess]}
                          onPress={() => handleToggleSubscription(dj.user_id)}
                        >
                          <Ionicons name={statusInfo.label.includes('Actif') || statusInfo.label.includes('Essai') ? 'eye-off' : 'eye'} size={16} color="#fff" />
                          <Text style={styles.actionBtnText}>
                            {statusInfo.label.includes('Actif') || statusInfo.label.includes('Essai') ? 'Desactiver' : 'Activer'}
                          </Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                          style={[styles.actionBtn, dj.boost_active ? styles.btnDanger : styles.btnBoost]}
                          onPress={() => handleToggleBoost(dj.user_id)}
                        >
                          <Ionicons name="star" size={16} color={dj.boost_active ? '#fff' : '#000'} />
                          <Text style={[styles.actionBtnText, !dj.boost_active && { color: '#000' }]}>
                            {dj.boost_active ? 'Retirer boost' : 'Booster'}
                          </Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                          style={[styles.actionBtn, styles.btnView]}
                          onPress={() => router.push(`/dj/${dj.user_id}`)}
                        >
                          <Ionicons name="open-outline" size={16} color="#fff" />
                          <Text style={styles.actionBtnText}>Voir</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                          style={[styles.actionBtn, styles.btnDelete]}
                          onPress={() => handleDeleteDJ(dj.user_id, dj.nom_de_scene || dj.nom)}
                        >
                          <Ionicons name="trash" size={16} color="#fff" />
                        </TouchableOpacity>

                        {(dj.subscription_status === 'expired' || dj.subscription_status === 'inactive') && (
                          <TouchableOpacity
                            style={[styles.actionBtn, { backgroundColor: '#F59E0B' }]}
                            onPress={() => handleSendReminder(dj.user_id, dj.nom_de_scene || 'DJ')}
                          >
                            <Ionicons name="mail" size={16} color="#000" />
                            <Text style={[styles.actionBtnText, { color: '#000' }]}>Relancer</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        )}

        {/* TAB: Contact Requests */}
        {activeTab === 'contacts' && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Demandes de contact clients</Text>

            {/* Delete Buttons */}
            {contacts.length > 0 && (
              <View style={{ flexDirection: 'row', marginHorizontal: 16, marginBottom: 12 }}>
                <TouchableOpacity
                  style={{ flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#10B981', paddingVertical: 10, borderRadius: 10, marginRight: 6 }}
                  onPress={() => handleDeleteContacts('read')}
                >
                  <Ionicons name="checkmark-circle" size={16} color="#fff" />
                  <Text style={{ color: '#fff', fontSize: 13, fontWeight: '700', marginLeft: 6 }}>
                    Suppr. lues ({contacts.filter(c => c.read).length})
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={{ flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#F59E0B', paddingVertical: 10, borderRadius: 10, marginRight: 6 }}
                  onPress={() => handleDeleteContacts('unread')}
                >
                  <Ionicons name="alert-circle" size={16} color="#000" />
                  <Text style={{ color: '#000', fontSize: 13, fontWeight: '700', marginLeft: 6 }}>
                    Suppr. non lues ({contacts.filter(c => !c.read).length})
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={{ flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#EF4444', paddingVertical: 10, borderRadius: 10 }}
                  onPress={() => handleDeleteContacts('all')}
                >
                  <Ionicons name="trash" size={16} color="#fff" />
                  <Text style={{ color: '#fff', fontSize: 13, fontWeight: '700', marginLeft: 6 }}>
                    Tout ({contacts.length})
                  </Text>
                </TouchableOpacity>
              </View>
            )}

            {contacts.length === 0 ? (
              <View style={styles.emptyState}>
                <Ionicons name="mail-open" size={48} color="#666" />
                <Text style={styles.emptyText}>Aucune demande de contact</Text>
              </View>
            ) : (
              contacts.map((req, index) => (
                <View key={index} style={styles.contactCard}>
                  <View style={styles.contactHeader}>
                    <Text style={styles.contactClient}>{req.client_nom || req.client_email}</Text>
                    <Text style={styles.contactDate}>
                      {req.created_at ? new Date(req.created_at).toLocaleDateString('fr-FR') : ''}
                    </Text>
                  </View>
                  <View style={styles.contactDetails}>
                    <View style={styles.detailRow}>
                      <Ionicons name="musical-notes" size={14} color="#8B5CF6" />
                      <Text style={styles.detailText}>Pour: {req.dj_nom}</Text>
                    </View>
                    <View style={styles.detailRow}>
                      <Ionicons name="mail" size={14} color="#888" />
                      <Text style={styles.detailText}>{req.client_email}</Text>
                    </View>
                    {req.client_telephone && (
                      <View style={styles.detailRow}>
                        <Ionicons name="call" size={14} color="#888" />
                        <Text style={styles.detailText}>{req.client_telephone}</Text>
                      </View>
                    )}
                    {req.message && (
                      <View style={styles.detailRow}>
                        <Ionicons name="chatbubble" size={14} color="#888" />
                        <Text style={[styles.detailText, { flex: 1 }]} numberOfLines={3}>{req.message}</Text>
                      </View>
                    )}
                    {req.type_evenement && (
                      <View style={styles.detailRow}>
                        <Ionicons name="calendar" size={14} color="#888" />
                        <Text style={styles.detailText}>{req.type_evenement} {req.date_evenement ? `— ${req.date_evenement}` : ''}</Text>
                      </View>
                    )}
                  </View>
                  <View style={[styles.statusBadge, { backgroundColor: req.read ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)', alignSelf: 'flex-start', marginTop: 8 }]}>
                    <Text style={[styles.statusText, { color: req.read ? '#10B981' : '#F59E0B' }]}>
                      {req.read ? 'Lu' : 'Non lu'}
                    </Text>
                  </View>
                </View>
              ))
            )}
          </View>
        )}

        {/* TAB: Stats */}
        {activeTab === 'stats' && stats && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Statistiques de la plateforme</Text>
            <View style={styles.statsGrid}>
              {[
                { icon: 'people', label: 'DJs inscrits', value: stats.total_djs, color: '#8B5CF6' },
                { icon: 'checkmark-circle', label: 'DJs actifs', value: stats.active_djs, color: '#10B981' },
                { icon: 'time', label: 'En essai gratuit', value: stats.trial_djs, color: '#F59E0B' },
                { icon: 'close-circle', label: 'Essai expire', value: stats.expired_djs, color: '#EF4444' },
                { icon: 'star', label: 'DJs boostes', value: stats.boosted_djs, color: '#F59E0B' },
                { icon: 'mail', label: 'Demandes contact', value: stats.total_contacts, color: '#3B82F6' },
                { icon: 'person', label: 'Utilisateurs', value: stats.total_users, color: '#6366F1' },
              ].map((stat, i) => (
                <View key={i} style={styles.statGridCard}>
                  <Ionicons name={stat.icon as any} size={28} color={stat.color} />
                  <Text style={styles.statGridNumber}>{stat.value}</Text>
                  <Text style={styles.statGridLabel}>{stat.label}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0B0B24' },
  header: { flexDirection: 'row', alignItems: 'center', padding: 20 },
  backBtn: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center', marginRight: 8 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#fff' },
  subtitle: { fontSize: 13, color: '#888', marginTop: 2 },
  statsRow: { flexDirection: 'row', paddingHorizontal: 16, gap: 8, marginBottom: 16 },
  statCard: {
    flex: 1, backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 12, padding: 12,
    borderLeftWidth: 3, alignItems: 'center',
  },
  statNumber: { fontSize: 22, fontWeight: 'bold', color: '#fff' },
  statLabel: { fontSize: 10, color: '#888', marginTop: 2 },
  tabBar: { flexDirection: 'row', marginHorizontal: 16, marginBottom: 16, backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 12, padding: 4 },
  tab: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 10, borderRadius: 10, gap: 6 },
  tabActive: { backgroundColor: 'rgba(139,92,246,0.15)' },
  tabText: { fontSize: 13, color: '#666', fontWeight: '500' },
  tabTextActive: { color: '#8B5CF6', fontWeight: '700' },
  section: { paddingHorizontal: 16 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#fff', marginBottom: 16 },
  searchBar: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 12, paddingHorizontal: 14, height: 48, marginBottom: 12, gap: 10,
  },
  searchInput: { flex: 1, color: '#fff', fontSize: 14 },
  crmLink: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    backgroundColor: 'rgba(139,92,246,0.1)', borderRadius: 10, padding: 12, marginBottom: 16, gap: 8,
  },
  crmLinkText: { color: '#8B5CF6', fontSize: 14, fontWeight: '600', flex: 1 },
  djCard: {
    backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 14, marginBottom: 10,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)', overflow: 'hidden',
  },
  djCardHeader: { flexDirection: 'row', alignItems: 'center', padding: 14 },
  djNameRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  djName: { fontSize: 16, fontWeight: '700', color: '#fff' },
  djCity: { fontSize: 12, color: '#888', marginTop: 2 },
  boostBadge: {
    backgroundColor: '#F59E0B', borderRadius: 10, width: 20, height: 20,
    alignItems: 'center', justifyContent: 'center',
  },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  statusText: { fontSize: 12, fontWeight: '700' },
  djDetails: {
    paddingHorizontal: 14, paddingBottom: 14,
    borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.06)', paddingTop: 12,
  },
  detailRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 6 },
  detailText: { fontSize: 13, color: '#bbb' },
  djActions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 12 },
  actionBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8,
  },
  actionBtnText: { fontSize: 12, fontWeight: '600', color: '#fff' },
  btnSuccess: { backgroundColor: '#10B981' },
  btnDanger: { backgroundColor: '#EF4444' },
  btnBoost: { backgroundColor: '#F59E0B' },
  btnView: { backgroundColor: '#3B82F6' },
  btnDelete: { backgroundColor: '#7F1D1D' },
  contactCard: {
    backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 14, padding: 14, marginBottom: 10,
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)',
  },
  contactHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  contactClient: { fontSize: 16, fontWeight: '700', color: '#fff' },
  contactDate: { fontSize: 12, color: '#888' },
  contactDetails: {},
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyText: { fontSize: 16, color: '#666', marginTop: 12 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  statGridCard: {
    width: '47%', backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 14, padding: 18,
    alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)',
  },
  statGridNumber: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginTop: 8 },
  statGridLabel: { fontSize: 12, color: '#888', marginTop: 4, textAlign: 'center' },
});
