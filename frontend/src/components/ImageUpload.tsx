import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  Platform,
  Modal,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../services/api';
import { resolveImageUrl } from '../utils/imageUrl';

// Helper: convert blob/uri to base64 on web
const uriToBase64 = async (uri: string): Promise<string> => {
  if (uri.startsWith('data:')) return uri;
  try {
    const response = await fetch(uri);
    const blob = await response.blob();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch {
    return uri;
  }
};

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
  const [showMenu, setShowMenu] = useState(false);

  const pickImage = async () => {
    setShowMenu(false);
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        if (Platform.OS === 'web') {
          window.alert('Permission requise pour accéder à vos photos.');
        } else {
          Alert.alert('Permission requise', 'Nous avons besoin de votre permission pour accéder à vos photos.');
        }
        return;
      }

      setLoading(true);
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: circular ? [1, 1] : [4, 3],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        let base64Data: string;
        if (asset.base64) {
          base64Data = `data:image/jpeg;base64,${asset.base64}`;
        } else if (asset.uri) {
          base64Data = await uriToBase64(asset.uri);
        } else {
          return;
        }
        // Upload to server and get URL
        try {
          const url = await api.uploadImage(base64Data, 'profile');
          onImageChange(url);
        } catch (uploadErr) {
          console.error('Upload error, falling back to base64:', uploadErr);
          onImageChange(base64Data);
        }
      }
    } catch (error) {
      console.error('Image picker error:', error);
      if (Platform.OS === 'web') {
        window.alert('Impossible de sélectionner l\'image');
      } else {
        Alert.alert('Erreur', 'Impossible de sélectionner l\'image');
      }
    } finally {
      setLoading(false);
    }
  };

  const takePhoto = async () => {
    setShowMenu(false);
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        if (Platform.OS === 'web') {
          window.alert('Permission requise pour utiliser la caméra.');
        } else {
          Alert.alert('Permission requise', 'Nous avons besoin de votre permission pour utiliser la caméra.');
        }
        return;
      }

      setLoading(true);
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: circular ? [1, 1] : [4, 3],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        let base64Data: string;
        if (asset.base64) {
          base64Data = `data:image/jpeg;base64,${asset.base64}`;
        } else if (asset.uri) {
          base64Data = await uriToBase64(asset.uri);
        } else {
          return;
        }
        // Upload to server and get URL
        try {
          const url = await api.uploadImage(base64Data, 'profile');
          onImageChange(url);
        } catch (uploadErr) {
          console.error('Upload error, falling back to base64:', uploadErr);
          onImageChange(base64Data);
        }
      }
    } catch (error) {
      console.error('Camera error:', error);
      if (Platform.OS === 'web') {
        window.alert('Impossible de prendre la photo');
      } else {
        Alert.alert('Erreur', 'Impossible de prendre la photo');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePress = () => {
    if (Platform.OS === 'web') {
      // On web, directly open file picker
      pickImage();
    } else {
      setShowMenu(true);
    }
  };

  const removeImage = () => {
    setShowMenu(false);
    onImageChange(null);
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
        onPress={handlePress}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator size="large" color="#8B5CF6" />
        ) : image ? (
          <Image
            source={{ uri: resolveImageUrl(image) || image }}
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

      {/* Web: show remove button below image */}
      {Platform.OS === 'web' && image && (
        <TouchableOpacity style={styles.webRemoveBtn} onPress={removeImage}>
          <Ionicons name="trash-outline" size={16} color="#EF4444" />
          <Text style={styles.webRemoveText}>Supprimer</Text>
        </TouchableOpacity>
      )}

      {/* Native: Action Sheet Modal */}
      {Platform.OS !== 'web' && (
        <Modal
          visible={showMenu}
          transparent
          animationType="slide"
          onRequestClose={() => setShowMenu(false)}
        >
          <TouchableOpacity
            style={styles.modalOverlay}
            activeOpacity={1}
            onPress={() => setShowMenu(false)}
          >
            <View style={styles.menuContainer}>
              <Text style={styles.menuTitle}>{label}</Text>

              <TouchableOpacity style={styles.menuOption} onPress={takePhoto}>
                <Ionicons name="camera" size={22} color="#8B5CF6" />
                <Text style={styles.menuOptionText}>Prendre une photo</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.menuOption} onPress={pickImage}>
                <Ionicons name="images" size={22} color="#8B5CF6" />
                <Text style={styles.menuOptionText}>Choisir depuis la galerie</Text>
              </TouchableOpacity>

              {image && (
                <TouchableOpacity style={styles.menuOption} onPress={removeImage}>
                  <Ionicons name="trash" size={22} color="#EF4444" />
                  <Text style={[styles.menuOptionText, { color: '#EF4444' }]}>Supprimer</Text>
                </TouchableOpacity>
              )}

              <TouchableOpacity
                style={[styles.menuOption, styles.menuCancel]}
                onPress={() => setShowMenu(false)}
              >
                <Text style={styles.menuCancelText}>Annuler</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </Modal>
      )}
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
      if (Platform.OS === 'web') {
        window.alert(`Vous pouvez ajouter maximum ${maxImages} photos.`);
      } else {
        Alert.alert('Limite atteinte', `Vous pouvez ajouter maximum ${maxImages} photos.`);
      }
      return;
    }

    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        if (Platform.OS === 'web') {
          window.alert('Permission requise pour accéder à vos photos.');
        } else {
          Alert.alert('Permission requise', 'Nous avons besoin de votre permission pour accéder à vos photos.');
        }
        return;
      }

      setLoading(true);
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        let imageData: string;
        if (asset.base64) {
          imageData = `data:image/jpeg;base64,${asset.base64}`;
        } else if (asset.uri) {
          imageData = await uriToBase64(asset.uri);
        } else {
          return;
        }
        // Upload to server and get URL
        try {
          const url = await api.uploadImage(imageData, 'gallery');
          onImagesChange([...images, url]);
        } catch (uploadErr) {
          console.error('Gallery upload error, falling back to base64:', uploadErr);
          onImagesChange([...images, imageData]);
        }
      }
    } catch (error) {
      console.error('Image picker error:', error);
      if (Platform.OS === 'web') {
        window.alert('Impossible de sélectionner l\'image');
      } else {
        Alert.alert('Erreur', 'Impossible de sélectionner l\'image');
      }
    } finally {
      setLoading(false);
    }
  };

  const removeImage = (index: number) => {
    const doRemove = () => {
      const newImages = [...images];
      newImages.splice(index, 1);
      onImagesChange(newImages);
    };

    if (Platform.OS === 'web') {
      if (window.confirm('Supprimer cette photo ?')) {
        doRemove();
      }
    } else {
      Alert.alert(
        'Supprimer la photo',
        'Voulez-vous vraiment supprimer cette photo ?',
        [
          { text: 'Annuler', style: 'cancel' },
          { text: 'Supprimer', style: 'destructive', onPress: doRemove },
        ]
      );
    }
  };

  return (
    <View style={styles.galleryContainer}>
      <Text style={styles.label}>{label} ({images.length}/{maxImages})</Text>
      <View style={styles.galleryGrid}>
        {images.map((image, index) => (
          <View key={index} style={styles.galleryItem}>
            <Image source={{ uri: resolveImageUrl(image) || image }} style={styles.galleryImage} />
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
    backgroundColor: '#12123A',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#1E1E4A',
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
    backgroundColor: '#12123A',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#1E1E4A',
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
  webRemoveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderRadius: 8,
  },
  webRemoveText: {
    color: '#EF4444',
    fontSize: 12,
    marginLeft: 4,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'flex-end',
  },
  menuContainer: {
    backgroundColor: '#12123A',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: 40,
  },
  menuTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
  },
  menuOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 4,
  },
  menuOptionText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 12,
  },
  menuCancel: {
    backgroundColor: '#222',
    marginTop: 8,
    justifyContent: 'center',
  },
  menuCancelText: {
    color: '#888',
    fontSize: 16,
    textAlign: 'center',
  },
});
