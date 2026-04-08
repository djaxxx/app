import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../src/services/api';

export default function ReviewsManageScreen() {
  const router = useRouter();
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('pending');

  const loadReviews = async () => {
    try {
      const result = await api.getAllMyReviews();
      setReviews(result.reviews);
      setPendingCount(result.pending_count);
    } catch (error: any) {
      if (Platform.OS === 'web') window.alert(error.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { loadReviews(); }, []);

  const handleApprove = async (reviewId: string) => {
    try {
      await api.approveReview(reviewId);
      loadReviews();
    } catch (error: any) {
      if (Platform.OS === 'web') window.alert(error.message);
    }
  };

  const handleReject = async (reviewId: string) => {
    const doReject = async () => {
      try {
        await api.rejectReview(reviewId);
        loadReviews();
      } catch (error: any) {
        if (Platform.OS === 'web') window.alert(error.message);
      }
    };

    if (Platform.OS === 'web') {
      if (window.confirm('Rejeter cet avis ?')) doReject();
    } else {
      Alert.alert('Confirmer', 'Rejeter cet avis ?', [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Rejeter', style: 'destructive', onPress: doReject },
      ]);
    }
  };

  const filteredReviews = reviews.filter(r => filter === 'all' || r.status === filter);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#10B981';
      case 'rejected': return '#EF4444';
      default: return '#F59E0B';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'approved': return 'Approuvé';
      case 'rejected': return 'Rejeté';
      default: return 'En attente';
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
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadReviews(); }} tintColor="#8B5CF6" />}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Gestion des avis</Text>
            {pendingCount > 0 && (
              <Text style={styles.pendingBadge}>{pendingCount} en attente</Text>
            )}
          </View>
        </View>

        {/* Filters */}
        <View style={styles.filters}>
          {(['pending', 'approved', 'rejected', 'all'] as const).map(f => (
            <TouchableOpacity
              key={f}
              style={[styles.filterBtn, filter === f && styles.filterBtnActive]}
              onPress={() => setFilter(f)}
            >
              <Text style={[styles.filterText, filter === f && styles.filterTextActive]}>
                {f === 'pending' ? 'En attente' : f === 'approved' ? 'Approuvés' : f === 'rejected' ? 'Rejetés' : 'Tous'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Reviews */}
        <View style={styles.list}>
          {filteredReviews.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="chatbubbles-outline" size={48} color="#666" />
              <Text style={styles.emptyText}>Aucun avis {filter === 'pending' ? 'en attente' : ''}</Text>
            </View>
          ) : (
            filteredReviews.map(review => (
              <View key={review.review_id} style={styles.reviewCard}>
                <View style={styles.reviewHeader}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.reviewAuthor}>{review.client_nom}</Text>
                    <Text style={styles.reviewEmail}>{review.client_email}</Text>
                  </View>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(review.status) + '33' }]}>
                    <Text style={[styles.statusText, { color: getStatusColor(review.status) }]}>
                      {getStatusLabel(review.status)}
                    </Text>
                  </View>
                </View>

                <View style={styles.stars}>
                  {[1, 2, 3, 4, 5].map(star => (
                    <Ionicons key={star} name={star <= review.note ? 'star' : 'star-outline'} size={18} color="#FFD700" />
                  ))}
                </View>

                {review.type_evenement && (
                  <Text style={styles.eventType}>{review.type_evenement}{review.date_evenement ? ` — ${review.date_evenement}` : ''}</Text>
                )}

                <Text style={styles.reviewText}>{review.commentaire}</Text>

                {review.status === 'pending' && (
                  <View style={styles.actions}>
                    <TouchableOpacity style={styles.approveBtn} onPress={() => handleApprove(review.review_id)}>
                      <Ionicons name="checkmark" size={18} color="#fff" />
                      <Text style={styles.actionText}>Approuver</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.rejectBtn} onPress={() => handleReject(review.review_id)}>
                      <Ionicons name="close" size={18} color="#fff" />
                      <Text style={styles.actionText}>Rejeter</Text>
                    </TouchableOpacity>
                  </View>
                )}
              </View>
            ))
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0c0c0c' },
  header: { flexDirection: 'row', alignItems: 'center', padding: 20 },
  backBtn: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center', marginRight: 8 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#fff' },
  pendingBadge: { color: '#F59E0B', fontSize: 13, fontWeight: '600', marginTop: 2 },
  filters: { flexDirection: 'row', paddingHorizontal: 20, gap: 8, marginBottom: 16 },
  filterBtn: { backgroundColor: '#1a1a1a', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#2a2a2a' },
  filterBtnActive: { backgroundColor: '#8B5CF6', borderColor: '#8B5CF6' },
  filterText: { color: '#888', fontSize: 13, fontWeight: '600' },
  filterTextActive: { color: '#fff' },
  list: { paddingHorizontal: 20, paddingBottom: 40 },
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyText: { color: '#888', fontSize: 16, marginTop: 12 },
  reviewCard: { backgroundColor: '#1a1a1a', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#2a2a2a' },
  reviewHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  reviewAuthor: { fontSize: 16, fontWeight: 'bold', color: '#fff' },
  reviewEmail: { fontSize: 12, color: '#666', marginTop: 2 },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10 },
  statusText: { fontSize: 12, fontWeight: '700' },
  stars: { flexDirection: 'row', marginVertical: 8, gap: 2 },
  eventType: { color: '#8B5CF6', fontSize: 13, marginBottom: 6, fontWeight: '600' },
  reviewText: { color: '#ccc', fontSize: 14, lineHeight: 20 },
  actions: { flexDirection: 'row', marginTop: 14, gap: 10 },
  approveBtn: { flex: 1, flexDirection: 'row', backgroundColor: '#10B981', borderRadius: 10, padding: 12, alignItems: 'center', justifyContent: 'center', gap: 6 },
  rejectBtn: { flex: 1, flexDirection: 'row', backgroundColor: '#EF4444', borderRadius: 10, padding: 12, alignItems: 'center', justifyContent: 'center', gap: 6 },
  actionText: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
});
