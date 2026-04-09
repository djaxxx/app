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
  TextInput,
  Platform,
  KeyboardAvoidingView,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import { api } from '../../src/services/api';
import { resolveImageUrl } from '../../src/utils/imageUrl';
import { Button } from '../../src/components/Button';
import { DJProfile, Review } from '../../src/types';

const { width } = Dimensions.get('window');

export default function DJProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [dj, setDJ] = useState<DJProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewSuccess, setReviewSuccess] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [reviewForm, setReviewForm] = useState({
    client_nom: '',
    client_email: '',
    note: 5,
    commentaire: '',
    type_evenement: '',
    date_evenement: '',
  });

  useEffect(() => {
    const loadDJ = async () => {
      if (!id) return;
      try {
        const profile = await api.getDJProfile(id);
        setDJ(profile);
        try {
          const reviewsData = await api.getDJReviews(id);
          setReviews(reviewsData);
        } catch {}
      } catch (err: any) {
        setError(err.message || 'Erreur lors du chargement');
      } finally {
        setLoading(false);
      }
    };

    loadDJ();
  }, [id]);

  const handleSubmitReview = async () => {
    if (!reviewForm.client_nom.trim()) {
      if (Platform.OS === 'web') window.alert('Veuillez entrer votre nom');
      return;
    }
    if (!reviewForm.client_email.trim() || !reviewForm.client_email.includes('@')) {
      if (Platform.OS === 'web') window.alert('Veuillez entrer un email valide');
      return;
    }
    if (!reviewForm.commentaire.trim()) {
      if (Platform.OS === 'web') window.alert('Veuillez écrire un commentaire');
      return;
    }
    setSubmittingReview(true);
    try {
      await api.submitReview({ dj_user_id: id!, ...reviewForm });
      setReviewSuccess(true);
      setShowReviewForm(false);
      setReviewForm({ client_nom: '', client_email: '', note: 5, commentaire: '', type_evenement: '', date_evenement: '' });
    } catch (err: any) {
      if (Platform.OS === 'web') window.alert(err.message || 'Erreur');
    } finally {
      setSubmittingReview(false);
    }
  };

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

  const openSocialLink = async (url: string, platform: string) => {
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
    await WebBrowser.openBrowserAsync(fullUrl);
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
            <Image source={{ uri: resolveImageUrl(dj.photo_profil) || '' }} style={styles.heroImage} />
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

        {/* Photo Gallery */}
        {dj.galerie_photos && dj.galerie_photos.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Galerie Photos ({dj.galerie_photos.length})</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.galleryScroll}
            >
              {dj.galerie_photos.map((photo: string, index: number) => (
                <TouchableOpacity
                  key={`photo-${index}`}
                  onPress={() => {
                    setSelectedImage(resolveImageUrl(photo) || photo);
                    setShowImageModal(true);
                  }}
                  activeOpacity={0.8}
                >
                  <Image
                    source={{ uri: resolveImageUrl(photo) || '' }}
                    style={styles.galleryImage}
                    resizeMode="cover"
                  />
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Video Gallery */}
        {dj.galerie_videos && dj.galerie_videos.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Vidéos ({dj.galerie_videos.length})</Text>
            {dj.galerie_videos.map((video: string, index: number) => (
              <TouchableOpacity
                key={`video-${index}`}
                style={styles.videoItem}
                onPress={() => WebBrowser.openBrowserAsync(video)}
              >
                <Ionicons name="play-circle" size={32} color="#8B5CF6" />
                <Text style={styles.videoText} numberOfLines={1}>{video}</Text>
                <Ionicons name="open-outline" size={18} color="#666" />
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Social Links */}
        {(dj.instagram || dj.tiktok || dj.youtube || dj.google_page || dj.site_internet) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Réseaux sociaux & Liens</Text>
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
              {dj.google_page && (
                <TouchableOpacity
                  style={styles.socialButton}
                  onPress={() => openSocialLink(dj.google_page, 'google')}
                >
                  <Ionicons name="logo-google" size={28} color="#4285F4" />
                </TouchableOpacity>
              )}
              {dj.site_internet && (
                <TouchableOpacity
                  style={styles.socialButton}
                  onPress={() => openSocialLink(dj.site_internet, 'website')}
                >
                  <Ionicons name="globe-outline" size={28} color="#8B5CF6" />
                </TouchableOpacity>
              )}
            </View>
            {dj.google_page && (
              <TouchableOpacity
                style={styles.linkRow}
                onPress={() => openSocialLink(dj.google_page, 'google')}
              >
                <Ionicons name="logo-google" size={18} color="#4285F4" />
                <Text style={styles.linkText} numberOfLines={1}>Page Google</Text>
                <Ionicons name="open-outline" size={16} color="#666" />
              </TouchableOpacity>
            )}
            {dj.site_internet && (
              <TouchableOpacity
                style={styles.linkRow}
                onPress={() => openSocialLink(dj.site_internet, 'website')}
              >
                <Ionicons name="globe-outline" size={18} color="#8B5CF6" />
                <Text style={styles.linkText} numberOfLines={1}>{dj.site_internet}</Text>
                <Ionicons name="open-outline" size={16} color="#666" />
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* Reviews */}
        {reviews.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Avis clients ({reviews.length})</Text>
            {reviews.map((review: any) => (
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

        {/* Leave a Review */}
        {reviewSuccess ? (
          <View style={styles.section}>
            <View style={styles.successCard}>
              <Ionicons name="checkmark-circle" size={40} color="#10B981" />
              <Text style={styles.successTitle}>Merci pour votre avis !</Text>
              <Text style={styles.successText}>
                Votre avis sera publié après validation par le DJ.
              </Text>
            </View>
          </View>
        ) : (
          <View style={styles.section}>
            {!showReviewForm ? (
              <TouchableOpacity
                style={styles.leaveReviewBtn}
                onPress={() => setShowReviewForm(true)}
              >
                <Ionicons name="star" size={22} color="#FFD700" />
                <Text style={styles.leaveReviewText}>Laisser un avis</Text>
                <Ionicons name="chevron-forward" size={20} color="#666" />
              </TouchableOpacity>
            ) : (
              <View style={styles.reviewFormContainer}>
                <Text style={styles.reviewFormTitle}>Votre avis</Text>

                {/* Star Rating */}
                <View style={styles.ratingRow}>
                  <Text style={styles.ratingLabel}>Note :</Text>
                  <View style={styles.starSelector}>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <TouchableOpacity
                        key={star}
                        onPress={() => setReviewForm({ ...reviewForm, note: star })}
                        style={styles.starButton}
                      >
                        <Ionicons
                          name={star <= reviewForm.note ? 'star' : 'star-outline'}
                          size={32}
                          color="#FFD700"
                        />
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>

                <TextInput
                  style={styles.reviewInput}
                  value={reviewForm.client_nom}
                  onChangeText={t => setReviewForm({ ...reviewForm, client_nom: t })}
                  placeholder="Votre nom *"
                  placeholderTextColor="#666"
                />

                <TextInput
                  style={styles.reviewInput}
                  value={reviewForm.client_email}
                  onChangeText={t => setReviewForm({ ...reviewForm, client_email: t })}
                  placeholder="Votre email *"
                  placeholderTextColor="#666"
                  keyboardType="email-address"
                  autoCapitalize="none"
                />

                <TextInput
                  style={styles.reviewInput}
                  value={reviewForm.type_evenement}
                  onChangeText={t => setReviewForm({ ...reviewForm, type_evenement: t })}
                  placeholder="Type d'événement (ex: Mariage, Anniversaire...)"
                  placeholderTextColor="#666"
                />

                <TextInput
                  style={styles.reviewInput}
                  value={reviewForm.date_evenement}
                  onChangeText={t => setReviewForm({ ...reviewForm, date_evenement: t })}
                  placeholder="Date de l'événement (ex: Mars 2025)"
                  placeholderTextColor="#666"
                />

                <TextInput
                  style={[styles.reviewInput, styles.reviewTextArea]}
                  value={reviewForm.commentaire}
                  onChangeText={t => setReviewForm({ ...reviewForm, commentaire: t })}
                  placeholder="Votre avis détaillé... *"
                  placeholderTextColor="#666"
                  multiline
                  numberOfLines={4}
                />

                <View style={styles.reviewFormActions}>
                  <TouchableOpacity
                    style={styles.cancelReviewBtn}
                    onPress={() => setShowReviewForm(false)}
                  >
                    <Text style={styles.cancelReviewText}>Annuler</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.submitReviewBtn, submittingReview && { opacity: 0.6 }]}
                    onPress={handleSubmitReview}
                    disabled={submittingReview}
                  >
                    {submittingReview ? (
                      <ActivityIndicator size="small" color="#fff" />
                    ) : (
                      <Text style={styles.submitReviewText}>Envoyer</Text>
                    )}
                  </TouchableOpacity>
                </View>

                <Text style={styles.reviewDisclaimer}>
                  Votre avis sera publié après validation par le DJ.
                </Text>
              </View>
            )}
          </View>
        )}

        <View style={styles.footer} />
      </ScrollView>

      {/* Image Fullscreen Modal */}
      {showImageModal && selectedImage && (
        <Modal
          visible={showImageModal}
          transparent={true}
          animationType="fade"
          onRequestClose={() => setShowImageModal(false)}
        >
          <View style={styles.imageModalOverlay}>
            <TouchableOpacity
              style={styles.imageModalClose}
              onPress={() => setShowImageModal(false)}
            >
              <Ionicons name="close-circle" size={40} color="#fff" />
            </TouchableOpacity>
            <Image
              source={{ uri: selectedImage }}
              style={styles.imageModalFull}
              resizeMode="contain"
            />
          </View>
        </Modal>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
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
    backgroundColor: '#12123A',
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
    backgroundColor: '#0B0B24',
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
    backgroundColor: '#12123A',
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
    backgroundColor: '#12123A',
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
    backgroundColor: '#12123A',
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
    backgroundColor: '#12123A',
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  linkRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12123A',
    borderRadius: 10,
    padding: 12,
    marginTop: 10,
  },
  linkText: {
    flex: 1,
    color: '#ccc',
    fontSize: 14,
    marginLeft: 10,
  },
  leaveReviewBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12123A',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  leaveReviewText: {
    flex: 1,
    color: '#FFD700',
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 10,
  },
  reviewFormContainer: {
    backgroundColor: '#12123A',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#1E1E4A',
  },
  reviewFormTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  ratingLabel: {
    color: '#ccc',
    fontSize: 15,
    marginRight: 12,
  },
  starSelector: {
    flexDirection: 'row',
  },
  starButton: {
    padding: 4,
  },
  reviewInput: {
    backgroundColor: '#111',
    borderRadius: 10,
    padding: 12,
    color: '#fff',
    fontSize: 15,
    borderWidth: 1,
    borderColor: '#1E1E4A',
    marginBottom: 10,
  },
  reviewTextArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  reviewFormActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
    gap: 12,
  },
  cancelReviewBtn: {
    flex: 1,
    backgroundColor: '#222',
    borderRadius: 10,
    padding: 14,
    alignItems: 'center',
  },
  cancelReviewText: {
    color: '#888',
    fontSize: 15,
    fontWeight: '600',
  },
  submitReviewBtn: {
    flex: 1,
    backgroundColor: '#8B5CF6',
    borderRadius: 10,
    padding: 14,
    alignItems: 'center',
  },
  submitReviewText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: 'bold',
  },
  reviewDisclaimer: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 12,
  },
  successCard: {
    backgroundColor: '#12123A',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.3)',
  },
  successTitle: {
    color: '#10B981',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 12,
  },
  successText: {
    color: '#888',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 8,
  },
  reviewCard: {
    backgroundColor: '#12123A',
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
  galleryScroll: {
    paddingRight: 20,
  },
  galleryImage: {
    width: 200,
    height: 200,
    borderRadius: 12,
    marginRight: 12,
    backgroundColor: '#12123A',
  },
  videoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12123A',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
  },
  videoText: {
    flex: 1,
    color: '#ccc',
    fontSize: 14,
    marginLeft: 12,
    marginRight: 8,
  },
  imageModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.95)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageModalClose: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 10,
    padding: 8,
  },
  imageModalFull: {
    width: width,
    height: width,
  },
});
