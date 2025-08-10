import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Api from '../services/ApiService';

export default function OfflineBanner() {
  const [offline, setOffline] = useState(false);
  useEffect(() => {
    let mounted = true;
    const check = async () => {
      try {
        await Api.getHealth();
        if (mounted) setOffline(false);
      } catch {
        if (mounted) setOffline(true);
      }
    };
    check();
    const id = setInterval(check, 60000);
    return () => { mounted = false; clearInterval(id); };
  }, []);
  if (!offline) return null;
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Offline mode: showing cached data</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#78350f', paddingVertical: 6, paddingHorizontal: 12 },
  text: { color: '#fff', textAlign: 'center', fontWeight: '600' },
});
