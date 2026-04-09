import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../src/services/api';

interface ZoneDetail {
  code: string;
  name: string;
  is_primary: boolean;
}

interface DeptOption {
  code: string;
  name: string;
  selected: boolean;
}

export default function ZoneManagementScreen() {
  const [zoneStatus, setZoneStatus] = useState<any>(null);
  const [allDepts, setAllDepts] = useState<DeptOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [removing, setRemoving] = useState<string | null>(null);
  const [showPicker, setShowPicker] = useState(false);
  const [searchDept, setSearchDept] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [status, depts] = await Promise.all([
        api.getZoneStatus(),
        api.getAvailableDepartments(),
      ]);
      setZoneStatus(status);
      setAllDepts(depts);
    } catch (error) {
      console.error('Error loading zone data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddDepartment = async (deptCode: string) => {
    setAdding(true);
    try {
      const originUrl = Platform.OS === 'web' ? window.location.origin : '';
      const result = await api.addDepartmentZone(deptCode, originUrl);
      if (result.checkout_url) {
        if (Platform.OS === 'web') {
          window.location.href = result.checkout_url;
        } else {
          const { Linking } = require('react-native');
          Linking.openURL(result.checkout_url);
        }
      }
    } catch (error: any) {
      const msg = error.message || 'Erreur';
      if (Platform.OS === 'web') {
        window.alert(msg);
      }
    } finally {
      setAdding(false);
      setShowPicker(false);
    }
  };

  const handleRemoveDepartment = async (deptCode: string) => {
    const doRemove = async () => {
      setRemoving(deptCode);
      try {
        await api.removeDepartmentZone(deptCode);
        await loadData();
      } catch (error: any) {
        const msg = error.message || 'Erreur';
        if (Platform.OS === 'web') {
          window.alert(msg);
        }
      } finally {
        setRemoving(null);
      }
    };

    if (Platform.OS === 'web') {
      if (window.confirm('Retirer ce département de votre zone ?')) {
        await doRemove();
      }
    } else {
      const { Alert } = require('react-native');
      Alert.alert('Confirmer', 'Retirer ce département de votre zone ?', [
        { text: 'Annuler', style: 'cancel' },
        { text: 'Retirer', style: 'destructive', onPress: doRemove },
      ]);
    }
  };

  const filteredDepts = allDepts.filter(
    d => !d.selected && (
      d.name.toLowerCase().includes(searchDept.toLowerCase()) ||
      d.code.includes(searchDept)
    )
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#8B5CF6" style={{ flex: 1 }} />
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
          <Text style={styles.title}>Ma zone d'intervention</Text>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={22} color="#8B5CF6" />
          <Text style={styles.infoText}>
            Votre département principal est inclus dans l'abonnement.{"\n"}
            Ajoutez jusqu'à 3 départements supplémentaires (20€/an chacun).
          </Text>
        </View>

        {/* Counter */}
        <View style={styles.counterRow}>
          <Text style={styles.counterText}>
            {zoneStatus?.total_departments || 0} / {zoneStatus?.max_departments || 4} départements
          </Text>
          <View style={styles.counterBar}>
            {[1, 2, 3, 4].map(i => (
              <View
                key={i}
                style={[
                  styles.counterDot,
                  i <= (zoneStatus?.total_departments || 0) && styles.counterDotActive,
                ]}
              />
            ))}
          </View>
        </View>

        {/* Current Zones */}
        <Text style={styles.sectionTitle}>Mes départements actifs</Text>
        {zoneStatus?.zones_detail?.map((zone: ZoneDetail) => (
          <View key={zone.code} style={[styles.zoneCard, zone.is_primary && styles.zoneCardPrimary]}>
            <View style={styles.zoneInfo}>
              <Text style={styles.zoneDeptCode}>{zone.code}</Text>
              <View>
                <Text style={styles.zoneName}>{zone.name}</Text>
                {zone.is_primary && (
                  <Text style={styles.primaryBadge}>Département principal (inclus)</Text>
                )}
              </View>
            </View>
            {!zone.is_primary && (
              <TouchableOpacity
                style={styles.removeBtn}
                onPress={() => handleRemoveDepartment(zone.code)}
                disabled={removing === zone.code}
              >
                {removing === zone.code ? (
                  <ActivityIndicator size="small" color="#EF4444" />
                ) : (
                  <Ionicons name="close-circle" size={24} color="#EF4444" />
                )}
              </TouchableOpacity>
            )}
          </View>
        ))}

        {/* Add Department Button */}
        {(zoneStatus?.total_departments || 0) < (zoneStatus?.max_departments || 4) && (
          <>
            {!showPicker ? (
              <TouchableOpacity
                style={styles.addButton}
                onPress={() => setShowPicker(true)}
              >
                <Ionicons name="add-circle" size={24} color="#8B5CF6" />
                <Text style={styles.addButtonText}>
                  Ajouter un département (20€/an)
                </Text>
              </TouchableOpacity>
            ) : (
              <View style={styles.pickerContainer}>
                <View style={styles.pickerHeader}>
                  <Text style={styles.pickerTitle}>Choisir un département</Text>
                  <TouchableOpacity onPress={() => setShowPicker(false)}>
                    <Ionicons name="close" size={24} color="#888" />
                  </TouchableOpacity>
                </View>
                <TextInput
                  style={styles.searchInput}
                  placeholder="Rechercher un département..."
                  placeholderTextColor="#666"
                  value={searchDept}
                  onChangeText={setSearchDept}
                />
                <ScrollView style={styles.deptList} nestedScrollEnabled>
                  {filteredDepts.slice(0, 20).map(dept => (
                    <TouchableOpacity
                      key={dept.code}
                      style={styles.deptItem}
                      onPress={() => handleAddDepartment(dept.code)}
                      disabled={adding}
                    >
                      <Text style={styles.deptItemCode}>{dept.code}</Text>
                      <Text style={styles.deptItemName}>{dept.name}</Text>
                      <View style={styles.deptItemPrice}>
                        <Text style={styles.deptItemPriceText}>20€/an</Text>
                      </View>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
                {adding && (
                  <View style={styles.addingOverlay}>
                    <ActivityIndicator size="large" color="#8B5CF6" />
                    <Text style={styles.addingText}>Redirection vers le paiement...</Text>
                  </View>
                )}
              </View>
            )}
          </>
        )}

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
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
  infoCard: {
    flexDirection: 'row',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)',
    borderRadius: 12,
    marginHorizontal: 20,
    padding: 14,
    marginBottom: 20,
    alignItems: 'flex-start',
  },
  infoText: {
    color: '#ccc',
    fontSize: 13,
    marginLeft: 10,
    flex: 1,
    lineHeight: 20,
  },
  counterRow: {
    marginHorizontal: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  counterText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  counterBar: {
    flexDirection: 'row',
    gap: 8,
  },
  counterDot: {
    width: 40,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#1E1E4A',
  },
  counterDotActive: {
    backgroundColor: '#8B5CF6',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  zoneCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12123A',
    borderRadius: 12,
    marginHorizontal: 20,
    marginBottom: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  zoneCardPrimary: {
    borderColor: '#8B5CF6',
  },
  zoneInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  zoneDeptCode: {
    color: '#8B5CF6',
    fontSize: 18,
    fontWeight: 'bold',
    width: 36,
    marginRight: 12,
  },
  zoneName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  primaryBadge: {
    color: '#8B5CF6',
    fontSize: 12,
    marginTop: 2,
  },
  removeBtn: {
    padding: 8,
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    borderWidth: 1,
    borderColor: '#8B5CF6',
    borderStyle: 'dashed',
    borderRadius: 12,
    marginHorizontal: 20,
    marginTop: 8,
    padding: 16,
  },
  addButtonText: {
    color: '#8B5CF6',
    fontSize: 15,
    fontWeight: '600',
    marginLeft: 8,
  },
  pickerContainer: {
    backgroundColor: '#12123A',
    borderRadius: 16,
    marginHorizontal: 20,
    marginTop: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  pickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#1E1E4A',
  },
  pickerTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  searchInput: {
    backgroundColor: '#0B0B24',
    color: '#fff',
    padding: 12,
    margin: 12,
    borderRadius: 10,
    fontSize: 15,
  },
  deptList: {
    maxHeight: 300,
  },
  deptItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#1E1E4A',
  },
  deptItemCode: {
    color: '#8B5CF6',
    fontSize: 16,
    fontWeight: 'bold',
    width: 36,
  },
  deptItemName: {
    color: '#fff',
    fontSize: 15,
    flex: 1,
  },
  deptItemPrice: {
    backgroundColor: 'rgba(139, 92, 246, 0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  deptItemPriceText: {
    color: '#8B5CF6',
    fontSize: 12,
    fontWeight: '600',
  },
  addingOverlay: {
    padding: 20,
    alignItems: 'center',
  },
  addingText: {
    color: '#ccc',
    marginTop: 8,
    fontSize: 14,
  },
});
