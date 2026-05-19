import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DJProfile } from '../types';
import { resolveImageUrl } from '../utils/imageUrl';

interface DJCardWebProps {
  dj: DJProfile;
  onPress: () => void;
  onContact?: () => void;
}

/**
 * Carte DJ horizontale optimisée WEB.
 * Style "fiche établissement" inspiré mariages.net mais identité DJ Match conservée.
 * Couleurs : noir profond + violet/fuchsia + accents dorés (boost) + blanc.
 */
export function DJCardWeb({ dj, onPress, onContact }: DJCardWebProps) {
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<Ionicons key={i} name="star" size={16} color="#FFD700" />);
      } else if (i === fullStars && hasHalf) {
        stars.push(<Ionicons key={i} name="star-half" size={16} color="#FFD700" />);
      } else {
        stars.push(<Ionicons key={i} name="star-outline" size={16} color="#FFD700" />);
      }
    }
    return stars;
  };

  return (
    <TouchableOpacity
      style={[styles.card, dj.boost_active && styles.cardBoosted]}
      onPress={onPress}
      activeOpacity={0.92}
    >
      {/* PHOTO À GAUCHE */}
      <View style={styles.imageWrapper}>
        {dj.photo_profil ? (
          <Image source={{ uri: resolveImageUrl(dj.photo_profil) || '' }} style={styles.image} />
        ) : (
          <View style={styles.placeholderImage}>
            <Ionicons name="musical-notes" size={48} color="#8B5CF6" />
          </View>
        )}
        {dj.boost_active && (
          <View style={styles.boostBadge}>
            <Ionicons name="flash" size={12} color="#000" />
            <Text style={styles.boostBadgeText}>SPONSORISÉ</Text>
          </View>
        )}
      </View>

      {/* CONTENU AU MILIEU */}
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <View style={styles.nameBlock}>
            <Text style={styles.stageName} numberOfLines={1}>
              {dj.nom_de_scene || `${dj.prenom} ${dj.nom}`}
            </Text>
            {dj.badge_verifie && (
              <View style={styles.verifiedBadge}>
                <Ionicons name="shield-checkmark" size={14} color="#fff" />
                <Text style={styles.verifiedText}>Vérifié</Text>
              </View>
            )}
          </View>
          <View style={styles.ratingBlock}>
            <View style={styles.ratingRow}>
              <Ionicons name="star" size={16} color="#FFD700" />
              <Text style={styles.ratingNumber}>{(dj.note_moyenne || 0).toFixed(1)}</Text>
            </View>
            <Text style={styles.reviewCount}>
              {dj.nombre_avis || 0} avis
            </Text>
          </View>
        </View>

        <View style={styles.locationRow}>
          <Ionicons name="location-outline" size={15} color="#A78BFA" />
          <Text style={styles.location}>
            {dj.ville}{dj.code_postal ? ` · ${dj.code_postal}` : ''}
          </Text>
        </View>

        {dj.tarif_indicatif && (
          <View style={styles.priceRow}>
            <Ionicons name="cash-outline" size={15} color="#A78BFA" />
            <Text style={styles.price}>À partir de <Text style={styles.priceValue}>{dj.tarif_indicatif}€</Text></Text>
          </View>
        )}

        {dj.types_evenements && dj.types_evenements.length > 0 && (
          <View style={styles.tags}>
            {dj.types_evenements.slice(0, 4).map((type, i) => (
              <View key={i} style={styles.tag}>
                <Text style={styles.tagText}>{type}</Text>
              </View>
            ))}
            {dj.types_evenements.length > 4 && (
              <View style={styles.tag}>
                <Text style={styles.tagText}>+{dj.types_evenements.length - 4}</Text>
              </View>
            )}
          </View>
        )}

        {dj.description && (
          <Text style={styles.description} numberOfLines={2}>
            {dj.description}
          </Text>
        )}
      </View>

      {/* CTA À DROITE */}
      <View style={styles.cta}>
        <View style={styles.ctaButton}>
          <Ionicons name="chatbubble-ellipses" size={18} color="#fff" />
          <Text style={styles.ctaText}>Contacter</Text>
        </View>
        <Text style={styles.ctaSubtext}>Voir le profil →</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: '#12123A',
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.15)',
    // @ts-ignore web shadow
    transition: 'transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease',
    // @ts-ignore web shadow
    boxShadow: '0 4px 14px rgba(0, 0, 0, 0.25)',
    minHeight: 200,
  },
  cardBoosted: {
    borderWidth: 2,
    borderColor: '#FFD700',
    // @ts-ignore web shadow
    boxShadow: '0 6px 22px rgba(255, 215, 0, 0.18)',
  },
  imageWrapper: {
    width: 280,
    position: 'relative',
    backgroundColor: '#1E1E4A',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  placeholderImage: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1E1E4A',
    justifyContent: 'center',
    alignItems: 'center',
  },
  boostBadge: {
    position: 'absolute',
    top: 12,
    left: 12,
    backgroundColor: '#FFD700',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 4,
  },
  boostBadgeText: {
    color: '#000',
    fontWeight: '800',
    fontSize: 11,
    letterSpacing: 0.5,
  },
  content: {
    flex: 1,
    padding: 20,
    gap: 8,
    justifyContent: 'space-between',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 12,
  },
  nameBlock: {
    flex: 1,
    gap: 6,
  },
  stageName: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '800',
  },
  verifiedBadge: {
    alignSelf: 'flex-start',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(139, 92, 246, 0.25)',
    borderWidth: 1,
    borderColor: '#8B5CF6',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  verifiedText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  ratingBlock: {
    alignItems: 'flex-end',
    gap: 2,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  ratingNumber: {
    color: '#FFD700',
    fontSize: 18,
    fontWeight: '800',
  },
  reviewCount: {
    color: '#A78BFA',
    fontSize: 12,
    fontWeight: '500',
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  location: {
    color: '#C4B5FD',
    fontSize: 14,
    fontWeight: '500',
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  price: {
    color: '#A78BFA',
    fontSize: 14,
  },
  priceValue: {
    color: '#fff',
    fontWeight: '700',
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 4,
  },
  tag: {
    backgroundColor: 'rgba(139, 92, 246, 0.18)',
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.35)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  tagText: {
    color: '#DDD6FE',
    fontSize: 12,
    fontWeight: '500',
  },
  description: {
    color: '#9CA3AF',
    fontSize: 13,
    lineHeight: 18,
    marginTop: 4,
  },
  cta: {
    width: 200,
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    borderLeftWidth: 1,
    borderLeftColor: 'rgba(139, 92, 246, 0.15)',
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },
  ctaButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#8B5CF6',
    paddingVertical: 12,
    paddingHorizontal: 22,
    borderRadius: 10,
    width: '100%',
    // @ts-ignore web shadow
    boxShadow: '0 4px 12px rgba(139, 92, 246, 0.4)',
  },
  ctaText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  ctaSubtext: {
    color: '#A78BFA',
    fontSize: 12,
    fontWeight: '500',
  },
});
