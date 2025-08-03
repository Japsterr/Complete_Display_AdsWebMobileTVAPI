/**
 * Digital Signage TV App
 * React Native app for displaying advertisement campaigns on Android TV
 * Simple 3-screen flow: Loading → Activation → Ad Player
 */

import React, {useState, useEffect} from 'react';
import {
  StatusBar,
  StyleSheet,
  View,
  TouchableOpacity,
  Text,
} from 'react-native';

import LoadingScreen from './src/components/LoadingScreen';
import ActivationScreen from './src/components/ActivationScreen';
import PlayerScreen from './src/components/PlayerScreen';
import DeviceActivationService from './src/services/DeviceActivationService';

// App states
type AppState = 'LOADING' | 'NEEDS_ACTIVATION' | 'PLAYING_CONTENT';

function App(): React.JSX.Element {
  const [appState, setAppState] = useState<AppState>('LOADING');

  useEffect(() => {
    // Initialize app - check if device is already activated
    const initializeApp = async () => {
      try {
        // Initialize device info first
        await DeviceActivationService.initialize();
        
        // Check if device is already activated
        const status = await DeviceActivationService.checkActivationStatus();
        
        if (status.activated) {
          console.log('Device already activated:', status.display_name);
          setAppState('PLAYING_CONTENT');
        } else {
          console.log('Device needs activation');
          setAppState('NEEDS_ACTIVATION');
        }
        
      } catch (error) {
        console.error('App initialization error:', error);
        // If we can't connect to backend, still go to activation screen
        // The ActivationScreen will handle the connection error gracefully
        setAppState('NEEDS_ACTIVATION');
      }
    };

    if (appState === 'LOADING') {
      initializeApp();
    }
  }, [appState]);

  const renderCurrentScreen = () => {
    switch (appState) {
      case 'LOADING':
        return <LoadingScreen />;
      case 'NEEDS_ACTIVATION':
        return <ActivationScreen onActivated={() => setAppState('PLAYING_CONTENT')} />;
      case 'PLAYING_CONTENT':
        return <PlayerScreen />;
      default:
        return <LoadingScreen />;
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar hidden={true} />
      {renderCurrentScreen()}
      
      {/* Development/Testing Controls - Remove in production */}
      <View style={styles.debugControls}>
        <TouchableOpacity 
          style={styles.debugButton} 
          onPress={() => setAppState('LOADING')}
        >
          <Text style={styles.debugButtonText}>Loading</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.debugButton} 
          onPress={() => setAppState('NEEDS_ACTIVATION')}
        >
          <Text style={styles.debugButtonText}>Activation</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.debugButton} 
          onPress={() => setAppState('PLAYING_CONTENT')}
        >
          <Text style={styles.debugButtonText}>Player</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  debugControls: {
    position: 'absolute',
    top: 20,
    right: 20,
    flexDirection: 'row',
    gap: 10,
  },
  debugButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 5,
  },
  debugButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '500',
  },
});

export default App;
