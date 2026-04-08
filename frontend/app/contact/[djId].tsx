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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../src/services/api';
import { Button } from '../../src/components/Button';
import { DJProfile, EventType } from '../../src/types';

export default function ContactDJScreen() {
  const { djId } = useLocalSearchParams<{ djId: string }>();
  const router = useRouter();
  const [dj, setDJ] = useState<DJProfile | null>(null);
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    client_nom: '',
    client_email: '',
    client_telephone: '',
    date_evenement: '',
    lieu_evenement: '',
    type_evenement: '',
    message: '',
  });

  useEffect(() => {
    const loadData = async () => {
      if (!djId) return;
      try {
        const [profile, types] = await Promise.all([
          api.getDJProfile(djId),
          api.getEventTypes(),
        ]);
        setDJ(profile);
        setEventTypes(types);
      } catch (error) {
        console.error('Error loading DJ:', error);
      }
    };
    loadData();
  }, [djId]);

  const handleSubmit = async () => {
    // Validation
    if (!formData.client_nom || !formData.client_email || !formData.date_evenement || !formData.message) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    try {
      await api.sendContactRequest({
        dj_user_id: djId!,
        ...formData,
      });
      Alert.alert(
        'Demande envoyée',
        'Votre demande a été envoyée au DJ. Vous recevrez une réponse rapidement.',
        [{ text: 'OK', onPress: () => router.back() }]
      );
    } catch (error: any) {
      Alert.alert('Erreur', error.message || 'Erreur lors de l\'envoi de la demande');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView style={styles.scrollView}>
          {dj && (
            <View style={styles.djPreview}>
              <View style={styles.djInfo}>
                <Ionicons name="person-circle" size={48} color="#8B5CF6" />
                <View style={styles.djDetails}>
                  <Text style={styles.djName}>{dj.nom_de_scene}</Text>
                  <Text style={styles.djLocation}>{dj.ville}</Text>
                </View>
              </View>
            </View>
          )}

          <View style={styles.form}>
            <Text style={styles.formTitle}>Demande de contact</Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Votre nom *</Text>
              <TextInput
                style={styles.input}
                value={formData.client_nom}
                onChangeText={(text) => setFormData({ ...formData, client_nom: text })}
                placeholder="Entrez votre nom"
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Votre email *</Text>
              <TextInput
                style={styles.input}
                value={formData.client_email}
                onChangeText={(text) => setFormData({ ...formData, client_email: text })}
                placeholder="votre@email.com"
                placeholderTextColor="#666"
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Votre téléphone</Text>
              <TextInput
                style={styles.input}
                value={formData.client_telephone}
                onChangeText={(text) => setFormData({ ...formData, client_telephone: text })}
                placeholder="06 XX XX XX XX"
                placeholderTextColor="#666"
                keyboardType="phone-pad"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Date de l'événement *</Text>
              <TextInput
                style={styles.input}
                value={formData.date_evenement}
                onChangeText={(text) => setFormData({ ...formData, date_evenement: text })}
                placeholder="JJ/MM/AAAA"
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Lieu de l'événement</Text>
              <TextInput
                style={styles.input}
                value={formData.lieu_evenement}
                onChangeText={(text) => setFormData({ ...formData, lieu_evenement: text })}
                placeholder="Ville, adresse..."
                placeholderTextColor="#666"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Type d'événement</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.eventTypeScroll}>
                {eventTypes.map((type) => (
                  <TouchableOpacity
                    key={type.id}
                    style={[
                      styles.eventTypeChip,
                      formData.type_evenement === type.id && styles.eventTypeChipActive,
                    ]}
                    onPress={() => setFormData({ ...formData, type_evenement: type.id })}
                  >
                    <Text
                      style={[
                        styles.eventTypeText,
                        formData.type_evenement === type.id && styles.eventTypeTextActive,
                      ]}
                    >
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Votre message *</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={formData.message}
                onChangeText={(text) => setFormData({ ...formData, message: text })}
                placeholder="Décrivez votre événement, vos attentes..."
                placeholderTextColor="#666"
                multiline
                numberOfLines={5}
                textAlignVertical="top"
              />
            </View>

            <Button
              title="Envoyer la demande"
              onPress={handleSubmit}
              loading={loading}
              style={styles.submitButton}
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
    backgroundColor: '#0c0c0c',
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  djPreview: {
    backgroundColor: '#1a1a1a',
    padding: 16,
    marginHorizontal: 20,
    marginTop: 16,
    borderRadius: 12,
  },
  djInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  djDetails: {
    marginLeft: 12,
  },
  djName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  djLocation: {
    color: '#888',
    fontSize: 14,
    marginTop: 2,
  },
  form: {
    padding: 20,
  },
  formTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 24,
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
    height: 120,
    paddingTop: 16,
  },
  eventTypeScroll: {
    marginTop: 8,
  },
  eventTypeChip: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 8,
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
  submitButton: {
    marginTop: 8,
  },
});
