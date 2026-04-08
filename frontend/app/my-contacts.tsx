import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Linking,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../src/services/api';

interface ContactRequest {
  request_id: string;
  dj_user_id: string;
  client_nom: string;
  client_email: string;
  client_telephone?: string;
  message: string;
  type_evenement?: string;
  date_evenement?: string;
  lieu_evenement?: string;
  budget?: string;
  status: string;
  read: boolean;
  created_at: string;
}

export default function MyContactsScreen() {
  const router = useRouter();
  const [contacts, setContacts] = useState<ContactRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<string | null>(null);

  const loadContacts = async () => {
    try {
      const data = await api.getDJContacts(filter || undefined);
      setContacts(data);
    } catch (error) {
      console.error('Error loading contacts:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, [filter]);

  const onRefresh = () => {
    setRefreshing(true);
    loadContacts();
  };

  const markAsRead = async (requestId: string) => {
    try {
      await api.markContactRead(requestId);
      setContacts(prev =>
        prev.map(c =>
          c.request_id === requestId ? { ...c, read: true } : c
        )
      );
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const handleCall = (phone: string) => {
    Linking.openURL(`tel:${phone}`);
  };

  const handleEmail = (email: string) => {
    Linking.openURL(`mailto:${email}`);
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  const unreadCount = contacts.filter(c => !c.read).length;

  const filters = [
    { key: null, label: 'Toutes' },
    { key: 'nouveau', label: 'Nouvelles' },
  ];

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#8B5CF6" style={styles.loader} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.title}>Mes demandes</Text>
        {unreadCount > 0 && (
          <View style={styles.unreadBadge}>
            <Text style={styles.unreadBadgeText}>{unreadCount}</Text>
          </View>
        )}
      </View>

      {/* Filters */}
      <View style={styles.filtersRow}>
        {filters.map(f => (
          <TouchableOpacity
            key={f.key || 'all'}
            style={[styles.filterChip, filter === f.key && styles.filterChipActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterChipText, filter === f.key && styles.filterChipTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#8B5CF6" />
        }
        contentContainerStyle={styles.scrollContent}
      >
        {contacts.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="mail-open-outline" size={64} color="#444" />
            <Text style={styles.emptyStateText}>Aucune demande</Text>
            <Text style={styles.emptyStateSubtext}>
              Les demandes de contact des clients apparaîtront ici
            </Text>
          </View>
        ) : (
          contacts.map((contact) => (
            <TouchableOpacity
              key={contact.request_id}
              style={[styles.contactCard, !contact.read && styles.contactCardUnread]}
              onPress={() => markAsRead(contact.request_id)}
              activeOpacity={0.7}
            >
              {/* Unread indicator */}
              {!contact.read && <View style={styles.unreadDot} />}

              {/* Client info header */}
              <View style={styles.contactHeader}>
                <View style={styles.clientInfo}>
                  <View style={styles.avatarCircle}>
                    <Ionicons name="person" size={20} color="#8B5CF6" />
                  </View>
                  <View style={styles.clientDetails}>
                    <Text style={styles.clientName}>{contact.client_nom}</Text>
                    <Text style={styles.contactDate}>{formatDate(contact.created_at)}</Text>
                  </View>
                </View>
                {!contact.read && (
                  <View style={styles.newBadge}>
                    <Text style={styles.newBadgeText}>Nouveau</Text>
                  </View>
                )}
              </View>

              {/* Event details */}
              {(contact.type_evenement || contact.date_evenement || contact.lieu_evenement) && (
                <View style={styles.eventDetails}>
                  {contact.type_evenement && (
                    <View style={styles.eventTag}>
                      <Ionicons name="musical-notes" size={14} color="#8B5CF6" />
                      <Text style={styles.eventTagText}>{contact.type_evenement}</Text>
                    </View>
                  )}
                  {contact.date_evenement && (
                    <View style={styles.eventTag}>
                      <Ionicons name="calendar" size={14} color="#F59E0B" />
                      <Text style={styles.eventTagText}>{contact.date_evenement}</Text>
                    </View>
                  )}
                  {contact.lieu_evenement && (
                    <View style={styles.eventTag}>
                      <Ionicons name="location" size={14} color="#10B981" />
                      <Text style={styles.eventTagText}>{contact.lieu_evenement}</Text>
                    </View>
                  )}
                </View>
              )}

              {/* Message */}
              <Text style={styles.messageText} numberOfLines={3}>
                {contact.message}
              </Text>

              {/* Action buttons */}
              <View style={styles.actionButtons}>
                {contact.client_telephone && (
                  <TouchableOpacity
                    style={styles.actionBtn}
                    onPress={() => handleCall(contact.client_telephone!)}
                  >
                    <Ionicons name="call" size={18} color="#10B981" />
                    <Text style={styles.actionBtnText}>Appeler</Text>
                  </TouchableOpacity>
                )}
                <TouchableOpacity
                  style={styles.actionBtn}
                  onPress={() => handleEmail(contact.client_email)}
                >
                  <Ionicons name="mail" size={18} color="#3B82F6" />
                  <Text style={styles.actionBtnText}>Email</Text>
                </TouchableOpacity>
              </View>
            </TouchableOpacity>
          ))
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
    flex: 1,
  },
  unreadBadge: {
    backgroundColor: '#EF4444',
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  unreadBadgeText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  filtersRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  filterChip: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: '#8B5CF6',
  },
  filterChipText: {
    color: '#888',
    fontSize: 14,
  },
  filterChipTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 40,
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
  contactCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    position: 'relative',
  },
  contactCardUnread: {
    borderLeftWidth: 3,
    borderLeftColor: '#8B5CF6',
  },
  unreadDot: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#8B5CF6',
  },
  contactHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  clientInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  avatarCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(139, 92, 246, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  clientDetails: {
    marginLeft: 12,
    flex: 1,
  },
  clientName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  contactDate: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
  },
  newBadge: {
    backgroundColor: 'rgba(139, 92, 246, 0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  newBadgeText: {
    color: '#8B5CF6',
    fontSize: 12,
    fontWeight: '600',
  },
  eventDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  eventTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0c0c0c',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 4,
  },
  eventTagText: {
    color: '#ccc',
    fontSize: 12,
    marginLeft: 4,
  },
  messageText: {
    color: '#aaa',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  actionButtons: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#2a2a2a',
    paddingTop: 12,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0c0c0c',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    marginRight: 10,
  },
  actionBtnText: {
    color: '#ccc',
    fontSize: 14,
    marginLeft: 6,
  },
});
