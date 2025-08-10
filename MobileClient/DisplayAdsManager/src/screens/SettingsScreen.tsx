import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { useApi } from '../contexts/ApiContext';

export default function SettingsScreen() {
  const api = useApi();
  const [baseUrl, setBaseUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const current = await api.getBaseUrl();
        setBaseUrl(current);
      } catch {}
      setLoading(false);
    })();
  }, []);

  const onSave = async () => {
    if (!/^https?:\/\//i.test(baseUrl)) {
      Alert.alert('Invalid URL', 'Please enter a valid http/https URL.');
      return;
    }
    setSaving(true);
    try {
      await api.setBaseUrl(baseUrl);
      Alert.alert('Saved', 'Server URL updated.');
    } catch (e) {
      Alert.alert('Error', 'Failed to save URL.');
    } finally {
      setSaving(false);
    }
  };

  const onTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
  const res = await api.getHealth?.();
  if (res && (res.status === 'ok' || res.status === 'healthy')) {
        setTestResult('✅ API reachable');
      } else {
        // fallback: try campaigns (auth may be required)
        try {
          await api.getCampaigns();
          setTestResult('✅ API reachable (campaigns)');
        } catch (e) {
          setTestResult('⚠️ API reachable but requires login');
        }
      }
    } catch (e: any) {
      setTestResult(`❌ Cannot reach API: ${e?.message || 'Unknown error'}`);
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={{ marginTop: 8 }}>Loading…</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Settings</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Server Base URL</Text>
        <TextInput
          style={styles.input}
          value={baseUrl}
          onChangeText={setBaseUrl}
          placeholder="http://<ip>:8000/api/v1/"
          autoCapitalize="none"
          autoCorrect={false}
        />
        <View style={styles.row}>
          <TouchableOpacity style={[styles.button, styles.secondary]} onPress={onTest} disabled={testing}>
            {testing ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Test Connection</Text>}
          </TouchableOpacity>
          <TouchableOpacity style={[styles.button, styles.primary]} onPress={onSave} disabled={saving}>
            {saving ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Save URL</Text>}
          </TouchableOpacity>
        </View>
        {testResult && <Text style={styles.testResult}>{testResult}</Text>}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: '700', marginBottom: 16 },
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, elevation: 1 },
  label: { fontSize: 14, color: '#555', marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 12,
  },
  row: { flexDirection: 'row', gap: 12 },
  button: { flex: 1, paddingVertical: 12, borderRadius: 8, alignItems: 'center' },
  primary: { backgroundColor: '#007AFF' },
  secondary: { backgroundColor: '#6B7280' },
  buttonText: { color: '#fff', fontWeight: '700' },
  testResult: { marginTop: 10, fontSize: 14 },
});
