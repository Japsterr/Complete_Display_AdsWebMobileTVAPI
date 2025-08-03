// Simple placeholder implementation for remaining screens
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const createPlaceholderScreen = (title: string, description: string) => {
  return function PlaceholderScreen() {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.subtitle}>{description}</Text>
      </View>
    );
  };
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1D1D1F',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
});

export const MediaLibraryScreen = createPlaceholderScreen('Media Library', 'Media management features will be implemented here');
export const DisplaysScreen = createPlaceholderScreen('Displays', 'Display monitoring features will be implemented here');
export const ProfileScreen = createPlaceholderScreen('Profile', 'User profile features will be implemented here');
export const CampaignEditorScreen = createPlaceholderScreen('Campaign Editor', 'Campaign creation features will be implemented here');
export const MediaUploadScreen = createPlaceholderScreen('Media Upload', 'Media upload features will be implemented here');
export const DisplayDetailScreen = createPlaceholderScreen('Display Details', 'Display detail features will be implemented here');
