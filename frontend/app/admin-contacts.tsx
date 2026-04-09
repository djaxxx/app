import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Platform,
  RefreshControl,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../src/services/api';
import { useAuthStore } from '../src/stores/authStore';

type TabType = 'all' | 'dj' | 'client';
type FilterStatus = '' | 'active' | 'inactive' | 'nouveau' | 'lu';

export default function AdminContactsScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [contacts, setContacts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [searchText, setSearchText] = useState('');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalContacts, setTotalContacts] = useState(0);
  const [showStats, setShowStats] = useState(false);

  const loadContacts = useCallback(async (page = 1) => {
    try {
      const params: any = { page, limit: 30 };
      if (activeTab !== 'all') params.type = activeTab;
      if (filterStatus) params.status = filterStatus;
      if (searchText.trim()) params.search = searchText.trim();
      const result = await api.adminGetContacts(params);
      setContacts(result.contacts);
      setTotalPages(result.pages);
      setTotalContacts(result.total);
      setCurrentPage(page);
    } catch (error: any) {
      if (error.message?.includes('403')) {
        router.back();
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeTab, filterStatus, searchText]);

  const loadStats = async () => {
    try {
      const result = await api.adminGetContactsStats();
      setStats(result);
    } catch (e) {
      console.error('Stats error:', e);
    }
  };

  useEffect(() => {
    setLoading(true);
    setCurrentPage(1);
    loadContacts(1);
  }, [activeTab, filterStatus]);

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setLoading(true);
      setCurrentPage(1);
      loadContacts(1);
    }, 400);
    return () => clearTimeout(timeout);
  }, [searchText]);

  const handleExportCSV = () => {
    const params: any = {};
    if (activeTab !== 'all') params.type = activeTab;
    if (filterStatus) params.status = filterStatus;
    if (searchText.trim()) params.search = searchText.trim();
    const url = api.getExportCsvUrl(params);
    if (Platform.OS === 'web') {
      window.open(url, '_blank');
    } else {
      Linking.openURL(url);
    }
  };

  const formatDate = (date: any) => {
    if (!date) return '-';
    try {
      const d = new Date(date);
      return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch {
      return '-';
    }
  };

  if (loading && contacts.length === 0) {
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
          <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadContacts(currentPage); loadStats(); }} tintColor="#8B5CF6" />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Base Contacts CRM</Text>
            <Text style={styles.subtitle}>{totalContacts} contact(s)</Text>
          </View>
          <TouchableOpacity style={styles.exportButton} onPress={handleExportCSV}>
            <Ionicons name="download-outline" size={18} color="#fff" />
            <Text style={styles.exportButtonText}>CSV</Text>
          </TouchableOpacity>
        </View>

        {/* Stats Toggle */}
        <TouchableOpacity style={styles.statsToggle} onPress={() => setShowStats(!showStats)}>
          <Ionicons name={showStats ? 'stats-chart' : 'stats-chart-outline'} size={18} color="#8B5CF6" />
          <Text style={styles.statsToggleText}>{showStats ? 'Masquer' : 'Voir'} les statistiques</Text>
          <Ionicons name={showStats ? 'chevron-up' : 'chevron-down'} size={16} color="#8B5CF6" />
        </TouchableOpacity>

        {/* Stats Panel */}
        {showStats && stats && (
          <View style={styles.statsPanel}>
            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{stats.djs?.total || 0}</Text>
                <Text style={styles.statLabel}>DJs total</Text>
              </View>
              <View style={[styles.statCard, styles.statCardGreen]}>
                <Text style={styles.statNumber}>{stats.djs?.active || 0}</Text>
                <Text style={styles.statLabel}>DJs actifs</Text>
              </View>
              <View style={[styles.statCard, styles.statCardRed]}>
                <Text style={styles.statNumber}>{stats.djs?.inactive || 0}</Text>
                <Text style={styles.statLabel}>DJs inactifs</Text>
              </View>
              <View style={[styles.statCard, styles.statCardGold]}>
                <Text style={styles.statNumber}>{stats.djs?.boosted || 0}</Text>
                <Text style={styles.statLabel}>Boostés</Text>
              </View>
            </View>
            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{stats.clients?.unique_clients || 0}</Text>
                <Text style={styles.statLabel}>Clients uniques</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statNumber}>{stats.clients?.total_requests || 0}</Text>
                <Text style={styles.statLabel}>Demandes total</Text>
              </View>
              <View style={[styles.statCard, styles.statCardOrange]}>
                <Text style={styles.statNumber}>{stats.clients?.unread || 0}</Text>
                <Text style={styles.statLabel}>Non lues</Text>
              </View>
            </View>

            {stats.djs?.by_region?.length > 0 && (
              <View style={styles.segmentSection}>
                <Text style={styles.segmentTitle}>DJs par région</Text>
                {stats.djs.by_region.slice(0, 8).map((r: any, i: number) => (
                  <View key={i} style={styles.segmentRow}>
                    <Text style={styles.segmentName}>{r.name}</Text>
                    <View style={styles.segmentBar}>
                      <View style={[styles.segmentFill, { width: `${Math.min(100, (r.count / (stats.djs.total || 1)) * 100)}%` }]} />
                    </View>
                    <Text style={styles.segmentCount}>{r.count}</Text>
                  </View>
                ))}
              </View>
            )}

            {stats.clients?.by_event_type?.length > 0 && (
              <View style={styles.segmentSection}>
                <Text style={styles.segmentTitle}>Demandes par type</Text>
                {stats.clients.by_event_type.map((e: any, i: number) => (
                  <View key={i} style={styles.segmentRow}>
                    <Text style={styles.segmentName}>{e.name}</Text>
                    <Text style={styles.segmentCount}>{e.count}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* Tabs */}
        <View style={styles.tabs}>
          {([
            { key: 'all', label: 'Tous' },
            { key: 'dj', label: 'DJs' },
            { key: 'client', label: 'Clients' },
          ] as { key: TabType; label: string }[]).map((tab) => (
            <TouchableOpacity
              key={tab.key}
              style={[styles.tab, activeTab === tab.key && styles.tabActive]}
              onPress={() => { setActiveTab(tab.key); setFilterStatus(''); }}
            >
              <Text style={[styles.tabText, activeTab === tab.key && styles.tabTextActive]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Search */}
        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color="#666" />
          <TextInput
            style={styles.searchInput}
            value={searchText}
            onChangeText={setSearchText}
            placeholder="Rechercher par nom, email, ville..."
            placeholderTextColor="#555"
          />
          {searchText ? (
            <TouchableOpacity onPress={() => setSearchText('')}>
              <Ionicons name="close-circle" size={18} color="#666" />
            </TouchableOpacity>
          ) : null}
        </View>

        {/* Filter chips */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filtersScroll}>
          <View style={styles.filters}>
            <TouchableOpacity
              style={[styles.filterChip, !filterStatus && styles.filterChipActive]}
              onPress={() => setFilterStatus('')}
            >
              <Text style={[styles.filterChipText, !filterStatus && styles.filterChipTextActive]}>Tous</Text>
            </TouchableOpacity>
            {activeTab !== 'client' && (
              <>
                <TouchableOpacity
                  style={[styles.filterChip, filterStatus === 'active' && styles.filterChipActive]}
                  onPress={() => setFilterStatus('active')}
                >
                  <Text style={[styles.filterChipText, filterStatus === 'active' && styles.filterChipTextActive]}>Actifs</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.filterChip, filterStatus === 'inactive' && styles.filterChipActive]}
                  onPress={() => setFilterStatus('inactive')}
                >
                  <Text style={[styles.filterChipText, filterStatus === 'inactive' && styles.filterChipTextActive]}>Inactifs</Text>
                </TouchableOpacity>
              </>
            )}
            {activeTab !== 'dj' && (
              <>
                <TouchableOpacity
                  style={[styles.filterChip, filterStatus === 'nouveau' && styles.filterChipActive]}
                  onPress={() => setFilterStatus('nouveau')}
                >
                  <Text style={[styles.filterChipText, filterStatus === 'nouveau' && styles.filterChipTextActive]}>Non lus</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.filterChip, filterStatus === 'lu' && styles.filterChipActive]}
                  onPress={() => setFilterStatus('lu')}
                >
                  <Text style={[styles.filterChipText, filterStatus === 'lu' && styles.filterChipTextActive]}>Lus</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </ScrollView>

        {/* Contacts List */}
        <View style={styles.listContainer}>
          {loading ? (
            <ActivityIndicator size="small" color="#8B5CF6" style={{ marginTop: 20 }} />
          ) : contacts.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="people-outline" size={48} color="#444" />
              <Text style={styles.emptyText}>Aucun contact trouvé</Text>
            </View>
          ) : (
            contacts.map((contact, index) => (
              <View key={`${contact.contact_type}-${contact.id}-${index}`} style={styles.contactCard}>
                <View style={styles.contactHeader}>
                  <View style={[styles.typeBadge, contact.contact_type === 'dj' ? styles.typeDJ : styles.typeClient]}>
                    <Ionicons name={contact.contact_type === 'dj' ? 'musical-notes' : 'person'} size={12} color="#fff" />
                    <Text style={styles.typeBadgeText}>{contact.contact_type === 'dj' ? 'DJ' : 'Client'}</Text>
                  </View>
                  {contact.subscription_status === 'active' && (
                    <View style={styles.activeBadge}>
                      <Text style={styles.activeBadgeText}>Actif</Text>
                    </View>
                  )}
                  {contact.boost_active && (
                    <View style={styles.boostBadge}>
                      <Ionicons name="star" size={10} color="#000" />
                    </View>
                  )}
                </View>

                <Text style={styles.contactName}>
                  {contact.nom_de_scene || contact.nom || 'Sans nom'}
                </Text>
                {contact.nom_de_scene && contact.nom ? (
                  <Text style={styles.contactSubname}>{contact.nom}</Text>
                ) : null}

                <View style={styles.contactDetails}>
                  {contact.email ? (
                    <View style={styles.detailRow}>
                      <Ionicons name="mail-outline" size={14} color="#8B5CF6" />
                      <Text style={styles.detailText}>{contact.email}</Text>
                    </View>
                  ) : null}
                  {contact.telephone ? (
                    <View style={styles.detailRow}>
                      <Ionicons name="call-outline" size={14} color="#8B5CF6" />
                      <Text style={styles.detailText}>{contact.telephone}</Text>
                    </View>
                  ) : null}
                  {contact.ville ? (
                    <View style={styles.detailRow}>
                      <Ionicons name="location-outline" size={14} color="#8B5CF6" />
                      <Text style={styles.detailText}>
                        {contact.ville}
                        {contact.department_name ? ` — ${contact.department_name}` : ''}
                        {contact.region_name ? ` (${contact.region_name})` : ''}
                      </Text>
                    </View>
                  ) : null}
                  {contact.contact_type === 'dj' && contact.tarif_indicatif ? (
                    <View style={styles.detailRow}>
                      <Ionicons name="cash-outline" size={14} color="#8B5CF6" />
                      <Text style={styles.detailText}>{contact.tarif_indicatif}</Text>
                    </View>
                  ) : null}
                  {contact.contact_type === 'dj' && contact.siret ? (
                    <View style={styles.detailRow}>
                      <Ionicons name="business-outline" size={14} color="#666" />
                      <Text style={styles.detailTextMuted}>SIRET: {contact.siret}</Text>
                    </View>
                  ) : null}
                  {contact.contact_type === 'client' && contact.type_evenement ? (
                    <View style={styles.detailRow}>
                      <Ionicons name="calendar-outline" size={14} color="#8B5CF6" />
                      <Text style={styles.detailText}>{contact.type_evenement} {contact.date_evenement ? `— ${contact.date_evenement}` : ''}</Text>
                    </View>
                  ) : null}
                </View>

                <Text style={styles.dateText}>{formatDate(contact.created_at)}</Text>
              </View>
            ))
          )}
        </View>

        {/* Pagination */}
        {totalPages > 1 && (
          <View style={styles.pagination}>
            <TouchableOpacity
              style={[styles.pageButton, currentPage <= 1 && styles.pageButtonDisabled]}
              onPress={() => currentPage > 1 && loadContacts(currentPage - 1)}
              disabled={currentPage <= 1}
            >
              <Ionicons name="chevron-back" size={18} color={currentPage <= 1 ? '#444' : '#fff'} />
            </TouchableOpacity>
            <Text style={styles.pageText}>
              Page {currentPage} / {totalPages}
            </Text>
            <TouchableOpacity
              style={[styles.pageButton, currentPage >= totalPages && styles.pageButtonDisabled]}
              onPress={() => currentPage < totalPages && loadContacts(currentPage + 1)}
              disabled={currentPage >= totalPages}
            >
              <Ionicons name="chevron-forward" size={18} color={currentPage >= totalPages ? '#444' : '#fff'} />
            </TouchableOpacity>
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
  backButton: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center', marginRight: 8 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#fff' },
  subtitle: { fontSize: 13, color: '#888', marginTop: 2 },
  exportButton: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#10B981', paddingHorizontal: 16, paddingVertical: 10, borderRadius: 10,
  },
  exportButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 14 },
  statsToggle: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    marginHorizontal: 20, marginBottom: 12, paddingVertical: 8,
  },
  statsToggleText: { color: '#8B5CF6', fontSize: 14, fontWeight: '500' },
  statsPanel: { marginHorizontal: 20, marginBottom: 16 },
  statsRow: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  statCard: {
    flex: 1, backgroundColor: '#12123A', borderRadius: 10, padding: 12,
    alignItems: 'center', borderWidth: 1, borderColor: '#1E1E4A',
  },
  statCardGreen: { borderColor: 'rgba(16,185,129,0.4)' },
  statCardRed: { borderColor: 'rgba(239,68,68,0.4)' },
  statCardGold: { borderColor: 'rgba(255,215,0,0.4)' },
  statCardOrange: { borderColor: 'rgba(245,158,11,0.4)' },
  statNumber: { fontSize: 22, fontWeight: 'bold', color: '#fff' },
  statLabel: { fontSize: 11, color: '#888', marginTop: 4 },
  segmentSection: { marginTop: 12, backgroundColor: '#12123A', borderRadius: 10, padding: 14, borderWidth: 1, borderColor: '#1E1E4A' },
  segmentTitle: { fontSize: 14, fontWeight: '600', color: '#8B5CF6', marginBottom: 10 },
  segmentRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  segmentName: { color: '#ccc', fontSize: 12, width: 120 },
  segmentBar: { flex: 1, height: 6, backgroundColor: '#1E1E4A', borderRadius: 3, marginHorizontal: 8 },
  segmentFill: { height: 6, backgroundColor: '#8B5CF6', borderRadius: 3 },
  segmentCount: { color: '#fff', fontSize: 12, fontWeight: '600', width: 30, textAlign: 'right' },
  tabs: { flexDirection: 'row', marginHorizontal: 20, marginBottom: 12, backgroundColor: '#12123A', borderRadius: 10, padding: 4 },
  tab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 8 },
  tabActive: { backgroundColor: '#8B5CF6' },
  tabText: { color: '#888', fontSize: 14, fontWeight: '500' },
  tabTextActive: { color: '#fff', fontWeight: 'bold' },
  searchBar: {
    flexDirection: 'row', alignItems: 'center', marginHorizontal: 20, marginBottom: 10,
    backgroundColor: '#12123A', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 10,
    borderWidth: 1, borderColor: '#1E1E4A',
  },
  searchInput: { flex: 1, color: '#fff', fontSize: 14, marginLeft: 10 },
  filtersScroll: { marginBottom: 12 },
  filters: { flexDirection: 'row', paddingHorizontal: 20, gap: 8 },
  filterChip: {
    paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20,
    backgroundColor: '#12123A', borderWidth: 1, borderColor: '#1E1E4A',
  },
  filterChipActive: { backgroundColor: '#8B5CF6', borderColor: '#8B5CF6' },
  filterChipText: { color: '#888', fontSize: 13 },
  filterChipTextActive: { color: '#fff', fontWeight: '600' },
  listContainer: { paddingHorizontal: 20 },
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyText: { color: '#666', fontSize: 15, marginTop: 12 },
  contactCard: {
    backgroundColor: '#12123A', borderRadius: 12, padding: 16, marginBottom: 10,
    borderWidth: 1, borderColor: '#1E1E4A',
  },
  contactHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  typeBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6,
  },
  typeDJ: { backgroundColor: 'rgba(139,92,246,0.3)' },
  typeClient: { backgroundColor: 'rgba(59,130,246,0.3)' },
  typeBadgeText: { color: '#fff', fontSize: 11, fontWeight: '600' },
  activeBadge: { backgroundColor: 'rgba(16,185,129,0.2)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  activeBadgeText: { color: '#10B981', fontSize: 11, fontWeight: '600' },
  boostBadge: { backgroundColor: '#FFD700', paddingHorizontal: 6, paddingVertical: 3, borderRadius: 6 },
  contactName: { fontSize: 16, fontWeight: 'bold', color: '#fff' },
  contactSubname: { fontSize: 13, color: '#888', marginTop: 2 },
  contactDetails: { marginTop: 10 },
  detailRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 5 },
  detailText: { color: '#ccc', fontSize: 13, flex: 1 },
  detailTextMuted: { color: '#666', fontSize: 12, flex: 1 },
  dateText: { color: '#555', fontSize: 11, marginTop: 8, textAlign: 'right' },
  pagination: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 16, paddingVertical: 16 },
  pageButton: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center', backgroundColor: '#12123A', borderRadius: 10 },
  pageButtonDisabled: { opacity: 0.3 },
  pageText: { color: '#888', fontSize: 14 },
});
