/**
 * DisplayAds Mobile Manager - Minimal Version
 * React Native app for display management
 */

import React from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
} from 'react-native';

function App(): React.JSX.Element {
  const handlePress = (feature: string) => {
    Alert.alert('Feature Coming Soon', `${feature} will be implemented in the next version.`);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      <ScrollView contentInsetAdjustmentBehavior="automatic" style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>DisplayAds Manager</Text>
          <Text style={styles.subtitle}>Mobile Management App</Text>
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={styles.button} 
            onPress={() => handlePress('Login')}
          >
            <Text style={styles.buttonText}>Login</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.button} 
            onPress={() => handlePress('QR Scanner')}
          >
            <Text style={styles.buttonText}>Scan QR Code</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.button} 
            onPress={() => handlePress('Campaigns')}
          >
            <Text style={styles.buttonText}>Manage Campaigns</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.button} 
            onPress={() => handlePress('Displays')}
          >
            <Text style={styles.buttonText}>Manage Displays</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.button} 
            onPress={() => handlePress('Media Library')}
          >
            <Text style={styles.buttonText}>Media Library</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Successfully built with React Native 0.75.4!
          </Text>
          <Text style={styles.footerText}>
            APK ready for deployment and feature expansion.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 40,
    alignItems: 'center',
    backgroundColor: '#007AFF',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  buttonContainer: {
    padding: 20,
    gap: 15,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
    marginTop: 20,
  },
  footerText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 5,
  },
});

export default App;
