import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../src/stores/authStore';
import { api } from '../src/services/api';
import { Button } from '../src/components/Button';
import { ImageUpload, GalleryUpload } from '../src/components/ImageUpload';
import { DJProfile, EventType } from '../src/types';

export default function EditDJProfileScreen() {
  const router = useRouter();
  const { user, isAuthenticated, checkAuth } = useAuthStore();
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<DJProfile | null>(null);

  const [formData, setFormData] = useState({
    description: '',
    annees_experience: '',
    types_evenements: [] as string[],
    materiel_son: '',
    materiel_lumiere: '',
    tarif_indicatif: '',
    instagram: '',
    tiktok: '',
    youtube: '',
    google_page: '',
    site_internet: '',
    photo_profil: '',
    galerie_photos: [] as string[],
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        const [profileData, types] = await Promise.all([
          api.getMyDJProfile(),
          api.getEventTypes(),
        ]);
        setProfile(profileData);
        setEventTypes(types);
        setFormData({
          description: profileData.description || '',
          annees_experience: profileData.annees_experience?.toString() || '',
          types_evenements: profileData.types_evenements || [],
          materiel_son: profileData.materiel_son || '',
          materiel_lumiere: profileData.materiel_lumiere || '',
          tarif_indicatif: profileData.tarif_indicatif || '',
          instagram: profileData.instagram || '',
          tiktok: profileData.tiktok || '',
          youtube: profileData.youtube || '',
          google_page: profileData.google_page || '',
          site_internet: profileData.site_internet || '',
          photo_profil: profileData.photo_profil || '',
          galerie_photos: profileData.galerie_photos || [],
        });
      } catch (error) {
        console.error('Error loading profile:', error);
        Alert.alert('Erreur', 'Impossible de charger le profil');
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const toggleEventType = (typeId: string) => {
    setFormData(prev => ({
      ...prev,
      types_evenements: prev.types_evenements.includes(typeId)
        ? prev.types_evenements.filter(t => t !== typeId)
        : [...prev.types_evenements, typeId],
    }));
  };

  const extractPrice = (tarif: string): number => {
    if (!tarif) return 0;
    const numbers = tarif.replace(/\s/g, '').match(/\d+/);
    return numbers ? parseInt(numbers[0]) : 0;
  };

  const showMessage = (title: string, message: string, onOk?: () => void) => {
    if (Platform.OS === 'web') {
      window.alert(`${title}\n${message}`);
      if (onOk) onOk();
    } else {
      Alert.alert(title, message, onOk ? [{ text: 'OK', onPress: onOk }] : undefined);
    }
  };

  const handleSave = async () => {
    // Validate minimum tarif
    const price = extractPrice(formData.tarif_indicatif);
    if (price < 800) {
      showMessage('Tarif minimum requis', 'Le tarif indicatif doit être d\'au moins 800€. Tarif détecté: ' + (price > 0 ? price + '€' : 'non renseigné'));
      return;
    }

    setSaving(true);
    try {
      await api.updateDJProfile({
        ...formData,
        annees_experience: parseInt(formData.annees_experience) || 0,
      });
      await checkAuth();
      showMessage('Succès', 'Profil mis à jour avec succès', () => router.back());
    } catch (error: any) {
      showMessage('Erreur', error.message || 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContent}>
          <Ionicons name="lock-closed" size={64} color="#8B5CF6" />
          <Text style={styles.errorText}>Connexion requise</Text>
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

  if (!profile) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContent}>
          <Ionicons name="alert-circle" size={64} color="#EF4444" />
          <Text style={styles.errorText}>Profil DJ non trouvé</Text>
          <Button
            title="Créer un profil"
            onPress={() => router.push('/dj-register')}
            style={styles.ctaButton}
          />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView}>
          <View style={styles.header}>
            <TouchableOpacity onPress={() => router.back()}>
              <Ionicons name="arrow-back" size={24} color="#fff" />
            </TouchableOpacity>
            <Text style={styles.title}>Modifier mon profil</Text>
            <View style={{ width: 24 }} />
          </View>

          <View style={styles.form}>
            <Text style={styles.sectionTitle}>Photos</Text>

            <ImageUpload
              image={formData.photo_profil}
              onImageChange={(image) => setFormData({ ...formData, photo_profil: image || '' })}
              label="Photo de profil"
              size={150}
              circular={true}
            />

            <GalleryUpload
              images={formData.galerie_photos}
              onImagesChange={(images) => setFormData({ ...formData, galerie_photos: images })}
              maxImages={4}
              label="Galerie photos (4 max)"
            />

            <Text style={styles.sectionTitle}>Profil professionnel</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Description</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={formData.description}
                onChangeText={(text) => setFormData({ ...formData, description: text })}
                placeholder="Présentez-vous et décrivez votre style..."
                placeholderTextColor="#666"
                multiline
                numberOfLines={4}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Années d'expérience</Text>
              <TextInput
                style={styles.input}
                value={formData.annees_experience}
                onChangeText={(text) => setFormData({ ...formData, annees_experience: text })}
                placeholder="5"
                placeholderTextColor="#666"
                keyboardType="numeric"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Types d'événements</Text>
              <View style={styles.eventTypesGrid}>
                {eventTypes.map((type) => (
                  <TouchableOpacity
                    key={type.id}
                    style={[
                      styles.eventTypeChip,
                      formData.types_evenements.includes(type.id) && styles.eventTypeChipActive,
                    ]}
                    onPress={() => toggleEventType(type.id)}
                  >
                    <Text
                      style={[
                        styles.eventTypeText,
                        formData.types_evenements.includes(type.id) && styles.eventTypeTextActive,
                      ]}
                    >
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Matériel son</Text>
              <TextInput
                style={styles.input}
                value={formData.materiel_son}
                onChangeText={(text) => setFormData({ ...formData, materiel_son: text })}
                placeholder="Pioneer, JBL..."
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Matériel lumière</Text>
              <TextInput
                style={styles.input}
                value={formData.materiel_lumiere}
                onChangeText={(text) => setFormData({ ...formData, materiel_lumiere: text })}
                placeholder="Laser, LED, machine à fumée..."
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Tarif indicatif * (minimum 800€)</Text>
              <TextInput
                style={styles.input}
                value={formData.tarif_indicatif}
                onChangeText={(text) => setFormData({ ...formData, tarif_indicatif: text })}
                placeholder="À partir de 800€"
                placeholderTextColor="#666"
              />
              <Text style={styles.hint}>Indiquez votre tarif de base (ex: "800€", "À partir de 1000€")</Text>
            </View>

            <Text style={styles.sectionTitle}>Réseaux sociaux</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Instagram</Text>
              <TextInput
                style={styles.input}
                value={formData.instagram}
                onChangeText={(text) => setFormData({ ...formData, instagram: text })}
                placeholder="@votre_compte"
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>TikTok</Text>
              <TextInput
                style={styles.input}
                value={formData.tiktok}
                onChangeText={(text) => setFormData({ ...formData, tiktok: text })}
                placeholder="@votre_compte"
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>YouTube</Text>
              <TextInput
                style={styles.input}
                value={formData.youtube}
                onChangeText={(text) => setFormData({ ...formData, youtube: text })}
                placeholder="URL ou nom de chaîne"
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
            </View>

            <Text style={styles.sectionTitle}>Présence en ligne</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Page Google (Google My Business)</Text>
              <TextInput
                style={styles.input}
                value={formData.google_page}
                onChangeText={(text) => setFormData({ ...formData, google_page: text })}
                placeholder="https://g.page/votre-page ou lien Google Maps"
                placeholderTextColor="#666"
                autoCapitalize="none"
                keyboardType="url"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Site Internet</Text>
              <TextInput
                style={styles.input}
                value={formData.site_internet}
                onChangeText={(text) => setFormData({ ...formData, site_internet: text })}
                placeholder="https://www.votre-site.fr"
                placeholderTextColor="#666"
                autoCapitalize="none"
                keyboardType="url"
              />
            </View>

            <Button
              title="Enregistrer les modifications"
              onPress={handleSave}
              loading={saving}
              style={styles.saveButton}
            />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  form: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 20,
    marginTop: 16,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#12123A',
    borderRadius: 12,
    padding: 16,
    color: '#fff',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  textArea: {
    height: 100,
    paddingTop: 16,
  },
  hint: {
    color: '#666',
    fontSize: 12,
    marginTop: 4,
  },
  eventTypesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  eventTypeChip: {
    backgroundColor: '#12123A',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  eventTypeChipActive: {
    backgroundColor: '#8B5CF6',
    borderColor: '#8B5CF6',
  },
  eventTypeText: {
    color: '#888',
    fontSize: 14,
  },
  eventTypeTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  saveButton: {
    marginTop: 16,
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  errorText: {
    color: '#fff',
    fontSize: 18,
    marginTop: 16,
    textAlign: 'center',
  },
  ctaButton: {
    marginTop: 24,
    width: '100%',
  },
});
