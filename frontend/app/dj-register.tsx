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
import { EventType } from '../src/types';

export default function DJRegisterScreen() {
  const router = useRouter();
  const { user, isAuthenticated, checkAuth } = useAuthStore();
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [loading, setLoading] = useState(false);
  const [siretVerifying, setSiretVerifying] = useState(false);
  const [siretResult, setSiretResult] = useState<any>(null);
  const [step, setStep] = useState(1);
  const [geoInfo, setGeoInfo] = useState<{
    department_name?: string;
    region_name?: string;
    department_code?: string;
    region_code?: string;
  } | null>(null);
  const [geoLoading, setGeoLoading] = useState(false);

  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    nom_de_scene: '',
    telephone: '',
    ville: '',
    zone_intervention: '',
    siret: '',
    description: '',
    annees_experience: '',
    types_evenements: [] as string[],
    materiel_son: '',
    materiel_lumiere: '',
    tarif_indicatif: '',
    instagram: '',
    tiktok: '',
    youtube: '',
    photo_profil: '',
    galerie_photos: [] as string[],
  });

  useEffect(() => {
    const loadEventTypes = async () => {
      try {
        const types = await api.getEventTypes();
        setEventTypes(types);
      } catch (error) {
        console.error('Error loading event types:', error);
      }
    };
    loadEventTypes();
  }, []);

  // Auto-lookup city for geo info
  useEffect(() => {
    const lookupTimeout = setTimeout(async () => {
      const city = formData.ville.trim();
      if (city.length >= 3) {
        setGeoLoading(true);
        try {
          const result = await api.lookupCity(city);
          if ('department_name' in result) {
            setGeoInfo({
              department_name: result.department_name,
              region_name: result.region_name,
              department_code: result.department_code,
              region_code: result.region_code,
            });
          } else {
            setGeoInfo(null);
          }
        } catch {
          setGeoInfo(null);
        } finally {
          setGeoLoading(false);
        }
      } else {
        setGeoInfo(null);
      }
    }, 500); // debounce 500ms

    return () => clearTimeout(lookupTimeout);
  }, [formData.ville]);

  const handleLogin = () => {
    const redirectUrl = typeof window !== 'undefined'
      ? `${window.location.origin}/dj-register`
      : '';
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
    
    if (typeof window !== 'undefined') {
      window.location.href = authUrl;
    }
  };

  const verifySiret = async () => {
    if (!formData.siret || formData.siret.length !== 14) {
      Alert.alert('Erreur', 'Le SIRET doit contenir 14 chiffres');
      return;
    }

    setSiretVerifying(true);
    try {
      const result = await api.verifySiret(formData.siret);
      setSiretResult(result);
      if (!result.valid) {
        Alert.alert('SIRET invalide', result.message || 'Ce numéro SIRET n\'est pas valide');
      }
    } catch (error: any) {
      Alert.alert('Erreur', 'Impossible de vérifier le SIRET');
    } finally {
      setSiretVerifying(false);
    }
  };

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

  const handleSubmit = async () => {
    if (!formData.nom || !formData.prenom || !formData.nom_de_scene || !formData.telephone || !formData.ville || !formData.siret) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (!siretResult?.valid) {
      Alert.alert('Erreur', 'Veuillez vérifier votre numéro SIRET');
      return;
    }

    // Validate minimum tarif
    const price = extractPrice(formData.tarif_indicatif);
    if (price < 800) {
      Alert.alert('Tarif minimum requis', 'Le tarif indicatif doit être d\'au moins 800€. Tarif détecté: ' + (price > 0 ? price + '€' : 'non renseigné'));
      return;
    }

    setLoading(true);
    try {
      const profileData = {
        ...formData,
        email: user?.email || '',
        zone_intervention: formData.zone_intervention.split(',').map(z => z.trim()).filter(Boolean),
        annees_experience: parseInt(formData.annees_experience) || 0,
      };

      await api.registerDJ(profileData);
      await checkAuth();
      
      Alert.alert(
        'Profil créé !',
        'Votre profil DJ a été créé avec succès. Activez votre abonnement pour être visible.',
        [{ text: 'OK', onPress: () => router.replace('/(tabs)/dashboard') }]
      );
    } catch (error: any) {
      Alert.alert('Erreur', error.message || 'Erreur lors de la création du profil');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.authRequired}>
          <Ionicons name="lock-closed" size={64} color="#8B5CF6" />
          <Text style={styles.authTitle}>Connexion requise</Text>
          <Text style={styles.authText}>
            Connectez-vous pour créer votre profil DJ professionnel
          </Text>
          <Button title="Se connecter avec Google" onPress={handleLogin} style={styles.loginButton} />
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
            <Text style={styles.title}>Devenir DJ</Text>
            <Text style={styles.subtitle}>Étape {step}/3</Text>
          </View>

          <View style={styles.progress}>
            <View style={[styles.progressBar, { width: step === 1 ? '33%' : step === 2 ? '66%' : '100%' }]} />
          </View>

          {step === 1 ? (
            <View style={styles.form}>
              <Text style={styles.sectionTitle}>Informations personnelles</Text>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Prénom *</Text>
                <TextInput
                  style={styles.input}
                  value={formData.prenom}
                  onChangeText={(text) => setFormData({ ...formData, prenom: text })}
                  placeholder="Votre prénom"
                  placeholderTextColor="#666"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Nom *</Text>
                <TextInput
                  style={styles.input}
                  value={formData.nom}
                  onChangeText={(text) => setFormData({ ...formData, nom: text })}
                  placeholder="Votre nom"
                  placeholderTextColor="#666"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Nom de scène *</Text>
                <TextInput
                  style={styles.input}
                  value={formData.nom_de_scene}
                  onChangeText={(text) => setFormData({ ...formData, nom_de_scene: text })}
                  placeholder="DJ..."
                  placeholderTextColor="#666"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Téléphone *</Text>
                <TextInput
                  style={styles.input}
                  value={formData.telephone}
                  onChangeText={(text) => setFormData({ ...formData, telephone: text })}
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
                  onChangeText={(text) => setFormData({ ...formData, ville: text })}
                  placeholder="Votre ville (ex: Paris, Lyon, Marseille...)"
                  placeholderTextColor="#666"
                />
                {geoLoading && (
                  <View style={styles.geoLoading}>
                    <ActivityIndicator size="small" color="#8B5CF6" />
                    <Text style={styles.geoLoadingText}>Recherche...</Text>
                  </View>
                )}
                {geoInfo && (
                  <View style={styles.geoInfoContainer}>
                    <Ionicons name="location" size={16} color="#10B981" />
                    <Text style={styles.geoInfoText}>
                      {geoInfo.department_name} — {geoInfo.region_name}
                    </Text>
                  </View>
                )}
                {formData.ville.length >= 3 && !geoLoading && !geoInfo && (
                  <Text style={styles.geoNotFound}>
                    Ville non reconnue — la géolocalisation sera ajoutée manuellement
                  </Text>
                )}
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Zone d'intervention</Text>
                <TextInput
                  style={styles.input}
                  value={formData.zone_intervention}
                  onChangeText={(text) => setFormData({ ...formData, zone_intervention: text })}
                  placeholder="Paris, Ile-de-France, Lyon..."
                  placeholderTextColor="#666"
                />
                <Text style={styles.hint}>Séparez par des virgules</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Numéro SIRET * (obligatoire)</Text>
                <View style={styles.siretRow}>
                  <TextInput
                    style={[styles.input, styles.siretInput]}
                    value={formData.siret}
                    onChangeText={(text) => {
                      setFormData({ ...formData, siret: text.replace(/\D/g, '').slice(0, 14) });
                      setSiretResult(null);
                    }}
                    placeholder="14 chiffres"
                    placeholderTextColor="#666"
                    keyboardType="numeric"
                    maxLength={14}
                  />
                  <TouchableOpacity
                    style={styles.verifyButton}
                    onPress={verifySiret}
                    disabled={siretVerifying || formData.siret.length !== 14}
                  >
                    {siretVerifying ? (
                      <ActivityIndicator color="#fff" size="small" />
                    ) : (
                      <Text style={styles.verifyButtonText}>Vérifier</Text>
                    )}
                  </TouchableOpacity>
                </View>
                {siretResult && (
                  <View style={[
                    styles.siretStatus,
                    siretResult.valid ? styles.siretValid : styles.siretInvalid,
                  ]}>
                    <Ionicons
                      name={siretResult.valid ? 'checkmark-circle' : 'close-circle'}
                      size={20}
                      color={siretResult.valid ? '#10B981' : '#EF4444'}
                    />
                    <Text style={[
                      styles.siretStatusText,
                      siretResult.valid ? styles.siretValidText : styles.siretInvalidText,
                    ]}>
                      {siretResult.valid ? siretResult.company_name : siretResult.message}
                    </Text>
                  </View>
                )}
              </View>

              <Button
                title="Suivant"
                onPress={() => {
                  if (!formData.nom || !formData.prenom || !formData.nom_de_scene || !formData.telephone || !formData.ville || !formData.siret) {
                    Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
                    return;
                  }
                  if (!siretResult?.valid) {
                    Alert.alert('Erreur', 'Veuillez vérifier votre SIRET');
                    return;
                  }
                  setStep(2);
                }}
                style={styles.nextButton}
              />
            </View>
          ) : step === 2 ? (
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

              <View style={styles.buttonRow}>
                <Button
                  title="Retour"
                  onPress={() => setStep(1)}
                  variant="outline"
                  style={styles.backButton}
                />
                <Button
                  title="Suivant"
                  onPress={() => setStep(3)}
                  style={styles.submitButton}
                />
              </View>
            </View>
          ) : (
            <View style={styles.form}>
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

              <View style={styles.buttonRow}>
                <Button
                  title="Retour"
                  onPress={() => setStep(2)}
                  variant="outline"
                  style={styles.backButton}
                />
                <Button
                  title="Créer mon profil"
                  onPress={handleSubmit}
                  loading={loading}
                  style={styles.submitButton}
                />
              </View>
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0c0c0c',
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#8B5CF6',
    fontWeight: '600',
  },
  progress: {
    height: 4,
    backgroundColor: '#2a2a2a',
    marginHorizontal: 20,
    borderRadius: 2,
    marginBottom: 24,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#8B5CF6',
    borderRadius: 2,
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
    marginTop: 8,
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
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    color: '#fff',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#2a2a2a',
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
  siretRow: {
    flexDirection: 'row',
  },
  siretInput: {
    flex: 1,
    marginRight: 12,
  },
  verifyButton: {
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 20,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  verifyButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  siretStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  siretValid: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  siretInvalid: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
  },
  siretStatusText: {
    marginLeft: 8,
    fontSize: 14,
    flex: 1,
  },
  siretValidText: {
    color: '#10B981',
  },
  siretInvalidText: {
    color: '#EF4444',
  },
  eventTypesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  eventTypeChip: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#2a2a2a',
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
  nextButton: {
    marginTop: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 8,
  },
  backButton: {
    flex: 1,
    marginRight: 12,
  },
  submitButton: {
    flex: 1,
  },
  authRequired: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  authTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 24,
  },
  authText: {
    fontSize: 16,
    color: '#888',
    textAlign: 'center',
    marginTop: 12,
  },
  loginButton: {
    marginTop: 32,
    width: '100%',
  },
  geoLoading: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
    paddingHorizontal: 4,
  },
  geoLoadingText: {
    color: '#888',
    fontSize: 12,
    marginLeft: 6,
  },
  geoInfoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    padding: 10,
    borderRadius: 8,
    marginTop: 6,
  },
  geoInfoText: {
    color: '#10B981',
    fontSize: 13,
    marginLeft: 8,
    fontWeight: '600',
  },
  geoNotFound: {
    color: '#F59E0B',
    fontSize: 12,
    marginTop: 6,
    paddingHorizontal: 4,
  },
});
