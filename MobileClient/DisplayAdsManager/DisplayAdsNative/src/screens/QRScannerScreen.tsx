/**
 * QR Scanner Screen
 * Scans QR codes from TV displays to activate them
 * This is the key mobile-specific feature
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  TouchableOpacity,
  Modal,
  TextInput,
  ActivityIndicator,
  Linking,
  Platform,
} from 'react-native';
import { RNCamera } from 'react-native-camera';
import { check, request, PERMISSIONS, RESULTS } from 'react-native-permissions';
import { useApi } from '../contexts/ApiContext';

interface QRScannerScreenProps {
  navigation: any;
}

export default function QRScannerScreen({ navigation }: QRScannerScreenProps) {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [scanned, setScanned] = useState(false);
  const [showActivationModal, setShowActivationModal] = useState(false);
  const [activationCode, setActivationCode] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [location, setLocation] = useState('');
  const [isActivating, setIsActivating] = useState(false);
  const api = useApi();

  useEffect(() => {
    checkCameraPermission();
  }, []);

  const checkCameraPermission = async () => {
    const permission = Platform.OS === 'ios' 
      ? PERMISSIONS.IOS.CAMERA 
      : PERMISSIONS.ANDROID.CAMERA;

    const result = await check(permission);
    
    if (result === RESULTS.GRANTED) {
      setHasPermission(true);
    } else if (result === RESULTS.DENIED) {
      const requestResult = await request(permission);
      setHasPermission(requestResult === RESULTS.GRANTED);
    } else {
      setHasPermission(false);
    }
  };

  const handleBarCodeScanned = ({ data }: { data: string }) => {
    if (scanned) return;
    
    setScanned(true);
    
    // Check if the scanned data looks like an activation code
    // Activation codes are typically 6-character alphanumeric codes
    const activationCodePattern = /^[A-Z0-9]{6}$/;
    
    if (activationCodePattern.test(data)) {
      setActivationCode(data);
      setShowActivationModal(true);
    } else {
      Alert.alert(
        'Invalid QR Code',
        'This doesn\'t appear to be a DisplayAds activation code. Please scan the QR code displayed on your TV screen.',
        [
          {
            text: 'OK',
            onPress: () => setScanned(false),
          },
        ]
      );
    }
  };

  const handleActivateDevice = async () => {
    if (!displayName.trim()) {
      Alert.alert('Error', 'Please enter a display name');
      return;
    }

    setIsActivating(true);
    
    try {
      const result = await api.activateDevice(activationCode, {
        display_name: displayName.trim(),
        location: location.trim(),
      });

      Alert.alert(
        'Success!',
        `Display "${displayName}" has been activated successfully.`,
        [
          {
            text: 'OK',
            onPress: () => {
              setShowActivationModal(false);
              setScanned(false);
              setActivationCode('');
              setDisplayName('');
              setLocation('');
              // Navigate to displays list to see the new display
              navigation.navigate('Displays');
            },
          },
        ]
      );
    } catch (error: any) {
      Alert.alert(
        'Activation Failed',
        error.response?.data?.error || 'Failed to activate display. Please try again.',
        [
          {
            text: 'OK',
            onPress: () => setScanned(false),
          },
        ]
      );
    } finally {
      setIsActivating(false);
    }
  };

  const openSettings = () => {
    Linking.openSettings();
  };

  if (hasPermission === null) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Checking camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.title}>Camera Permission Required</Text>
        <Text style={styles.description}>
          To scan QR codes from your TV displays, we need access to your camera.
        </Text>
        <TouchableOpacity style={styles.primaryButton} onPress={checkCameraPermission}>
          <Text style={styles.primaryButtonText}>Grant Permission</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={openSettings}>
          <Text style={styles.secondaryButtonText}>Open Settings</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <RNCamera
        style={styles.camera}
        type={RNCamera.Constants.Type.back}
        flashMode={RNCamera.Constants.FlashMode.auto}
        onBarCodeRead={handleBarCodeScanned}
        barCodeTypes={[RNCamera.Constants.BarCodeType.qr]}
        captureAudio={false}
      >
        <View style={styles.overlay}>
          <View style={styles.topOverlay}>
            <Text style={styles.instructionText}>
              Scan the QR code displayed on your TV screen
            </Text>
          </View>
          
          <View style={styles.scanArea}>
            <View style={styles.scanFrame} />
          </View>
          
          <View style={styles.bottomOverlay}>
            <TouchableOpacity
              style={styles.manualButton}
              onPress={() => {
                setShowActivationModal(true);
                setScanned(true);
              }}
            >
              <Text style={styles.manualButtonText}>Enter Code Manually</Text>
            </TouchableOpacity>
          </View>
        </View>
      </RNCamera>

      {/* Activation Modal */}
      <Modal
        visible={showActivationModal}
        animationType="slide"
        presentationStyle="formSheet"
        onRequestClose={() => {
          if (!isActivating) {
            setShowActivationModal(false);
            setScanned(false);
          }
        }}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Activate Display</Text>
            {!isActivating && (
              <TouchableOpacity
                onPress={() => {
                  setShowActivationModal(false);
                  setScanned(false);
                }}
              >
                <Text style={styles.modalCloseButton}>✕</Text>
              </TouchableOpacity>
            )}
          </View>

          <View style={styles.modalContent}>
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Activation Code</Text>
              <TextInput
                style={styles.input}
                value={activationCode}
                onChangeText={setActivationCode}
                placeholder="Enter 6-character code"
                autoCapitalize="characters"
                maxLength={6}
                editable={!isActivating}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Display Name *</Text>
              <TextInput
                style={styles.input}
                value={displayName}
                onChangeText={setDisplayName}
                placeholder="e.g., Lobby Display, Store Front"
                editable={!isActivating}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Location</Text>
              <TextInput
                style={styles.input}
                value={location}
                onChangeText={setLocation}
                placeholder="e.g., Main Lobby, Reception Area"
                editable={!isActivating}
              />
            </View>

            <TouchableOpacity
              style={[styles.activateButton, isActivating && styles.buttonDisabled]}
              onPress={handleActivateDevice}
              disabled={isActivating}
            >
              {isActivating ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.activateButtonText}>Activate Display</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F8F9FA',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  topOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  instructionText: {
    color: '#FFFFFF',
    fontSize: 18,
    textAlign: 'center',
    fontWeight: '600',
  },
  scanArea: {
    width: 250,
    height: 250,
    alignSelf: 'center',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanFrame: {
    width: 200,
    height: 200,
    borderWidth: 2,
    borderColor: '#007AFF',
    borderRadius: 12,
    backgroundColor: 'transparent',
  },
  bottomOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom: 50,
  },
  manualButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FFFFFF',
  },
  manualButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1D1D1F',
    textAlign: 'center',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 22,
  },
  loadingText: {
    fontSize: 16,
    color: '#8E8E93',
    marginTop: 16,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  secondaryButton: {
    paddingHorizontal: 32,
    paddingVertical: 16,
  },
  secondaryButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E1E1E1',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1D1D1F',
  },
  modalCloseButton: {
    fontSize: 20,
    color: '#8E8E93',
    padding: 4,
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1D1D1F',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E1E1E1',
  },
  activateButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisabled: {
    backgroundColor: '#A8A8A8',
  },
  activateButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
});
