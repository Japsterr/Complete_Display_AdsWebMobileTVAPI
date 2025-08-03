import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function CampaignsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Campaigns</Text>
      <Text style={styles.subtitle}>Campaign management features will be implemented here</Text>
    </View>
  );
}

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
