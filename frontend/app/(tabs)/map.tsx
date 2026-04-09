import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
  Modal,
  Dimensions,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../src/services/api';
import { EventType } from '../../src/types';

const { width, height } = Dimensions.get('window');
const isWeb = Platform.OS === 'web';

interface DJMarker {
  user_id: string;
  nom_de_scene: string;
  ville: string;
  department_name?: string;
  region_name?: string;
  latitude: number;
  longitude: number;
  note_moyenne: number;
  badge_verifie: boolean;
  tarif_indicatif?: string;
}

export default function MapScreen() {
  const router = useRouter();
  const webViewRef = useRef<any>(null);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  const [djs, setDJs] = useState<DJMarker[]>([]);
  const [loading, setLoading] = useState(true);
  const [eventTypes, setEventTypes] = useState<EventType[]>([]);
  const [regions, setRegions] = useState<{ code: string; name: string }[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    region_code: '',
    type_evenement: '',
    verifie_uniquement: false,
  });
  const [selectedDJ, setSelectedDJ] = useState<DJMarker | null>(null);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadDJs();
  }, [filters]);

  // Send markers when map becomes ready and DJs are loaded
  useEffect(() => {
    if (mapReady && djs.length > 0) {
      sendMarkersToMap(djs);
    }
  }, [mapReady]);

  // Web: Listen for messages from iframe
  useEffect(() => {
    if (!isWeb) return;
    
    const handleMessage = (event: MessageEvent) => {
      try {
        const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        if (data.type === 'markerClick') {
          const dj = djs.find(d => d.user_id === data.user_id);
          if (dj) setSelectedDJ(dj);
        } else if (data.type === 'mapReady') {
          setMapReady(true);
          if (djs.length > 0) {
            sendMarkersToMap(djs);
          }
        }
      } catch {}
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [djs]);

  const loadInitialData = async () => {
    try {
      const [typesData, regionsData] = await Promise.all([
        api.getEventTypes(),
        api.getRegions(),
      ]);
      setEventTypes(typesData);
      setRegions(regionsData);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const sendMarkersToMap = (markers: DJMarker[]) => {
    const message = JSON.stringify({ type: 'updateMarkers', markers });
    if (isWeb && iframeRef.current) {
      iframeRef.current.contentWindow?.postMessage(message, '*');
    } else if (!isWeb && webViewRef.current) {
      webViewRef.current.postMessage(message);
    }
  };

  const loadDJs = async () => {
    setLoading(true);
    try {
      const result = await api.getDJsForMap({
        region_code: filters.region_code || undefined,
        type_evenement: filters.type_evenement || undefined,
        verifie_uniquement: filters.verifie_uniquement,
      });
      setDJs(result.djs);
      
      // Update map markers
      if (mapReady) {
        sendMarkersToMap(result.djs);
      }
    } catch (error) {
      console.error('Error loading DJs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWebViewMessage = (event: any) => {
    try {
      const data = JSON.parse(event.nativeEvent.data);
      if (data.type === 'markerClick') {
        const dj = djs.find(d => d.user_id === data.user_id);
        if (dj) {
          setSelectedDJ(dj);
        }
      }
    } catch (error) {
      console.error('WebView message error:', error);
    }
  };

  const mapHTML = `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body, #map { width: 100%; height: 100%; }
    .custom-marker {
      background: #8B5CF6;
      border-radius: 50%;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 14px;
      border: 3px solid white;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .custom-marker.verified {
      background: #10B981;
    }
    .marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {
      background: rgba(139, 92, 246, 0.6);
    }
    .marker-cluster-small div, .marker-cluster-medium div, .marker-cluster-large div {
      background: #8B5CF6;
      color: white;
      font-weight: bold;
    }
    .leaflet-popup-content-wrapper {
      background: #12123A;
      color: white;
      border-radius: 12px;
    }
    .leaflet-popup-tip {
      background: #12123A;
    }
    .dj-popup {
      padding: 8px;
      min-width: 150px;
    }
    .dj-popup h3 {
      margin: 0 0 4px 0;
      font-size: 14px;
    }
    .dj-popup p {
      margin: 2px 0;
      font-size: 12px;
      color: #888;
    }
    .dj-popup .verified {
      color: #10B981;
      font-size: 11px;
    }
    .dj-popup .rating {
      color: #FFD700;
    }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    const map = L.map('map').setView([46.603354, 1.888334], 6);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap © CARTO',
      maxZoom: 19
    }).addTo(map);
    
    const markers = L.markerClusterGroup({
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
    });
    map.addLayer(markers);
    
    function createMarkerIcon(dj) {
      const initial = dj.nom_de_scene.charAt(0).toUpperCase();
      const className = dj.badge_verifie ? 'custom-marker verified' : 'custom-marker';
      return L.divIcon({
        html: '<div class="' + className + '">' + initial + '</div>',
        iconSize: [36, 36],
        className: ''
      });
    }
    
    function updateMarkers(djList) {
      markers.clearLayers();
      
      djList.forEach(dj => {
        if (dj.latitude && dj.longitude) {
          const marker = L.marker([dj.latitude, dj.longitude], {
            icon: createMarkerIcon(dj)
          });
          
          const verifiedBadge = dj.badge_verifie ? '<span class="verified">✓ Vérifié</span>' : '';
          const rating = dj.note_moyenne > 0 ? '<span class="rating">★ ' + dj.note_moyenne.toFixed(1) + '</span>' : '';
          
          marker.bindPopup(
            '<div class="dj-popup">' +
            '<h3>' + dj.nom_de_scene + '</h3>' +
            '<p>' + dj.ville + '</p>' +
            (dj.tarif_indicatif ? '<p>' + dj.tarif_indicatif + '</p>' : '') +
            '<p>' + verifiedBadge + ' ' + rating + '</p>' +
            '</div>'
          );
          
          marker.on('click', () => {
            window.ReactNativeWebView.postMessage(JSON.stringify({
              type: 'markerClick',
              user_id: dj.user_id
            }));
          });
          
          markers.addLayer(marker);
        }
      });
    }
    
    // Notify parent that map is ready
    window.parent.postMessage(JSON.stringify({ type: 'mapReady' }), '*');
    if (window.ReactNativeWebView) {
      window.ReactNativeWebView.postMessage(JSON.stringify({ type: 'mapReady' }));
    }
    
    // Listen for messages from React Native
    document.addEventListener('message', function(e) {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'updateMarkers') {
          updateMarkers(data.markers);
        }
      } catch (err) {}
    });
    
    window.addEventListener('message', function(e) {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'updateMarkers') {
          updateMarkers(data.markers);
        }
      } catch (err) {}
    });
  </script>
</body>
</html>
`;

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Carte des DJ</Text>
        <TouchableOpacity style={styles.filterButton} onPress={() => setShowFilters(true)}>
          <Ionicons name="options" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {/* Stats */}
      <View style={styles.statsBar}>
        <Text style={styles.statsText}>
          {loading ? 'Chargement...' : `${djs.length} DJ actifs sur la carte`}
        </Text>
      </View>

      {/* Map */}
      <View style={styles.mapContainer}>
        {isWeb ? (
          <iframe
            ref={(ref: any) => { iframeRef.current = ref; }}
            srcDoc={mapHTML}
            style={{ width: '100%', height: '100%', border: 'none' } as any}
            onLoad={() => {
              setMapReady(true);
              if (djs.length > 0 && iframeRef.current) {
                setTimeout(() => {
                  sendMarkersToMap(djs);
                }, 500);
              }
            }}
          />
        ) : (
          (() => {
            const { WebView } = require('react-native-webview');
            return (
              <WebView
                ref={webViewRef}
                source={{ html: mapHTML }}
                style={styles.map}
                onMessage={handleWebViewMessage}
                onLoad={() => {
                  setMapReady(true);
                  if (djs.length > 0 && webViewRef.current) {
                    webViewRef.current.postMessage(JSON.stringify({
                      type: 'updateMarkers',
                      markers: djs,
                    }));
                  }
                }}
                javaScriptEnabled={true}
                domStorageEnabled={true}
                startInLoadingState={true}
                renderLoading={() => (
                  <View style={styles.loadingOverlay}>
                    <ActivityIndicator size="large" color="#8B5CF6" />
                  </View>
                )}
              />
            );
          })()
        )}
      </View>

      {/* Filter Modal */}
      <Modal visible={showFilters} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Filtres</Text>
              <TouchableOpacity onPress={() => setShowFilters(false)}>
                <Ionicons name="close" size={24} color="#fff" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalScroll}>
              {/* Region Filter */}
              <Text style={styles.filterLabel}>Région</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
                <TouchableOpacity
                  style={[styles.filterChip, !filters.region_code && styles.filterChipActive]}
                  onPress={() => setFilters({ ...filters, region_code: '' })}
                >
                  <Text style={[styles.filterChipText, !filters.region_code && styles.filterChipTextActive]}>
                    Toutes
                  </Text>
                </TouchableOpacity>
                {regions.map((region) => (
                  <TouchableOpacity
                    key={region.code}
                    style={[styles.filterChip, filters.region_code === region.code && styles.filterChipActive]}
                    onPress={() => setFilters({ ...filters, region_code: region.code })}
                  >
                    <Text style={[styles.filterChipText, filters.region_code === region.code && styles.filterChipTextActive]}>
                      {region.name}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              {/* Event Type Filter */}
              <Text style={styles.filterLabel}>Type d'événement</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
                <TouchableOpacity
                  style={[styles.filterChip, !filters.type_evenement && styles.filterChipActive]}
                  onPress={() => setFilters({ ...filters, type_evenement: '' })}
                >
                  <Text style={[styles.filterChipText, !filters.type_evenement && styles.filterChipTextActive]}>
                    Tous
                  </Text>
                </TouchableOpacity>
                {eventTypes.map((type) => (
                  <TouchableOpacity
                    key={type.id}
                    style={[styles.filterChip, filters.type_evenement === type.id && styles.filterChipActive]}
                    onPress={() => setFilters({ ...filters, type_evenement: type.id })}
                  >
                    <Text style={[styles.filterChipText, filters.type_evenement === type.id && styles.filterChipTextActive]}>
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              {/* Verified Only */}
              <TouchableOpacity
                style={styles.checkboxRow}
                onPress={() => setFilters({ ...filters, verifie_uniquement: !filters.verifie_uniquement })}
              >
                <Ionicons
                  name={filters.verifie_uniquement ? 'checkbox' : 'square-outline'}
                  size={24}
                  color="#8B5CF6"
                />
                <Text style={styles.checkboxText}>DJ vérifiés uniquement</Text>
              </TouchableOpacity>
            </ScrollView>

            <TouchableOpacity style={styles.applyButton} onPress={() => setShowFilters(false)}>
              <Text style={styles.applyButtonText}>Appliquer</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* DJ Detail Modal */}
      <Modal visible={!!selectedDJ} animationType="slide" transparent>
        <View style={styles.djModalOverlay}>
          <View style={styles.djModalContent}>
            <TouchableOpacity style={styles.djModalClose} onPress={() => setSelectedDJ(null)}>
              <Ionicons name="close" size={24} color="#fff" />
            </TouchableOpacity>
            
            {selectedDJ && (
              <>
                <View style={styles.djModalHeader}>
                  <Text style={styles.djModalName}>{selectedDJ.nom_de_scene}</Text>
                  {selectedDJ.badge_verifie && (
                    <View style={styles.djModalBadge}>
                      <Ionicons name="checkmark-circle" size={16} color="#fff" />
                      <Text style={styles.djModalBadgeText}>Vérifié</Text>
                    </View>
                  )}
                </View>
                
                <View style={styles.djModalInfo}>
                  <Ionicons name="location" size={16} color="#888" />
                  <Text style={styles.djModalInfoText}>
                    {selectedDJ.ville}
                    {selectedDJ.department_name && ` (${selectedDJ.department_name})`}
                  </Text>
                </View>
                
                {selectedDJ.note_moyenne > 0 && (
                  <View style={styles.djModalInfo}>
                    <Ionicons name="star" size={16} color="#FFD700" />
                    <Text style={styles.djModalInfoText}>{selectedDJ.note_moyenne.toFixed(1)}</Text>
                  </View>
                )}
                
                {selectedDJ.tarif_indicatif && (
                  <View style={styles.djModalInfo}>
                    <Ionicons name="pricetag" size={16} color="#10B981" />
                    <Text style={styles.djModalInfoText}>{selectedDJ.tarif_indicatif}</Text>
                  </View>
                )}
                
                <TouchableOpacity
                  style={styles.djModalButton}
                  onPress={() => {
                    setSelectedDJ(null);
                    router.push(`/dj/${selectedDJ.user_id}`);
                  }}
                >
                  <Text style={styles.djModalButtonText}>Voir le profil</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  filterButton: {
    backgroundColor: '#8B5CF6',
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsBar: {
    paddingHorizontal: 20,
    paddingBottom: 8,
  },
  statsText: {
    color: '#888',
    fontSize: 14,
  },
  mapContainer: {
    flex: 1,
    overflow: 'hidden',
  },
  map: {
    flex: 1,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#0B0B24',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#12123A',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  modalScroll: {
    maxHeight: 400,
  },
  filterLabel: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 12,
  },
  filterScroll: {
    marginBottom: 8,
  },
  filterChip: {
    backgroundColor: '#1E1E4A',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: '#8B5CF6',
  },
  filterChipText: {
    color: '#888',
    fontSize: 14,
  },
  filterChipTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
    paddingVertical: 12,
  },
  checkboxText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 12,
  },
  applyButton: {
    backgroundColor: '#8B5CF6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  applyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  djModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
  },
  djModalContent: {
    backgroundColor: '#12123A',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
  },
  djModalClose: {
    position: 'absolute',
    top: 16,
    right: 16,
    zIndex: 1,
  },
  djModalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  djModalName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginRight: 12,
  },
  djModalBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#10B981',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  djModalBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  djModalInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  djModalInfoText: {
    color: '#ccc',
    fontSize: 16,
    marginLeft: 8,
  },
  djModalButton: {
    backgroundColor: '#8B5CF6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  djModalButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
