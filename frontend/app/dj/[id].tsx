import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Linking,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../src/services/api';
import { Button } from '../../src/components/Button';
import { DJProfile, Review } from '../../src/types';

const { width } = Dimensions.get('window');

export default function DJProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [dj, setDJ] = useState<DJProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDJ = async () => {
      if (!id) return;
      try {
        const profile = await api.getDJProfile(id);
        setDJ(profile);
      } catch (err: any) {
        setError(err.message || 'Erreur lors du chargement');
      } finally {
        setLoading(false);
      }
    };

    loadDJ();
  }, [id]);

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      if (i <= Math.floor(rating)) {
        stars.push(<Ionicons key={i} name="star" size={18} color="#FFD700" />);
      } else if (i === Math.ceil(rating) && rating % 1 >= 0.5) {
        stars.push(<Ionicons key={i} name="star-half" size={18} color="#FFD700" />);
      } else {
        stars.push(<Ionicons key={i} name="star-outline" size={18} color="#FFD700" />);
      }
    }
    return stars;
  };

  const openSocialLink = (url: string, platform: string) => {
    let fullUrl = url;
    if (!url.startsWith('http')) {
      switch (platform) {
        case 'instagram':
          fullUrl = `https://instagram.com/${url}`;
          break;
        case 'tiktok':
          fullUrl = `https://tiktok.com/@${url}`;
          break;
        case 'youtube':
          fullUrl = `https://youtube.com/${url}`;
          break;
      }
    }
    Linking.openURL(fullUrl);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#8B5CF6" style={styles.loader} />
      </SafeAreaView>
    );
  }

  if (error || !dj) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={64} color="#EF4444" />
          <Text style={styles.errorText}>{error || 'DJ non trouvé'}</Text>
          <Button title="Retour" onPress={() => router.back()} style={styles.backButton} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        {/* Hero Image */}
        <View style={styles.heroSection}>
          {dj.photo_profil ? (
            <Image source={{ uri: dj.photo_profil }} style={styles.heroImage} />
          ) : (
            <View style={styles.placeholderHero}>
              <Ionicons name="person" size={80} color="#666" />
            </View>
          )}
          <View style={styles.heroOverlay}>
            <TouchableOpacity style={styles.backIcon} onPress={() => router.back()}>
              <Ionicons name="arrow-back" size={24} color="#fff" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Profile Info */}
        <View style={styles.profileSection}>
          <View style={styles.profileHeader}>
            <View style={styles.nameRow}>
              <Text style={styles.stageName}>{dj.nom_de_scene}</Text>
              {dj.badge_verifie && (
                <View style={styles.verifiedBadge}>
                  <Ionicons name="checkmark-circle" size={16} color="#fff" />
                  <Text style={styles.verifiedText}>Vérifié</Text>
                </View>
              )}
            </View>
            <Text style={styles.realName}>{dj.prenom} {dj.nom}</Text>
          </View>

          {/* Rating & Location */}
          <View style={styles.infoRow}>
            <View style={styles.ratingContainer}>
              <View style={styles.stars}>{renderStars(dj.note_moyenne)}</View>
              <Text style={styles.ratingText}>
                {dj.note_moyenne.toFixed(1)} ({dj.nombre_avis} avis)
              </Text>
            </View>
            <View style={styles.locationContainer}>
              <Ionicons name="location" size={18} color="#8B5CF6" />
              <Text style={styles.locationText}>{dj.ville}</Text>
            </View>
          </View>

          {/* Pricing */}
          {dj.tarif_indicatif && (
            <View style={styles.pricingSection}>
              <Ionicons name="pricetag" size={20} color="#10B981" />
              <Text style={styles.pricingText}>{dj.tarif_indicatif}</Text>
            </View>
          )}

          {/* CTA Buttons */}
          <View style={styles.ctaSection}>
            <Button
              title="Contacter ce DJ"
              onPress={() => router.push(`/contact/${dj.user_id}`)}
              style={styles.contactButton}
            />
            {dj.telephone && (
              <TouchableOpacity
                style={styles.callButton}
                onPress={() => Linking.openURL(`tel:${dj.telephone}`)}
              >
                <Ionicons name="call" size={24} color="#10B981" />
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Description */}
        {dj.description && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>À propos</Text>
            <Text style={styles.description}>{dj.description}</Text>
          </View>
        )}

        {/* Details */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Détails</Text>
          
          <View style={styles.detailItem}>
            <Ionicons name="time" size={20} color="#8B5CF6" />
            <Text style={styles.detailLabel}>Expérience:</Text>
            <Text style={styles.detailValue}>{dj.annees_experience} ans</Text>
          </View>

          {dj.zone_intervention && dj.zone_intervention.length > 0 && (
            <View style={styles.detailItem}>
              <Ionicons name="map" size={20} color="#8B5CF6" />
              <Text style={styles.detailLabel}>Zone:</Text>
              <Text style={styles.detailValue}>{dj.zone_intervention.join(', ')}</Text>
            </View>
          )}

          {dj.company_name && (
            <View style={styles.detailItem}>
              <Ionicons name="business" size={20} color="#8B5CF6" />
              <Text style={styles.detailLabel}>Entreprise:</Text>
              <Text style={styles.detailValue}>{dj.company_name}</Text>
            </View>
          )}
        </View>

        {/* Event Types */}
        {dj.types_evenements && dj.types_evenements.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Types d'événements</Text>
            <View style={styles.tagsContainer}>
              {dj.types_evenements.map((type, index) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>{type}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Equipment */}
        {(dj.materiel_son || dj.materiel_lumiere) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Matériel</Text>
            {dj.materiel_son && (
              <View style={styles.equipmentItem}>
                <Ionicons name="volume-high" size={20} color="#F59E0B" />
                <Text style={styles.equipmentText}>{dj.materiel_son}</Text>
              </View>
            )}
            {dj.materiel_lumiere && (
              <View style={styles.equipmentItem}>
                <Ionicons name="flashlight" size={20} color="#F59E0B" />
                <Text style={styles.equipmentText}>{dj.materiel_lumiere}</Text>
              </View>
            )}
            {dj.options_supplementaires && (
              <View style={styles.equipmentItem}>
                <Ionicons name="add-circle" size={20} color="#F59E0B" />
                <Text style={styles.equipmentText}>{dj.options_supplementaires}</Text>
              </View>
            )}
          </View>
        )}

        {/* Social Links */}
        {(dj.instagram || dj.tiktok || dj.youtube) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Réseaux sociaux</Text>
            <View style={styles.socialLinks}>
              {dj.instagram && (
                <TouchableOpacity
                  style={styles.socialButton}
                  onPress={() => openSocialLink(dj.instagram, 'instagram')}
                >
                  <Ionicons name="logo-instagram" size={28} color="#E4405F" />
                </TouchableOpacity>
              )}
              {dj.tiktok && (
                <TouchableOpacity
                  style={styles.socialButton}
                  onPress={() => openSocialLink(dj.tiktok, 'tiktok')}
                >
                  <Ionicons name="logo-tiktok" size={28} color="#fff" />
                </TouchableOpacity>
              )}
              {dj.youtube && (
                <TouchableOpacity
                  style={styles.socialButton}
                  onPress={() => openSocialLink(dj.youtube, 'youtube')}
                >
                  <Ionicons name="logo-youtube" size={28} color="#FF0000" />
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}

        {/* Reviews */}
        {dj.reviews && dj.reviews.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Avis clients</Text>
            {dj.reviews.map((review: Review) => (
              <View key={review.review_id} style={styles.reviewCard}>
                <View style={styles.reviewHeader}>
                  <Text style={styles.reviewAuthor}>{review.client_nom}</Text>
                  <View style={styles.reviewStars}>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Ionicons
                        key={star}
                        name={star <= review.note ? 'star' : 'star-outline'}
                        size={14}
                        color="#FFD700"
                      />
                    ))}
                  </View>
                </View>
                {review.type_evenement && (
                  <Text style={styles.reviewEventType}>{review.type_evenement}</Text>
                )}
                <Text style={styles.reviewText}>{review.commentaire}</Text>
              </View>
            ))}
          </View>
        )}

        <View style={styles.footer} />
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
  errorContainer: {
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
  backButton: {
    marginTop: 24,
  },
  heroSection: {
    height: 300,
    position: 'relative',
  },
  heroImage: {
    width: '100%',
    height: '100%',
  },
  placeholderHero: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  heroOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    padding: 16,
  },
  backIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileSection: {
    padding: 20,
    marginTop: -40,
    backgroundColor: '#0c0c0c',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  profileHeader: {
    marginBottom: 16,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stageName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginRight: 12,
  },
  verifiedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  verifiedText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  realName: {
    fontSize: 16,
    color: '#888',
    marginTop: 4,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stars: {
    flexDirection: 'row',
    marginRight: 8,
  },
  ratingText: {
    color: '#888',
    fontSize: 14,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  locationText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 4,
  },
  pricingSection: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  pricingText: {
    color: '#10B981',
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
  ctaSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  contactButton: {
    flex: 1,
  },
  callButton: {
    width: 52,
    height: 52,
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12,
    borderWidth: 1,
    borderColor: '#10B981',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  description: {
    color: '#ccc',
    fontSize: 16,
    lineHeight: 24,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  detailLabel: {
    color: '#888',
    fontSize: 14,
    marginLeft: 8,
    marginRight: 4,
  },
  detailValue: {
    color: '#fff',
    fontSize: 14,
    flex: 1,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: '#8B5CF6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  tagText: {
    color: '#fff',
    fontSize: 14,
  },
  equipmentItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 12,
  },
  equipmentText: {
    color: '#ccc',
    fontSize: 14,
    marginLeft: 12,
    flex: 1,
  },
  socialLinks: {
    flexDirection: 'row',
  },
  socialButton: {
    width: 56,
    height: 56,
    backgroundColor: '#1a1a1a',
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  reviewCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  reviewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  reviewAuthor: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  reviewStars: {
    flexDirection: 'row',
  },
  reviewEventType: {
    color: '#8B5CF6',
    fontSize: 12,
    marginBottom: 8,
  },
  reviewText: {
    color: '#ccc',
    fontSize: 14,
    lineHeight: 20,
  },
  footer: {
    height: 40,
  },
});
