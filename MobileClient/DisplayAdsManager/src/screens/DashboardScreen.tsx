/**
 * Dashboard Screen
 * Main overview screen showing statistics and quick actions
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useApi } from '../contexts/ApiContext';
import { DashboardStats } from '../services/ApiService';
import OfflineBanner from '../components/OfflineBanner';

interface DashboardScreenProps {
  navigation: any;
}

export default function DashboardScreen({ navigation }: DashboardScreenProps) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user, logout } = useAuth();
  const api = useApi();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const dashboardStats = await api.getDashboardStats();
      setStats(dashboardStats);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleLogout = () => {
    Alert.alert(
      'Confirm Logout',
      'Are you sure you want to log out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive',
          onPress: () => logout() 
        },
      ]
    );
  };

  const StatCard = ({ title, value, color, onPress }: {
    title: string;
    value: number;
    color: string;
    onPress?: () => void;
  }) => (
    <TouchableOpacity 
      style={[styles.statCard, { borderLeftColor: color }]}
      onPress={onPress}
      disabled={!onPress}
    >
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </TouchableOpacity>
  );

  const QuickActionButton = ({ title, subtitle, color, onPress }: {
    title: string;
    subtitle: string;
    color: string;
    onPress: () => void;
  }) => (
    <TouchableOpacity 
      style={[styles.actionButton, { backgroundColor: color }]}
      onPress={onPress}
    >
      <Text style={styles.actionTitle}>{title}</Text>
      <Text style={styles.actionSubtitle}>{subtitle}</Text>
    </TouchableOpacity>
  );

  if (loading && !stats) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      <OfflineBanner />
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.welcomeText}>Welcome back,</Text>
          <Text style={styles.userName}>{user?.email}</Text>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>

      {/* Statistics Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statsRow}>
          <StatCard
            title="Campaigns"
            value={stats?.total_campaigns || 0}
            color="#007AFF"
            onPress={() => navigation.navigate('Campaigns')}
          />
          <StatCard
            title="Media Files"
            value={stats?.total_media || 0}
            color="#34C759"
            onPress={() => navigation.navigate('Media')}
          />
        </View>
        <View style={styles.statsRow}>
          <StatCard
            title="Displays"
            value={stats?.total_displays || 0}
            color="#FF9500"
            onPress={() => navigation.navigate('Displays')}
          />
          <StatCard
            title="Total Views"
            value={stats?.total_views || 0}
            color="#FF3B30"
          />
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <QuickActionButton
          title="📱 Scan QR Code"
          subtitle="Activate a new TV display"
          color="#007AFF"
          onPress={() => navigation.navigate('QRScanner')}
        />
        
        <QuickActionButton
          title="📸 Upload Media"
          subtitle="Add images or videos"
          color="#34C759"
          onPress={() => navigation.navigate('MediaUpload')}
        />
        
        <QuickActionButton
          title="🎯 Create Campaign"
          subtitle="Design a new ad campaign"
          color="#FF9500"
          onPress={() => navigation.navigate('CampaignEditor')}
        />
        
        <QuickActionButton
          title="👤 Profile Settings"
          subtitle="Update your account"
          color="#8E8E93"
          onPress={() => navigation.navigate('Profile')}
        />
      </View>

      {/* Account Type Info */}
      <View style={styles.accountInfo}>
        <Text style={styles.accountTitle}>Account Type</Text>
        <Text style={[
          styles.accountType, 
          { color: user?.account_type === 'business' ? '#007AFF' : '#8E8E93' }
        ]}>
          {user?.account_type?.toUpperCase()}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    fontSize: 16,
    color: '#8E8E93',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#FFFFFF',
  },
  welcomeText: {
    fontSize: 16,
    color: '#8E8E93',
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1D1D1F',
  },
  logoutButton: {
    padding: 8,
  },
  logoutText: {
    color: '#FF3B30',
    fontSize: 16,
    fontWeight: '600',
  },
  statsContainer: {
    padding: 16,
  },
  statsRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 8,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1D1D1F',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: '#8E8E93',
  },
  quickActionsContainer: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1D1D1F',
    marginBottom: 16,
  },
  actionButton: {
    borderRadius: 12,
    padding: 20,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  accountInfo: {
    margin: 16,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  accountTitle: {
    fontSize: 16,
    color: '#8E8E93',
    marginBottom: 4,
  },
  accountType: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});
