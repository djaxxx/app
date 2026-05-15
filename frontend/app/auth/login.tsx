import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import * as AppleAuthentication from 'expo-apple-authentication';
import { useAuthStore } from '../../src/stores/authStore';
import { api } from '../../src/services/api';

export default function LoginScreen() {
  const router = useRouter();
  const { registerWithEmail, loginWithEmail, error, clearError, isLoading, checkAuth } = useAuthStore();

  const [isRegister, setIsRegister] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState('');
  const [socialLoading, setSocialLoading] = useState(false);

  const handleGoogleAuth = async () => {
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      const redirectUrl = `${window.location.origin}/auth/callback`;
      const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
      window.location.href = authUrl;
    } else {
      // Native: use WebBrowser (Safari View Controller on iOS)
      try {
        setSocialLoading(true);
        const callbackUrl = 'djmatch://auth/callback';
        const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(callbackUrl)}`;
        const result = await WebBrowser.openAuthSessionAsync(authUrl, callbackUrl);
        
        if (result.type === 'success' && result.url) {
          // Extract session_id from URL
          const url = result.url;
          const hashPart = url.split('#')[1] || '';
          const params = new URLSearchParams(hashPart);
          const sessionId = params.get('session_id');
          
          if (sessionId) {
            const user = await useAuthStore.getState().exchangeSession(sessionId);
            if (user) {
              if (user.has_dj_profile) {
                router.replace('/(tabs)/dashboard');
              } else {
                router.replace('/dj-register');
              }
            }
          }
        }
      } catch (error) {
        console.error('Google auth error:', error);
        setLocalError('Erreur de connexion Google. Reessayez.');
      } finally {
        setSocialLoading(false);
      }
    }
  };

  const handleAppleAuth = async () => {
    try {
      setSocialLoading(true);
      const credential = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
          AppleAuthentication.AppleAuthenticationScope.EMAIL,
        ],
      });

      // Send credential to backend
      const response = await api.request<any>('/api/auth/apple', {
        method: 'POST',
        body: JSON.stringify({
          identityToken: credential.identityToken,
          fullName: credential.fullName,
          email: credential.email,
          user: credential.user,
        }),
      });

      if (response) {
        await checkAuth();
        if (response.has_dj_profile) {
          router.replace('/(tabs)/dashboard');
        } else {
          router.replace('/dj-register');
        }
      }
    } catch (error: any) {
      if (error.code !== 'ERR_REQUEST_CANCELED') {
        console.error('Apple auth error:', error);
        setLocalError('Erreur de connexion Apple. Reessayez.');
      }
    } finally {
      setSocialLoading(false);
    }
  };

  const handleEmailSubmit = async () => {
    setLocalError('');
    clearError();

    if (!email.trim()) {
      setLocalError('Veuillez entrer votre email');
      return;
    }
    if (!password || password.length < 6) {
      setLocalError('Le mot de passe doit contenir au moins 6 caracteres');
      return;
    }
    if (isRegister && !name.trim()) {
      setLocalError('Veuillez entrer votre nom');
      return;
    }

    let user;
    if (isRegister) {
      user = await registerWithEmail(email.trim(), password, name.trim());
    } else {
      user = await loginWithEmail(email.trim(), password);
    }

    if (user) {
      if (user.has_dj_profile) {
        router.replace('/(tabs)/dashboard');
      } else {
        router.replace('/dj-register');
      }
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    setLocalError('');
    clearError();
  };

  const displayError = localError || error;

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Back button */}
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color="#fff" />
          </TouchableOpacity>

          {/* Logo */}
          <View style={styles.logoContainer}>
            <View style={styles.logoCircle}>
              <Ionicons name="musical-notes" size={40} color="#8B5CF6" />
            </View>
            <Text style={styles.appName}>DJ Match</Text>
            <Text style={styles.subtitle}>
              {isRegister ? 'Creez votre compte DJ' : 'Connectez-vous'}
            </Text>
          </View>

          {/* Apple Sign In - iOS only (REQUIRED by Apple) */}
          {Platform.OS === 'ios' && (
            <TouchableOpacity style={styles.appleButton} onPress={handleAppleAuth} disabled={socialLoading}>
              {socialLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="logo-apple" size={22} color="#fff" />
                  <Text style={styles.appleButtonText}>
                    {isRegister ? "S'inscrire avec Apple" : 'Se connecter avec Apple'}
                  </Text>
                </>
              )}
            </TouchableOpacity>
          )}

          {/* Google Button */}
          <TouchableOpacity style={styles.googleButton} onPress={handleGoogleAuth} disabled={socialLoading}>
            {socialLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <>
                <Ionicons name="logo-google" size={22} color="#fff" />
                <Text style={styles.googleButtonText}>
                  {isRegister ? "S'inscrire avec Google" : 'Se connecter avec Google'}
                </Text>
              </>
            )}
          </TouchableOpacity>

          {/* Divider */}
          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>ou par email</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* Email Form */}
          {isRegister && (
            <View style={styles.inputContainer}>
              <Ionicons name="person-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Votre nom complet"
                placeholderTextColor="#666"
                value={name}
                onChangeText={setName}
                autoCapitalize="words"
              />
            </View>
          )}

          <View style={styles.inputContainer}>
            <Ionicons name="mail-outline" size={20} color="#666" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Adresse email"
              placeholderTextColor="#666"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />
          </View>

          <View style={styles.inputContainer}>
            <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Mot de passe (6 caracteres min.)"
              placeholderTextColor="#666"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
              <Ionicons name={showPassword ? 'eye-off' : 'eye'} size={20} color="#666" />
            </TouchableOpacity>
          </View>

          {/* Error message */}
          {displayError ? (
            <View style={styles.errorContainer}>
              <Ionicons name="alert-circle" size={16} color="#EF4444" />
              <Text style={styles.errorText}>{displayError}</Text>
            </View>
          ) : null}

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
            onPress={handleEmailSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.submitButtonText}>
                {isRegister ? "Creer mon compte" : 'Se connecter'}
              </Text>
            )}
          </TouchableOpacity>

          {/* Toggle mode */}
          <TouchableOpacity onPress={toggleMode} style={styles.toggleContainer}>
            <Text style={styles.toggleText}>
              {isRegister
                ? 'Deja inscrit ? '
                : 'Pas encore de compte ? '}
            </Text>
            <Text style={styles.toggleLink}>
              {isRegister ? 'Se connecter' : "S'inscrire"}
            </Text>
          </TouchableOpacity>

          {/* Trial info */}
          {isRegister && (
            <View style={styles.trialInfo}>
              <Ionicons name="gift-outline" size={18} color="#8B5CF6" />
              <Text style={styles.trialInfoText}>
                15 jours d'essai gratuit inclus !
              </Text>
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0B0B24',
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  backButton: {
    marginTop: 8,
    marginBottom: 8,
    width: 44,
    height: 44,
    justifyContent: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(139, 92, 246, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  appName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 16,
    color: '#888',
    marginTop: 4,
  },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4285F4',
    borderRadius: 14,
    paddingVertical: 16,
    marginBottom: 20,
  },
  googleButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 10,
  },
  appleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#000',
    borderRadius: 14,
    paddingVertical: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  appleButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 10,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  dividerText: {
    color: '#666',
    paddingHorizontal: 12,
    fontSize: 13,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    marginBottom: 12,
    paddingHorizontal: 14,
    height: 54,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    height: '100%',
  },
  eyeIcon: {
    padding: 8,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
    gap: 8,
  },
  errorText: {
    color: '#EF4444',
    fontSize: 14,
    flex: 1,
  },
  submitButton: {
    backgroundColor: '#8B5CF6',
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 4,
    marginBottom: 16,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '700',
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 20,
  },
  toggleText: {
    color: '#888',
    fontSize: 14,
  },
  toggleLink: {
    color: '#8B5CF6',
    fontSize: 14,
    fontWeight: '600',
  },
  trialInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    borderRadius: 12,
    padding: 14,
    gap: 8,
  },
  trialInfoText: {
    color: '#8B5CF6',
    fontSize: 14,
    fontWeight: '600',
  },
});
