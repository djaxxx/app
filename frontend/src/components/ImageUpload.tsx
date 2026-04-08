import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';

interface ImageUploadProps {
  image: string | null;
  onImageChange: (base64: string | null) => void;
  label?: string;
  size?: number;
  circular?: boolean;
}

export function ImageUpload({
  image,
  onImageChange,
  label = 'Photo',
  size = 120,
  circular = true,
}: ImageUploadProps) {
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'Nous avons besoin de votre permission pour accéder à vos photos.');
        return;
      }

      setLoading(true);
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: circular ? [1, 1] : [4, 3],
        quality: 0.7,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        onImageChange(base64Image);
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Erreur', 'Impossible de sélectionner l\'image');
    } finally {
      setLoading(false);
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'Nous avons besoin de votre permission pour utiliser la caméra.');
        return;
      }

      setLoading(true);
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: circular ? [1, 1] : [4, 3],
        quality: 0.7,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        onImageChange(base64Image);
      }
    } catch (error) {
      console.error('Camera error:', error);
      Alert.alert('Erreur', 'Impossible de prendre la photo');
    } finally {
      setLoading(false);
    }
  };

  const showOptions = () => {
    Alert.alert(
      label,
      'Choisissez une option',
      [
        { text: 'Prendre une photo', onPress: takePhoto },
        { text: 'Choisir depuis la galerie', onPress: pickImage },
        ...(image ? [{ text: 'Supprimer', onPress: () => onImageChange(null), style: 'destructive' as const }] : []),
        { text: 'Annuler', style: 'cancel' as const },
      ]
    );
  };

  return (
    <View style={styles.container}>
      {label && <Text style={styles.label}>{label}</Text>}
      <TouchableOpacity
        style={[
          styles.imageContainer,
          { width: size, height: size },
          circular && { borderRadius: size / 2 },
        ]}
        onPress={showOptions}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator size="large" color="#8B5CF6" />
        ) : image ? (
          <Image
            source={{ uri: image }}
            style={[
              styles.image,
              { width: size, height: size },
              circular && { borderRadius: size / 2 },
            ]}
          />
        ) : (
          <View style={styles.placeholder}>
            <Ionicons name="camera" size={size / 3} color="#666" />
            <Text style={styles.placeholderText}>Ajouter</Text>
          </View>
        )}
        {image && (
          <View style={styles.editBadge}>
            <Ionicons name="pencil" size={14} color="#fff" />
          </View>
        )}
      </TouchableOpacity>
    </View>
  );
}

interface GalleryUploadProps {
  images: string[];
  onImagesChange: (images: string[]) => void;
  maxImages?: number;
  label?: string;
}

export function GalleryUpload({
  images,
  onImagesChange,
  maxImages = 4,
  label = 'Galerie photos',
}: GalleryUploadProps) {
  const [loading, setLoading] = useState(false);

  const addImage = async () => {
    if (images.length >= maxImages) {
      Alert.alert('Limite atteinte', `Vous pouvez ajouter maximum ${maxImages} photos.`);
      return;
    }

    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'Nous avons besoin de votre permission pour accéder à vos photos.');
        return;
      }

      setLoading(true);
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.7,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        onImagesChange([...images, base64Image]);
      }
    } catch (error) {
      console.error('Image picker error:', error);
      Alert.alert('Erreur', 'Impossible de sélectionner l\'image');
    } finally {
      setLoading(false);
    }
  };

  const removeImage = (index: number) => {
    Alert.alert(
      'Supprimer la photo',
      'Voulez-vous vraiment supprimer cette photo ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: () => {
            const newImages = [...images];
            newImages.splice(index, 1);
            onImagesChange(newImages);
          },
        },
      ]
    );
  };

  return (
    <View style={styles.galleryContainer}>
      <Text style={styles.label}>{label} ({images.length}/{maxImages})</Text>
      <View style={styles.galleryGrid}>
        {images.map((image, index) => (
          <View key={index} style={styles.galleryItem}>
            <Image source={{ uri: image }} style={styles.galleryImage} />
            <TouchableOpacity
              style={styles.removeButton}
              onPress={() => removeImage(index)}
            >
              <Ionicons name="close-circle" size={24} color="#EF4444" />
            </TouchableOpacity>
          </View>
        ))}
        {images.length < maxImages && (
          <TouchableOpacity
            style={styles.addButton}
            onPress={addImage}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator size="small" color="#8B5CF6" />
            ) : (
              <>
                <Ionicons name="add" size={32} color="#8B5CF6" />
                <Text style={styles.addButtonText}>Ajouter</Text>
              </>
            )}
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginBottom: 20,
  },
  label: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
  },
  imageContainer: {
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#2a2a2a',
    borderStyle: 'dashed',
    overflow: 'hidden',
  },
  image: {
    resizeMode: 'cover',
  },
  placeholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    color: '#666',
    fontSize: 12,
    marginTop: 4,
  },
  editBadge: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    backgroundColor: '#8B5CF6',
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  galleryContainer: {
    marginBottom: 20,
  },
  galleryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  galleryItem: {
    width: '48%',
    aspectRatio: 4 / 3,
    marginRight: '4%',
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden',
    position: 'relative',
  },
  galleryImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  removeButton: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 12,
  },
  addButton: {
    width: '48%',
    aspectRatio: 4 / 3,
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#2a2a2a',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  addButtonText: {
    color: '#8B5CF6',
    fontSize: 12,
    marginTop: 4,
  },
});
