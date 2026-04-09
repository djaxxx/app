export interface User {
  user_id: string;
  email: string;
  name: string;
  picture?: string;
  has_dj_profile?: boolean;
  is_dj?: boolean;
  is_admin?: boolean;
  dj_profile?: DJProfile;
}

export interface DJProfile {
  user_id: string;
  email: string;
  nom: string;
  prenom: string;
  nom_de_scene: string;
  telephone: string;
  ville: string;
  zone_intervention: string[];
  siret: string;
  siret_verified: boolean;
  company_name?: string;
  description: string;
  annees_experience: number;
  types_evenements: string[];
  materiel_son: string;
  materiel_lumiere: string;
  options_supplementaires: string;
  tarif_indicatif: string;
  instagram: string;
  tiktok: string;
  youtube: string;
  photo_profil: string;
  galerie_photos: string[];
  galerie_videos: string[];
  note_moyenne: number;
  nombre_avis: number;
  nombre_vues: number;
  nombre_demandes: number;
  badge_verifie: boolean;
  profil_complete_percent: number;
  subscription_status: string;
  subscription_end_date?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  boost_active?: boolean;
  boost_end?: string;
  reviews?: Review[];
}

export interface Review {
  review_id: string;
  dj_user_id: string;
  client_nom: string;
  note: number;
  commentaire: string;
  type_evenement?: string;
  created_at: string;
  verified: boolean;
}

export interface ContactRequest {
  request_id: string;
  dj_user_id: string;
  client_nom: string;
  client_email: string;
  client_telephone: string;
  date_evenement: string;
  lieu_evenement: string;
  type_evenement: string;
  message: string;
  created_at: string;
  status: string;
  read: boolean;
}

export interface EventType {
  id: string;
  label: string;
}

export interface DJSearchFilters {
  ville?: string;
  code_postal?: string;
  type_evenement?: string;
  budget_max?: number;
  note_min?: number;
  verifie_uniquement?: boolean;
}
