# Digital Signage Management App for Android

A native Android application for managing digital signage displays, QR code scanning for device activation, and comprehensive account management.

## Features

### Core Management Features
- **QR Code Scanning**: Scan TV displays for instant activation and setup
- **Display Management**: Monitor and control all registered displays
- **Account Management**: Complete user profile and subscription management
- **Campaign Management**: Create, edit, and deploy content campaigns
- **Media Upload**: Upload images and videos directly from mobile device
- **Real-time Monitoring**: Live status of all displays and campaigns

### Mobile-Optimized Interface
- **Native Android UI**: Designed for phones and tablets
- **Offline Capabilities**: Queue actions when network is unavailable
- **Push Notifications**: Alerts for display status and campaign updates
- **Biometric Authentication**: Fingerprint and face unlock support
- **Material Design 3**: Modern Android design language

### Integration Features
- **Django API Integration**: Full sync with web dashboard
- **JWT Authentication**: Secure API communication
- **File Upload**: Direct media upload to server
- **Stripe Integration**: Mobile subscription management
- **Analytics Dashboard**: Mobile-friendly campaign analytics

## Technical Architecture

### Android Components
- **MainActivity**: Main navigation and display list
- **QRScannerActivity**: Camera-based QR code scanning
- **DisplayDetailActivity**: Individual display management
- **CampaignActivity**: Campaign creation and editing
- **AccountActivity**: User profile and subscription management
- **SettingsActivity**: App configuration and preferences

### Key Dependencies
- **CameraX**: Modern camera API for QR scanning
- **Retrofit**: HTTP client for API communication
- **Room Database**: Local data caching and offline support
- **WorkManager**: Background sync and upload tasks
- **Material Components**: Android design system
- **Biometric**: Authentication support

### API Integration
- Base URL: Configurable server endpoint
- Authentication: JWT token-based
- Endpoints: Full REST API compatibility with web dashboard
- File Upload: Multipart upload for media files
- Real-time Updates: WebSocket or polling for live updates

## Build Requirements

- Android SDK 21+ (Android 5.0+)
- Gradle 8.5
- Kotlin 1.9.22
- Android Gradle Plugin 8.2.2
- Camera permission for QR scanning
- Internet permission for API communication
- Storage permission for media upload

## Installation

### Development Build
```bash
cd c:\DisplayAdsAPI\AndroidManagement
.\gradlew.bat assembleDebug
```

### Release Build
```bash
.\gradlew.bat assembleRelease
```

## Configuration

### Server Configuration
Update `app/build.gradle` with your server URL:
```gradle
buildConfigField "String", "API_BASE_URL", '"https://your-server.com/api/v1"'
```

### App Signing
For production releases, configure signing in `app/build.gradle`:
```gradle
signingConfigs {
    release {
        storeFile file('your-keystore.keystore')
        storePassword 'your-store-password'
        keyAlias 'your-key-alias'
        keyPassword 'your-key-password'
    }
}
```

## Usage

1. **Initial Setup**: Configure server URL in app settings
2. **Login**: Use web dashboard credentials or register new account
3. **Scan Display**: Use QR scanner to activate new TV displays
4. **Manage Content**: Upload media and create campaigns
5. **Monitor Displays**: View real-time status and analytics

## Google Play Store

This app is designed for Google Play Store distribution with:
- Professional app structure
- Privacy policy compliance
- Content rating guidelines
- Store listing optimization

## Support

For technical support and documentation:
- Web Dashboard: Access full feature set
- API Documentation: Developer resources
- User Guide: Step-by-step instructions
