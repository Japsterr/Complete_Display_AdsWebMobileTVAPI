# Stage 2: Backend Integration - Digital Signage TV App

## Overview
Stage 2 focuses on integrating the React Native TV app with the Django backend API to create a fully functional ad display system. The TV app now has three clear purposes:

1. **Device Registration** - Register the TV device with user accounts
2. **Campaign Assignment** - Receive assigned ad campaigns from the backend  
3. **Ad Display** - Display ads from campaigns in a continuous loop

## Key Features Implemented

### 1. Device Activation Flow
- **DeviceActivationService**: Handles communication with Django backend
- **Unique Device IDs**: Each TV gets a unique identifier using `react-native-device-info`
- **Activation Codes**: 6-character codes (e.g., "ABC123") for easy manual entry
- **Polling System**: TV automatically checks for activation every 3 seconds

### 2. Campaign Management
- **CampaignService**: Fetches current campaign and media content
- **Media Rotation**: Automatically cycles through campaign images/videos
- **Real-time Updates**: Polls for campaign changes every 30 seconds
- **Error Handling**: Graceful handling of network issues and missing campaigns

### 3. Enhanced Player Screen
- **Full-screen Media Display**: Images displayed at full screen resolution
- **Auto-advance**: Media items advance based on their duration settings
- **Campaign Info Overlay**: Shows current campaign and media item info (can be hidden in production)
- **No Campaign State**: Clear messaging when no campaign is assigned

## App Flow

### Loading Screen
- Shows spinner and "Initializing..." text
- Checks if device is already activated
- Auto-advances to appropriate screen

### Activation Screen  
- Displays unique Device ID and activation code
- Clear instructions: "To start displaying ads:"
  1. Log in to your account on the web
  2. Go to Displays → Register New Display  
  3. Enter the code above
  4. Assign a campaign to this display
- Real-time polling for activation status

### Player Screen
- Displays campaign media in full-screen
- Automatic advancement through media items
- Handles images and videos (video requires additional setup)
- Shows "No Campaign Assigned" when appropriate

## Backend API Endpoints

### Device Registration
- `POST /api/v1/devices/request-activation/` - Get activation code
- `POST /api/v1/devices/activate/` - Web user activates device  
- `POST /api/v1/devices/check-activation/` - Check activation status

### Campaign Management
- `GET /api/v1/devices/current-campaign/?device_id=xyz` - Get assigned campaign and media

## Technical Implementation

### Services
- **DeviceActivationService**: Device registration and activation
- **CampaignService**: Campaign and media management

### Components  
- **LoadingScreen**: Simple initialization screen
- **ActivationScreen**: Device registration with real-time polling
- **PlayerScreen**: Full-screen ad display with auto-advance

### Key Dependencies
- `react-native-device-info`: For unique device identification
- Native React Native components for TV-optimized UI

## TV-Optimized Features
- **Large Fonts**: 72px activation codes, 48px+ text throughout
- **High Contrast**: White text on black backgrounds
- **Remote-Friendly**: Focus management ready for TV remote navigation
- **Full-Screen Display**: Content fills entire TV screen
- **Error Resilience**: Graceful handling of connection issues

## Next Steps
The app is now ready for:
- Stage 3: Advanced media support (video playback)
- TV remote navigation and focus management
- Production deployment and testing
- Additional campaign scheduling features

## Usage
1. Install and run the TV app on Android TV
2. Note the activation code displayed
3. Log into the web dashboard
4. Register the display using the activation code
5. Assign a campaign with media to the display
6. The TV will automatically start displaying ads

The system is designed to be simple, reliable, and focused on the core purpose: displaying advertisement campaigns on TV screens.
