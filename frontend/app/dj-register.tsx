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
  Linking,
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
  const [authMode, setAuthMode] = useState<'choice' | 'email-register' | 'email-login'>('choice');
  const [emailForm, setEmailForm] = useState({ email: '', password: '', name: '', confirmPassword: '' });
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');
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
    code_postal: '',
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
    google_page: '',
    site_internet: '',
    photo_profil: '',
    galerie_photos: [] as string[],
    assurance_rc_numero: '',
    assurance_rc_organisme: '',
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

  // Auto-lookup geo info when postal code changes (primary)
  useEffect(() => {
    const cp = formData.code_postal.trim();
    if (cp.length !== 5 || !/^\d{5}$/.test(cp)) {
      return;
    }
    const lookupTimeout = setTimeout(async () => {
      setGeoLoading(true);
      try {
        const response = await fetch(`https://geo.api.gouv.fr/communes?codePostal=${cp}&fields=nom,codeDepartement,codeRegion&limit=5`);
        const data = await response.json();
        if (data && data.length > 0) {
          const commune = data[0];
          setFormData(prev => ({ ...prev, ville: commune.nom || prev.ville }));
          const result = await api.lookupCity(commune.nom);
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
        } else {
          setGeoInfo(null);
        }
      } catch {
        setGeoInfo(null);
      } finally {
        setGeoLoading(false);
      }
    }, 400);
    return () => clearTimeout(lookupTimeout);
  }, [formData.code_postal]);

  // Fallback: lookup by city name if no postal code
  useEffect(() => {
    if (formData.code_postal.trim().length === 5) return; // Postal code takes priority
    const city = formData.ville.trim();
    if (city.length < 3) { setGeoInfo(null); return; }
    const lookupTimeout = setTimeout(async () => {
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
    }, 500);
    return () => clearTimeout(lookupTimeout);
  }, [formData.ville]);

  const handleLogin = () => {
    const redirectUrl = typeof window !== 'undefined'
      ? `${window.location.origin}/auth/callback`
      : '';
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
    
    if (typeof window !== 'undefined') {
      window.location.href = authUrl;
    }
  };

  const handleEmailRegister = async () => {
    setAuthError('');
    if (!emailForm.name.trim()) { setAuthError('Le nom est requis'); return; }
    if (!emailForm.email.trim()) { setAuthError("L'email est requis"); return; }
    if (emailForm.password.length < 6) { setAuthError('Mot de passe : 6 caractères minimum'); return; }
    if (emailForm.password !== emailForm.confirmPassword) { setAuthError('Les mots de passe ne correspondent pas'); return; }
    
    setAuthLoading(true);
    try {
      await api.registerEmail(emailForm.email.trim(), emailForm.password, emailForm.name.trim());
      await checkAuth();
    } catch (error: any) {
      setAuthError(error.message || "Erreur lors de l'inscription");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleEmailLogin = async () => {
    setAuthError('');
    if (!emailForm.email.trim() || !emailForm.password) { setAuthError('Email et mot de passe requis'); return; }
    
    setAuthLoading(true);
    try {
      await api.loginEmail(emailForm.email.trim(), emailForm.password);
      await checkAuth();
    } catch (error: any) {
      setAuthError(error.message || 'Email ou mot de passe incorrect');
    } finally {
      setAuthLoading(false);
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
    if (!formData.nom || !formData.prenom || !formData.nom_de_scene || !formData.telephone || !formData.code_postal || !formData.siret) {
      if (Platform.OS === 'web') {
        window.alert('Veuillez remplir tous les champs obligatoires');
      } else {
        Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
      }
      return;
    }

    if (formData.code_postal.length !== 5 || !/^\d{5}$/.test(formData.code_postal)) {
      const msg = 'Veuillez entrer un code postal valide à 5 chiffres';
      if (Platform.OS === 'web') {
        window.alert(msg);
      } else {
        Alert.alert('Code postal invalide', msg);
      }
      return;
    }

    if (!siretResult?.valid) {
      if (Platform.OS === 'web') {
        window.alert('Veuillez vérifier votre numéro SIRET');
      } else {
        Alert.alert('Erreur', 'Veuillez vérifier votre numéro SIRET');
      }
      return;
    }

    // Validate minimum tarif
    const price = extractPrice(formData.tarif_indicatif);
    if (price < 800) {
      const msg = 'Le tarif indicatif doit être d\'au moins 800€. Tarif détecté: ' + (price > 0 ? price + '€' : 'non renseigné');
      if (Platform.OS === 'web') {
        window.alert(msg);
      } else {
        Alert.alert('Tarif minimum requis', msg);
      }
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
      
      // Free trial: redirect directly to dashboard (no Stripe payment needed)
      router.replace('/(tabs)/dashboard');
    } catch (error: any) {
      if (Platform.OS === 'web') {
        window.alert(error.message || 'Erreur lors de la création du profil');
      } else {
        Alert.alert('Erreur', error.message || 'Erreur lors de la création du profil');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView contentContainerStyle={styles.authContainer}>
            <TouchableOpacity onPress={() => router.back()} style={styles.authBack}>
              <Ionicons name="arrow-back" size={24} color="#fff" />
            </TouchableOpacity>

            <Ionicons name="musical-notes" size={64} color="#8B5CF6" />
            <Text style={styles.authTitle}>Devenir DJ</Text>
            <Text style={styles.authText}>
              Créez votre compte pour rejoindre le réseau DJ Match
            </Text>

            {(authMode === 'choice' || authMode === 'email-register') && (
              <View style={styles.authForm}>
                <TextInput
                  style={styles.authInput}
                  placeholder="Votre nom complet"
                  placeholderTextColor="#666"
                  value={emailForm.name}
                  onChangeText={(t) => setEmailForm(f => ({ ...f, name: t }))}
                  autoCapitalize="words"
                />
                <TextInput
                  style={styles.authInput}
                  placeholder="Votre email"
                  placeholderTextColor="#666"
                  value={emailForm.email}
                  onChangeText={(t) => setEmailForm(f => ({ ...f, email: t }))}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
                <TextInput
                  style={styles.authInput}
                  placeholder="Mot de passe (6 car. min)"
                  placeholderTextColor="#666"
                  value={emailForm.password}
                  onChangeText={(t) => setEmailForm(f => ({ ...f, password: t }))}
                  secureTextEntry
                />
                <TextInput
                  style={styles.authInput}
                  placeholder="Confirmer le mot de passe"
                  placeholderTextColor="#666"
                  value={emailForm.confirmPassword}
                  onChangeText={(t) => setEmailForm(f => ({ ...f, confirmPassword: t }))}
                  secureTextEntry
                />

                {authError ? <Text style={styles.authErrorText}>{authError}</Text> : null}

                <TouchableOpacity
                  style={[styles.submitButton, authLoading && styles.submitButtonDisabled]}
                  onPress={handleEmailRegister}
                  disabled={authLoading}
                >
                  {authLoading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.submitButtonText}>Créer mon compte</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity onPress={() => { setAuthMode('email-login'); setAuthError(''); }}>
                  <Text style={styles.switchText}>Déjà un compte ? Se connecter</Text>
                </TouchableOpacity>

                <View style={styles.divider}>
                  <View style={styles.dividerLine} />
                  <Text style={styles.dividerText}>ou</Text>
                  <View style={styles.dividerLine} />
                </View>

                <TouchableOpacity style={styles.googleButton} onPress={handleLogin}>
                  <Ionicons name="logo-google" size={20} color="#fff" />
                  <Text style={styles.googleButtonText}>Continuer avec Google</Text>
                </TouchableOpacity>
              </View>
            )}

            {authMode === 'email-login' && (
              <View style={styles.authForm}>
                <TextInput
                  style={styles.authInput}
                  placeholder="Votre email"
                  placeholderTextColor="#666"
                  value={emailForm.email}
                  onChangeText={(t) => setEmailForm(f => ({ ...f, email: t }))}
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
                <TextInput
                  style={styles.authInput}
                  placeholder="Mot de passe"
                  placeholderTextColor="#666"
                  value={emailForm.password}
                  onChangeText={(t) => setEmailForm(f => ({ ...f, password: t }))}
                  secureTextEntry
                />

                {authError ? <Text style={styles.authErrorText}>{authError}</Text> : null}

                <TouchableOpacity
                  style={[styles.submitButton, authLoading && styles.submitButtonDisabled]}
                  onPress={handleEmailLogin}
                  disabled={authLoading}
                >
                  {authLoading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.submitButtonText}>Se connecter</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity onPress={() => { setAuthMode('email-register'); setAuthError(''); }}>
                  <Text style={styles.switchText}>Pas de compte ? S'inscrire</Text>
                </TouchableOpacity>

                <TouchableOpacity onPress={() => setAuthMode('choice')}>
                  <Text style={styles.switchTextSecondary}>Retour aux options</Text>
                </TouchableOpacity>
              </View>
            )}
          </ScrollView>
        </KeyboardAvoidingView>
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
                <Text style={styles.label}>Code postal *</Text>
                <TextInput
                  style={styles.input}
                  value={formData.code_postal}
                  onChangeText={(text) => {
                    const cleaned = text.replace(/\D/g, '').slice(0, 5);
                    setFormData({ ...formData, code_postal: cleaned });
                  }}
                  placeholder="Ex: 75001, 69001, 13001..."
                  placeholderTextColor="#666"
                  keyboardType="number-pad"
                  maxLength={5}
                />
                {geoLoading && (
                  <View style={styles.geoLoading}>
                    <ActivityIndicator size="small" color="#8B5CF6" />
                    <Text style={styles.geoLoadingText}>Recherche en cours...</Text>
                  </View>
                )}
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Ville</Text>
                <TextInput
                  style={[styles.input, formData.code_postal.length === 5 && geoInfo ? styles.inputAutoFilled : null]}
                  value={formData.ville}
                  onChangeText={(text) => setFormData({ ...formData, ville: text })}
                  placeholder="Remplie automatiquement par le code postal"
                  placeholderTextColor="#666"
                />
                {geoInfo && (
                  <View style={styles.geoInfoContainer}>
                    <Ionicons name="location" size={16} color="#10B981" />
                    <Text style={styles.geoInfoText}>
                      {geoInfo.department_name} — {geoInfo.region_name}
                    </Text>
                  </View>
                )}
                {formData.code_postal.length === 5 && !geoLoading && !geoInfo && (
                  <Text style={styles.geoNotFound}>
                    Code postal non reconnu — vérifiez le code
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

              <View style={styles.sectionDivider}>
                <Text style={styles.sectionSubtitle}>Assurance RC Professionnelle (optionnel)</Text>
              </View>

              <Text style={styles.label}>Organisme assureur</Text>
              <TextInput
                style={styles.input}
                value={formData.assurance_rc_organisme}
                onChangeText={(text) => setFormData({ ...formData, assurance_rc_organisme: text })}
                placeholder="Ex: AXA, MAIF, Allianz..."
                placeholderTextColor="#666"
              />

              <Text style={styles.label}>N° de police RC Pro</Text>
              <TextInput
                style={styles.input}
                value={formData.assurance_rc_numero}
                onChangeText={(text) => setFormData({ ...formData, assurance_rc_numero: text })}
                placeholder="Numéro de votre contrat RC Pro"
                placeholderTextColor="#666"
              />

              <Button
                title="Suivant"
                onPress={() => {
                  if (!formData.nom || !formData.prenom || !formData.nom_de_scene || !formData.telephone || !formData.code_postal || !formData.siret) {
                    if (Platform.OS === 'web') {
                      window.alert('Veuillez remplir tous les champs obligatoires (dont le code postal)');
                    } else {
                      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires (dont le code postal)');
                    }
                    return;
                  }
                  if (formData.code_postal.length !== 5 || !/^\d{5}$/.test(formData.code_postal)) {
                    if (Platform.OS === 'web') {
                      window.alert('Veuillez entrer un code postal valide à 5 chiffres');
                    } else {
                      Alert.alert('Erreur', 'Veuillez entrer un code postal valide à 5 chiffres');
                    }
                    return;
                  }
                  if (!siretResult?.valid) {
                    if (Platform.OS === 'web') {
                      window.alert('Veuillez vérifier votre SIRET');
                    } else {
                      Alert.alert('Erreur', 'Veuillez vérifier votre SIRET');
                    }
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
    backgroundColor: '#1E1E4A',
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
  sectionDivider: {
    marginTop: 20,
    marginBottom: 12,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
  },
  sectionSubtitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#8B5CF6',
    marginBottom: 4,
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
  inputAutoFilled: {
    borderColor: 'rgba(16,185,129,0.4)',
    backgroundColor: 'rgba(16,185,129,0.05)',
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
  authContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 30,
  },
  authBack: {
    alignSelf: 'flex-start',
    padding: 8,
    marginBottom: 16,
  },
  authTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 16,
    marginBottom: 8,
  },
  authText: {
    fontSize: 15,
    color: '#999',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 22,
  },
  authChoices: {
    width: '100%',
    maxWidth: 340,
    alignItems: 'center',
  },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4285F4',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    width: '100%',
  },
  googleButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 10,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    marginVertical: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#1E1E4A',
  },
  dividerText: {
    color: '#666',
    marginHorizontal: 12,
    fontSize: 14,
  },
  emailButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#8B5CF6',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    width: '100%',
    marginBottom: 16,
  },
  emailButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 10,
  },
  switchText: {
    color: '#8B5CF6',
    fontSize: 14,
    marginTop: 12,
  },
  switchTextSecondary: {
    color: '#666',
    fontSize: 13,
    marginTop: 12,
  },
  authForm: {
    width: '100%',
    maxWidth: 340,
    alignItems: 'center',
  },
  authInput: {
    width: '100%',
    backgroundColor: '#12123A',
    borderRadius: 12,
    padding: 14,
    color: '#fff',
    fontSize: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  authErrorText: {
    color: '#EF4444',
    fontSize: 13,
    textAlign: 'center',
    marginBottom: 12,
  },
  submitButton: {
    backgroundColor: '#8B5CF6',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    width: '100%',
    alignItems: 'center',
    marginTop: 4,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
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
