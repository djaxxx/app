import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DJProfile } from '../types';

interface DJCardProps {
  dj: DJProfile;
  onPress: () => void;
}

export function DJCard({ dj, onPress }: DJCardProps) {
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<Ionicons key={i} name="star" size={14} color="#FFD700" />);
      } else if (i === fullStars && hasHalf) {
        stars.push(<Ionicons key={i} name="star-half" size={14} color="#FFD700" />);
      } else {
        stars.push(<Ionicons key={i} name="star-outline" size={14} color="#FFD700" />);
      }
    }
    return stars;
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.8}>
      <View style={styles.imageContainer}>
        {dj.photo_profil ? (
          <Image source={{ uri: dj.photo_profil }} style={styles.image} />
        ) : (
          <View style={styles.placeholderImage}>
            <Ionicons name="person" size={40} color="#666" />
          </View>
        )}
        {dj.badge_verifie && (
          <View style={styles.badge}>
            <Ionicons name="checkmark-circle" size={16} color="#fff" />
            <Text style={styles.badgeText}>Vérifié</Text>
          </View>
        )}
      </View>
      
      <View style={styles.content}>
        <Text style={styles.stageName} numberOfLines={1}>{dj.nom_de_scene}</Text>
        
        <View style={styles.locationRow}>
          <Ionicons name="location" size={14} color="#888" />
          <Text style={styles.location} numberOfLines={1}>{dj.ville}</Text>
        </View>
        
        <View style={styles.ratingRow}>
          <View style={styles.stars}>{renderStars(dj.note_moyenne)}</View>
          <Text style={styles.ratingText}>
            {dj.note_moyenne.toFixed(1)} ({dj.nombre_avis} avis)
          </Text>
        </View>
        
        {dj.tarif_indicatif && (
          <Text style={styles.price}>{dj.tarif_indicatif}</Text>
        )}
        
        {dj.types_evenements && dj.types_evenements.length > 0 && (
          <View style={styles.tags}>
            {dj.types_evenements.slice(0, 2).map((type, index) => (
              <View key={index} style={styles.tag}>
                <Text style={styles.tagText}>{type}</Text>
              </View>
            ))}
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1a1a1a',
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  imageContainer: {
    height: 180,
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  placeholderImage: {
    width: '100%',
    height: '100%',
    backgroundColor: '#2a2a2a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: '#8B5CF6',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  content: {
    padding: 16,
  },
  stageName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  location: {
    color: '#888',
    fontSize: 14,
    marginLeft: 4,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  stars: {
    flexDirection: 'row',
    marginRight: 8,
  },
  ratingText: {
    color: '#888',
    fontSize: 12,
  },
  price: {
    color: '#8B5CF6',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: '#2a2a2a',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 6,
    marginTop: 4,
  },
  tagText: {
    color: '#aaa',
    fontSize: 12,
  },
});
