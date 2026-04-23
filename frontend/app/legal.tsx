import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

const SECTIONS = [
  { id: 'mentions', title: 'Mentions legales', icon: 'document-text' },
  { id: 'privacy', title: 'Confidentialite (RGPD)', icon: 'shield-checkmark' },
  { id: 'cgu', title: 'CGU / CGV', icon: 'clipboard' },
  { id: 'cookies', title: 'Cookies', icon: 'ellipse' },
  { id: 'payment', title: 'Paiement & Abonnement', icon: 'card' },
] as const;

export default function LegalScreen() {
  const router = useRouter();
  const [activeSection, setActiveSection] = useState<string>('mentions');

  const renderContent = () => {
    switch (activeSection) {
      case 'mentions':
        return (
          <View>
            <Text style={s.h2}>Mentions legales</Text>
            <Text style={s.label}>Editeur de l'application</Text>
            <Text style={s.p}>DJ AS - Adrien Sebert</Text>
            <Text style={s.p}>08 rue Jean Motreuil, La Chapelle-pres-Sees</Text>
            <Text style={s.p}>Email : adrien.sebert@gmail.com</Text>
            <Text style={s.p}>SIRET : 53234667300025</Text>
            <Text style={s.label}>Responsable de la publication</Text>
            <Text style={s.p}>Adrien Sebert</Text>
            <Text style={s.label}>Hebergeur</Text>
            <Text style={s.p}>Emergent (emergent.sh) — Plateforme cloud Kubernetes</Text>
            <Text style={s.p}>Base de donnees : MongoDB Atlas</Text>
            <Text style={s.p}>Paiement : Stripe Inc. (stripe.com)</Text>
          </View>
        );
      case 'privacy':
        return (
          <View>
            <Text style={s.h2}>Politique de confidentialite (RGPD)</Text>
            <Text style={s.p}>Derniere mise a jour : Avril 2026</Text>

            <Text style={s.label}>1. Donnees collectees</Text>
            <Text style={s.bullet}>- Compte DJ : nom, prenom, email, telephone, SIRET, ville, code postal, description, photos, reseaux sociaux</Text>
            <Text style={s.bullet}>- Compte client : nom, email (via formulaire de contact)</Text>
            <Text style={s.bullet}>- Donnees techniques : adresse IP, type d'appareil, pages visitees</Text>
            <Text style={s.bullet}>- Paiement : gerees directement par Stripe (nous ne stockons pas vos donnees bancaires)</Text>

            <Text style={s.label}>2. Finalite du traitement</Text>
            <Text style={s.bullet}>- Inscription et gestion de compte DJ</Text>
            <Text style={s.bullet}>- Mise en relation clients / DJs</Text>
            <Text style={s.bullet}>- Gestion des abonnements et paiements</Text>
            <Text style={s.bullet}>- Statistiques de frequentation (anonymisees)</Text>
            <Text style={s.bullet}>- Amelioration du service</Text>

            <Text style={s.label}>3. Duree de conservation</Text>
            <Text style={s.bullet}>- Donnees de compte : conservees tant que le compte est actif</Text>
            <Text style={s.bullet}>- Donnees de contact : 12 mois apres la derniere interaction</Text>
            <Text style={s.bullet}>- Donnees de facturation : 10 ans (obligation legale)</Text>
            <Text style={s.bullet}>- Logs techniques : 12 mois</Text>

            <Text style={s.label}>4. Vos droits (RGPD)</Text>
            <Text style={s.p}>Conformement au RGPD, vous disposez des droits suivants :</Text>
            <Text style={s.bullet}>- Droit d'acces a vos donnees</Text>
            <Text style={s.bullet}>- Droit de rectification</Text>
            <Text style={s.bullet}>- Droit a l'effacement (suppression de compte)</Text>
            <Text style={s.bullet}>- Droit a la portabilite</Text>
            <Text style={s.bullet}>- Droit d'opposition</Text>
            <Text style={s.p}>Pour exercer ces droits : adrien.sebert@gmail.com</Text>
            <Text style={s.p}>Vous pouvez egalement supprimer votre compte directement depuis l'onglet Profil de l'application.</Text>

            <Text style={s.label}>5. Partage avec des tiers</Text>
            <Text style={s.bullet}>- Stripe : traitement des paiements</Text>
            <Text style={s.bullet}>- Google OAuth : authentification</Text>
            <Text style={s.bullet}>- INSEE (API SIRENE) : verification des numeros SIRET</Text>
            <Text style={s.bullet}>- API Geo Gouv : geolocalisation par code postal</Text>
            <Text style={s.p}>Aucune donnee n'est vendue a des tiers.</Text>

            <Text style={s.label}>6. Securite</Text>
            <Text style={s.p}>Les donnees sont stockees sur des serveurs securises (MongoDB Atlas) avec chiffrement en transit (HTTPS/TLS) et au repos. Les mots de passe sont haches avec bcrypt.</Text>
          </View>
        );
      case 'cgu':
        return (
          <View>
            <Text style={s.h2}>Conditions Generales d'Utilisation</Text>

            <Text style={s.label}>1. Objet</Text>
            <Text style={s.p}>DJ Match France est une plateforme d'annuaire professionnel permettant la mise en relation entre des DJs professionnels declares et des particuliers recherchant un DJ pour leurs evenements.</Text>

            <Text style={s.label}>2. Inscription DJ</Text>
            <Text style={s.bullet}>- L'inscription est reservee aux DJs professionnels disposant d'un numero SIRET valide</Text>
            <Text style={s.bullet}>- Le DJ s'engage a fournir des informations exactes et a jour</Text>
            <Text style={s.bullet}>- Un essai gratuit de 15 jours est offert a chaque nouvelle inscription</Text>

            <Text style={s.label}>3. Abonnement</Text>
            <Text style={s.bullet}>- Mensuel : 8 euros/mois</Text>
            <Text style={s.bullet}>- Annuel : 80 euros/an (economie de 16 euros)</Text>
            <Text style={s.bullet}>- Paiement securise via Stripe</Text>

            <Text style={s.label}>4. Boost de profil</Text>
            <Text style={s.bullet}>- 1 semaine : 19 euros (paiement unique)</Text>
            <Text style={s.bullet}>- 2 semaines : 29 euros (paiement unique)</Text>
            <Text style={s.bullet}>- 1 mois : 39 euros (paiement unique)</Text>

            <Text style={s.label}>5. Resiliation</Text>
            <Text style={s.p}>L'utilisateur peut resilier son abonnement a tout moment depuis son espace personnel. La resiliation prend effet a la fin de la periode en cours.</Text>

            <Text style={s.label}>6. Droit de retractation</Text>
            <Text style={s.p}>Conformement a l'article L221-28 du Code de la consommation, le droit de retractation de 14 jours s'applique. Pour exercer ce droit, contactez : adrien.sebert@gmail.com</Text>

            <Text style={s.label}>7. Responsabilite</Text>
            <Text style={s.p}>DJ Match France agit en tant qu'intermediaire et ne peut etre tenu responsable des prestations realisees par les DJs inscrits.</Text>

            <Text style={s.label}>8. Comportements interdits</Text>
            <Text style={s.bullet}>- Publication de contenu illegal ou diffamatoire</Text>
            <Text style={s.bullet}>- Usurpation d'identite</Text>
            <Text style={s.bullet}>- Utilisation de faux avis</Text>
            <Text style={s.bullet}>- Toute tentative de fraude ou manipulation</Text>

            <Text style={s.label}>9. Propriete intellectuelle</Text>
            <Text style={s.p}>L'ensemble du contenu de l'application (logo, design, code) est la propriete de DJ AS - Adrien Sebert. Toute reproduction est interdite.</Text>

            <Text style={s.label}>10. Droit applicable</Text>
            <Text style={s.p}>Les presentes CGU sont regies par le droit francais. En cas de litige, les tribunaux francais seront competents.</Text>
          </View>
        );
      case 'cookies':
        return (
          <View>
            <Text style={s.h2}>Politique de cookies</Text>
            <Text style={s.label}>Cookies utilises</Text>
            <Text style={s.bullet}>- Cookie de session (session_token) : necessaire au fonctionnement de l'authentification. Expire a la fermeture du navigateur ou apres 7 jours.</Text>
            <Text style={s.bullet}>- Aucun cookie publicitaire ou de tracking n'est utilise.</Text>
            <Text style={s.bullet}>- Aucun Google Analytics, Facebook Pixel ou tracker tiers n'est installe.</Text>
            <Text style={s.label}>Consentement</Text>
            <Text style={s.p}>Seuls des cookies strictement necessaires au fonctionnement sont utilises. Conformement a la directive ePrivacy, ils ne necessitent pas de consentement prealable.</Text>
          </View>
        );
      case 'payment':
        return (
          <View>
            <Text style={s.h2}>Paiement & Abonnement</Text>

            <Text style={s.label}>Prix (TTC)</Text>
            <Text style={s.bullet}>- Abonnement mensuel : 8,00 euros TTC / mois</Text>
            <Text style={s.bullet}>- Abonnement annuel : 80,00 euros TTC / an</Text>
            <Text style={s.bullet}>- Boost 1 semaine : 19,00 euros TTC</Text>
            <Text style={s.bullet}>- Boost 2 semaines : 29,00 euros TTC</Text>
            <Text style={s.bullet}>- Boost 1 mois : 39,00 euros TTC</Text>
            <Text style={s.bullet}>- Extension zone (+1 departement) : 20,00 euros TTC</Text>

            <Text style={s.label}>Essai gratuit</Text>
            <Text style={s.p}>Chaque nouveau DJ beneficie d'un essai gratuit de 15 jours. Aucun paiement n'est requis pendant cette periode.</Text>

            <Text style={s.label}>Moyen de paiement</Text>
            <Text style={s.p}>Les paiements sont traites par Stripe (stripe.com). Nous acceptons les cartes bancaires (Visa, Mastercard, American Express). Vos donnees bancaires ne transitent jamais par nos serveurs.</Text>

            <Text style={s.label}>Resiliation</Text>
            <Text style={s.p}>Vous pouvez resilier votre abonnement a tout moment. Votre profil restera actif jusqu'a la fin de la periode payee.</Text>

            <Text style={s.label}>Droit de retractation</Text>
            <Text style={s.p}>Vous disposez d'un delai de 14 jours pour exercer votre droit de retractation. Contactez adrien.sebert@gmail.com avec votre numero de commande.</Text>

            <Text style={s.label}>Remboursement</Text>
            <Text style={s.p}>En cas de probleme technique empechant l'utilisation du service, un remboursement au prorata peut etre accorde. Contactez-nous pour toute reclamation.</Text>
          </View>
        );
      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={s.container}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Informations legales</Text>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.tabs} contentContainerStyle={s.tabsContent}>
        {SECTIONS.map(sec => (
          <TouchableOpacity
            key={sec.id}
            style={[s.tab, activeSection === sec.id && s.tabActive]}
            onPress={() => setActiveSection(sec.id)}
          >
            <Ionicons name={sec.icon as any} size={16} color={activeSection === sec.id ? '#fff' : '#888'} />
            <Text style={[s.tabText, activeSection === sec.id && s.tabTextActive]}>{sec.title}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView style={s.content} contentContainerStyle={s.contentInner}>
        {renderContent()}
        <View style={s.footer}>
          <Text style={s.footerText}>DJ Match France - DJ AS</Text>
          <Text style={s.footerText}>adrien.sebert@gmail.com</Text>
          <Text style={s.footerText}>SIRET : 53234667300025</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0B0B24' },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12 },
  backBtn: { width: 44, height: 44, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#fff', marginLeft: 8 },
  tabs: { maxHeight: 48, borderBottomWidth: 1, borderBottomColor: '#1E1E4A' },
  tabsContent: { paddingHorizontal: 12, alignItems: 'center' },
  tab: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 10, marginRight: 6, borderRadius: 20, backgroundColor: '#12123A' },
  tabActive: { backgroundColor: '#8B5CF6' },
  tabText: { color: '#888', fontSize: 13, fontWeight: '600', marginLeft: 6 },
  tabTextActive: { color: '#fff' },
  content: { flex: 1 },
  contentInner: { padding: 20, paddingBottom: 60 },
  h2: { fontSize: 22, fontWeight: 'bold', color: '#fff', marginBottom: 16 },
  label: { fontSize: 16, fontWeight: 'bold', color: '#8B5CF6', marginTop: 20, marginBottom: 8 },
  p: { fontSize: 14, color: '#ccc', lineHeight: 22, marginBottom: 6 },
  bullet: { fontSize: 14, color: '#aaa', lineHeight: 22, marginBottom: 4, paddingLeft: 8 },
  footer: { marginTop: 40, paddingTop: 20, borderTopWidth: 1, borderTopColor: '#1E1E4A', alignItems: 'center' },
  footerText: { color: '#666', fontSize: 12, marginBottom: 4 },
});
