/**
 * DisplayAds Mobile Manager - Full Featured App
 * React Native app with complete dashboard functionality
 */

import React, {useState, useEffect} from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  TextInput,
  ActivityIndicator,
  RefreshControl,
  FlatList,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Configuration
const API_ENDPOINTS = [
  'http://192.168.3.73:8000/api/v1',
  'http://10.0.2.2:8000/api/v1',
  'http://127.0.0.1:8000/api/v1',
];

let CURRENT_API_BASE_URL = API_ENDPOINTS[0];

function App(): React.JSX.Element {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [user, setUser] = useState<any>(null);
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<string>('dashboard');
  const [refreshing, setRefreshing] = useState<boolean>(false);
  
  // Dashboard data
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [media, setMedia] = useState<any[]>([]);
  const [displays, setDisplays] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    checkApiConnection();
    checkStoredAuth();
  }, []);

  const checkApiConnection = async () => {
    setApiStatus('checking');
    
    for (const endpoint of API_ENDPOINTS) {
      try {
        console.log(`Trying to connect to: ${endpoint}`);
        const response = await axios.get(`${endpoint}/health/`, {
          timeout: 3000,
        });
        if (response.status === 200) {
          console.log(`Successfully connected to: ${endpoint}`);
          CURRENT_API_BASE_URL = endpoint;
          setApiStatus('connected');
          return;
        }
      } catch (error: any) {
        console.log(`Failed to connect to ${endpoint}:`, error.message);
      }
    }
    
    setApiStatus('disconnected');
    console.log('All API endpoints failed');
  };

  const checkStoredAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      const userData = await AsyncStorage.getItem('user_data');
      
      if (token && userData && apiStatus === 'connected') {
        setUser(JSON.parse(userData));
        setIsLoggedIn(true);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        loadDashboardData();
      }
    } catch (error) {
      console.log('Error checking stored auth:', error);
    }
  };

  const handleLogin = async () => {
    if (apiStatus === 'disconnected') {
      Alert.alert('Connection Required', 'Please ensure the API server is running.');
      return;
    }

    if (!email || !password) {
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${CURRENT_API_BASE_URL}/login/`, {
        email: email.trim(),
        password: password,
      });

      if (response.data.access) {
        // Store tokens and user data
        await AsyncStorage.setItem('access_token', response.data.access);
        await AsyncStorage.setItem('refresh_token', response.data.refresh);
        await AsyncStorage.setItem('user_data', JSON.stringify(response.data.user));
        
        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        setUser(response.data.user);
        setIsLoggedIn(true);
        setEmail('');
        setPassword('');
        
        // Load dashboard data
        await loadDashboardData();
        
        Alert.alert('Success', 'Logged in successfully!');
      }
    } catch (error: any) {
      console.log('Login error:', error.response?.data || error.message);
      Alert.alert('Login Failed', error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
      await AsyncStorage.removeItem('user_data');
      
      delete axios.defaults.headers.common['Authorization'];
      
      setIsLoggedIn(false);
      setUser(null);
      setActiveSection('dashboard');
      setCampaigns([]);
      setMedia([]);
      setDisplays([]);
      setAnalytics(null);
    } catch (error) {
      console.log('Logout error:', error);
    }
  };

  const loadDashboardData = async () => {
    try {
      // Load campaigns
      const campaignsResponse = await axios.get(`${CURRENT_API_BASE_URL}/campaigns/`);
      setCampaigns(campaignsResponse.data.results || campaignsResponse.data);

      // Load media
      const mediaResponse = await axios.get(`${CURRENT_API_BASE_URL}/media/`);
      setMedia(mediaResponse.data.results || mediaResponse.data);

      // Load displays
      const displaysResponse = await axios.get(`${CURRENT_API_BASE_URL}/displays/`);
      setDisplays(displaysResponse.data.results || displaysResponse.data);

      // Load analytics
      try {
        const analyticsResponse = await axios.get(`${CURRENT_API_BASE_URL}/analytics/dashboard/`);
        setAnalytics(analyticsResponse.data);
      } catch (error) {
        console.log('Analytics not available:', error);
      }
    } catch (error: any) {
      console.log('Error loading dashboard data:', error.response?.data || error.message);
      Alert.alert('Error', 'Failed to load dashboard data');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active': return '#28A745';
      case 'ready': return '#007BFF';
      case 'draft': return '#FFC107';
      case 'paused': return '#DC3545';
      default: return '#6C757D';
    }
  };

  const renderCampaignItem = ({item}: {item: any}) => (
    <View style={styles.listItem}>
      <View style={styles.listItemHeader}>
        <Text style={styles.listItemTitle}>{item.name}</Text>
        <View style={[styles.statusBadge, {backgroundColor: getStatusColor(item.status)}]}>
          <Text style={styles.statusText}>{item.status?.toUpperCase() || 'DRAFT'}</Text>
        </View>
      </View>
      <Text style={styles.listItemSubtitle}>Budget: R{item.budget || '0'}</Text>
      <Text style={styles.listItemDate}>Created: {new Date(item.created_at).toLocaleDateString()}</Text>
    </View>
  );

  const renderMediaItem = ({item}: {item: any}) => (
    <View style={styles.listItem}>
      <Text style={styles.listItemTitle}>{item.title}</Text>
      <Text style={styles.listItemSubtitle}>Type: {item.media_type || 'Unknown'}</Text>
      <Text style={styles.listItemDate}>Uploaded: {new Date(item.created_at).toLocaleDateString()}</Text>
    </View>
  );

  const renderDisplayItem = ({item}: {item: any}) => (
    <View style={styles.listItem}>
      <View style={styles.listItemHeader}>
        <Text style={styles.listItemTitle}>{item.name}</Text>
        <View style={[styles.statusBadge, {backgroundColor: item.is_active ? '#28A745' : '#DC3545'}]}>
          <Text style={styles.statusText}>{item.is_active ? 'ONLINE' : 'OFFLINE'}</Text>
        </View>
      </View>
      <Text style={styles.listItemSubtitle}>Location: {item.location || 'Unknown'}</Text>
      {item.last_heartbeat && (
        <Text style={styles.listItemDate}>
          Last seen: {new Date(item.last_heartbeat).toLocaleString()}
        </Text>
      )}
    </View>
  );

  // Login Screen
  if (!isLoggedIn) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#6366f1" />
        <ScrollView contentInsetAdjustmentBehavior="automatic" style={styles.scrollView}>
          <View style={styles.loginContainer}>
            <View style={styles.logoContainer}>
              <Text style={styles.appTitle}>DisplayAds</Text>
              <Text style={styles.appSubtitle}>Manager</Text>
              <Text style={styles.tagline}>Mobile Management Platform</Text>
            </View>

            <View style={[styles.connectionStatus, {backgroundColor: apiStatus === 'connected' ? '#28A745' : '#DC3545'}]}>
              <Text style={styles.connectionText}>
                {apiStatus === 'connected' ? 'API Connected ✓' : 'API Disconnected ✗'}
              </Text>
            </View>

            <View style={styles.loginForm}>
              <TextInput
                style={styles.input}
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                autoCorrect={false}
                keyboardType="email-address"
              />
              
              <TextInput
                style={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
                autoCorrect={false}
              />
              
              <TouchableOpacity 
                style={[styles.loginButton, (apiStatus === 'disconnected' || isLoading) && styles.disabledButton]} 
                onPress={handleLogin}
                disabled={apiStatus === 'disconnected' || isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color="#ffffff" />
                ) : (
                  <Text style={styles.loginButtonText}>Login to Dashboard</Text>
                )}
              </TouchableOpacity>
            </View>
            
            <TouchableOpacity 
              style={styles.retryButton} 
              onPress={checkApiConnection}
            >
              <Text style={styles.retryButtonText}>Test Connection</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Dashboard Menu
  if (activeSection === 'dashboard') {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#6366f1" />
        <ScrollView 
          contentInsetAdjustmentBehavior="automatic" 
          style={styles.scrollView}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
          <View style={styles.dashboardHeader}>
            <Text style={styles.welcomeText}>Welcome, {user?.email || 'User'}</Text>
            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
              <Text style={styles.logoutButtonText}>Logout</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.statsContainer}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{campaigns.length}</Text>
              <Text style={styles.statLabel}>Campaigns</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{media.length}</Text>
              <Text style={styles.statLabel}>Media Files</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{displays.length}</Text>
              <Text style={styles.statLabel}>Displays</Text>
            </View>
          </View>

          <View style={styles.menuContainer}>
            <TouchableOpacity style={styles.menuItem} onPress={() => setActiveSection('campaigns')}>
              <Text style={styles.menuItemTitle}>📺 Campaigns</Text>
              <Text style={styles.menuItemSubtitle}>Manage your advertising campaigns ({campaigns.length})</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem} onPress={() => setActiveSection('media')}>
              <Text style={styles.menuItemTitle}>🎬 Media Library</Text>
              <Text style={styles.menuItemSubtitle}>Upload and organize media files ({media.length})</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem} onPress={() => setActiveSection('displays')}>
              <Text style={styles.menuItemTitle}>📱 Displays</Text>
              <Text style={styles.menuItemSubtitle}>Monitor connected devices ({displays.length})</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem} onPress={() => setActiveSection('analytics')}>
              <Text style={styles.menuItemTitle}>📊 Analytics</Text>
              <Text style={styles.menuItemSubtitle}>View performance metrics</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem} onPress={() => Alert.alert('QR Scanner', 'QR Scanner feature coming soon!')}>
              <Text style={styles.menuItemTitle}>� QR Scanner</Text>
              <Text style={styles.menuItemSubtitle}>Scan QR codes for device setup</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Section views
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#6366f1" />
      
      <View style={styles.sectionHeader}>
        <TouchableOpacity onPress={() => setActiveSection('dashboard')}>
          <Text style={styles.backButton}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.sectionTitle}>{activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}</Text>
        <TouchableOpacity onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={
          activeSection === 'campaigns' ? campaigns :
          activeSection === 'media' ? media :
          activeSection === 'displays' ? displays : []
        }
        renderItem={
          activeSection === 'campaigns' ? renderCampaignItem :
          activeSection === 'media' ? renderMediaItem :
          activeSection === 'displays' ? renderDisplayItem : 
          () => null
        }
        keyExtractor={(item) => item.id?.toString() || Math.random().toString()}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No {activeSection} found</Text>
            <Text style={styles.emptyStateSubtext}>Pull down to refresh</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  // Common styles
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  
  // Login screen styles
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    minHeight: 500,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  appTitle: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#6366f1',
    marginBottom: 8,
  },
  appSubtitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#8b5cf6',
    marginBottom: 8,
  },
  tagline: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
  },
  connectionStatus: {
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 30,
    minWidth: 250,
  },
  connectionText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  connectionDetail: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.9,
    textAlign: 'center',
  },
  loginForm: {
    width: '100%',
    alignItems: 'center',
    gap: 15,
    marginBottom: 20,
  },
  input: {
    width: '80%',
    height: 50,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: '#ffffff',
  },
  loginButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    width: '80%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  disabledButton: {
    backgroundColor: '#94a3b8',
    opacity: 0.6,
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  retryButton: {
    backgroundColor: '#8b5cf6',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  
  // Dashboard styles
  dashboardHeader: {
    backgroundColor: '#6366f1',
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  welcomeText: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: '#8b5cf6',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  
  // Stats cards
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    paddingBottom: 10,
  },
  statCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 80,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6366f1',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#64748b',
    textAlign: 'center',
  },
  
  // Menu styles
  menuContainer: {
    padding: 20,
    paddingTop: 10,
    gap: 15,
  },
  menuItem: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
  },
  menuItemTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
  menuItemSubtitle: {
    fontSize: 14,
    color: '#64748b',
  },
  
  // Section view styles
  sectionHeader: {
    backgroundColor: '#6366f1',
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  backButton: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '500',
  },
  sectionTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '600',
  },
  
  // List styles
  listContainer: {
    padding: 16,
  },
  listItem: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  listItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  listItemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    flex: 1,
  },
  listItemSubtitle: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 4,
  },
  listItemDate: {
    fontSize: 12,
    color: '#94a3b8',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '600',
  },
  
  // Empty state
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#94a3b8',
  },
});

export default App;
