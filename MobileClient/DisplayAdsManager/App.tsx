/**
 * DisplayAds Mobile Manager
 * React Native app for QR code scanning, display management, and account management
 * 
 * Features:
 * - User authentication (login/register)
 * - Dashboard with statistics
 * - QR code scanning for TV activation 
 * - Campaign management
 * - Media library management
 * - Display management
 * - Analytics
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { AuthProvider } from './src/contexts/AuthContext';
import { ApiProvider } from './src/contexts/ApiContext';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import QRScannerScreen from './src/screens/QRScannerScreen';
import CampaignsScreen from './src/screens/CampaignsScreen';
import { 
  MediaLibraryScreen, 
  DisplaysScreen, 
  ProfileScreen, 
  CampaignEditorScreen, 
  MediaUploadScreen, 
  DisplayDetailScreen 
} from './src/screens/PlaceholderScreens';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Tab Navigator for authenticated users
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8E8E93',
        tabBarStyle: {
          backgroundColor: '#F8F9FA',
          borderTopWidth: 1,
          borderTopColor: '#E1E1E1',
        },
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="QRScanner" 
        component={QRScannerScreen}
        options={{
          tabBarLabel: 'Scan QR',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Campaigns" 
        component={CampaignsScreen}
        options={{
          tabBarLabel: 'Campaigns',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Media" 
        component={MediaLibraryScreen}
        options={{
          tabBarLabel: 'Media',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Displays" 
        component={DisplaysScreen}
        options={{
          tabBarLabel: 'Displays',
          headerShown: false,
        }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          tabBarLabel: 'Settings',
          headerShown: true,
          title: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
}

export default function App(): React.JSX.Element {
  return (
    <AuthProvider>
      <ApiProvider>
        <NavigationContainer>
          <Stack.Navigator 
            initialRouteName="Login"
            screenOptions={{
              headerStyle: {
                backgroundColor: '#007AFF',
              },
              headerTintColor: '#FFFFFF',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          >
            {/* Authentication Screens */}
            <Stack.Screen 
              name="Login" 
              component={LoginScreen} 
              options={{ headerShown: false }}
            />
            <Stack.Screen 
              name="Register" 
              component={RegisterScreen} 
              options={{ title: 'Create Account' }}
            />
            
            {/* Main App */}
            <Stack.Screen 
              name="Main" 
              component={MainTabs} 
              options={{ headerShown: false }}
            />
            
            {/* Detail Screens */}
            <Stack.Screen 
              name="CampaignEditor" 
              component={CampaignEditorScreen} 
              options={{ title: 'Edit Campaign' }}
            />
            <Stack.Screen 
              name="MediaUpload" 
              component={MediaUploadScreen} 
              options={{ title: 'Upload Media' }}
            />
            <Stack.Screen 
              name="DisplayDetail" 
              component={DisplayDetailScreen} 
              options={{ title: 'Display Details' }}
            />
            <Stack.Screen 
              name="Profile" 
              component={ProfileScreen} 
              options={{ title: 'Profile' }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </ApiProvider>
    </AuthProvider>
  );
}
