# Digital Signage Android TV App

## Overview
This is the Android TV application for the Digital Signage Platform. It allows TVs to connect to the platform and display campaigns automatically.

## Project Structure
```
AndroidTV/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/digitalsignage/tv/
│   │   │   ├── res/
│   │   │   ├── assets/
│   │   │   └── AndroidManifest.xml
│   │   └── androidTest/
│   ├── build.gradle
│   └── proguard-rules.pro
├── gradle/
├── build.gradle
├── settings.gradle
└── README.md
```

## Features
- ✅ Android TV optimized interface
- ✅ Automatic device activation with QR codes
- ✅ Campaign playback with media rotation
- ✅ Network connectivity handling
- ✅ Analytics and heartbeat reporting
- ✅ Settings for server configuration
- ✅ Kiosk mode for public displays
- ✅ Remote control navigation
- ✅ Auto-start on boot

## Setup Instructions

### 1. Create Android Studio Project
1. Open Android Studio
2. Create new project: "Digital Signage TV"
3. Select "TV" template
4. Package name: `com.digitalsignage.tv`
5. API Level: 21 (Android 5.0) - supports most TV devices

### 2. Configure Build Files
Copy the provided `build.gradle` and `AndroidManifest.xml` files

### 3. Add Assets
Copy the TV simulator HTML and assets to the `assets` folder

### 4. Build APK
```bash
./gradlew assembleRelease
```

## Google Play Console Setup

### 1. Create Developer Account
- Sign up at [Google Play Console](https://play.google.com/console)
- Pay $25 one-time registration fee
- Complete identity verification

### 2. Create App Listing
- App category: "Business"
- Target audience: "Business/Productivity"
- Content rating: "Everyone"
- Add screenshots and descriptions

### 3. Upload APK
- Generate signed APK bundle
- Upload to Internal Testing first
- Then promote to Production

## Publishing Checklist
- [ ] App signed with release keystore
- [ ] Privacy policy URL added
- [ ] Store listing complete with screenshots
- [ ] Content rating questionnaire completed
- [ ] Target API level compliance
- [ ] App Bundle uploaded and tested
- [ ] Pricing set (free or paid)

## Distribution Options

### Option 1: Google Play Store (Recommended)
- Widest reach and trust
- Automatic updates
- Built-in payment processing
- App security scanning

### Option 2: Enterprise Distribution
- Direct APK download from your website
- Custom OEM partnerships
- MDM (Mobile Device Management) integration
- Faster deployment for business customers

### Option 3: Alternative App Stores
- Amazon Appstore (Fire TV)
- Samsung Smart TV App Store
- LG Content Store
- Roku Channel Store (different platform)

## monetization Options
1. **Free App with Subscription**: Users download free, pay for service
2. **One-time Purchase**: Pay once, own forever
3. **Freemium**: Basic features free, premium features paid
4. **Enterprise Licensing**: Direct B2B sales with custom pricing

## Technical Requirements
- Android 5.0 (API 21) minimum
- 1GB RAM minimum
- Network connectivity required
- 100MB storage space
- TV/Leanback UI optimized
