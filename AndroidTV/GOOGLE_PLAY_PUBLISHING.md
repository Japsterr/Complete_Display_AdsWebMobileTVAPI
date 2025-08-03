# Google Play Store Publishing Guide

This guide will help you publish the Digital Signage TV app to the Google Play Store.

## Prerequisites

1. **Google Play Console Account**: You need a Google Play Console developer account ($25 one-time fee)
2. **Android Studio**: With SDK tools installed
3. **Keystore**: For signing your app (we'll create this)

## Step 1: Prepare Your App for Release

### 1.1 Update Version Information
Edit `app/build.gradle`:
```gradle
android {
    defaultConfig {
        versionCode 2  // Increment for each release
        versionName "1.1"  // User-visible version
    }
}
```

### 1.2 Generate Signed APK

1. **Create Keystore** (one-time setup):
```bash
cd c:\DisplayAdsAPI\AndroidTV
keytool -genkey -v -keystore digitalsignage-release-key.keystore -alias digitalsignage -keyalg RSA -keysize 2048 -validity 10000
```

2. **Create signing configuration** in `app/build.gradle`:
```gradle
android {
    signingConfigs {
        release {
            storeFile file('digitalsignage-release-key.keystore')
            storePassword 'YOUR_KEYSTORE_PASSWORD'
            keyAlias 'digitalsignage'
            keyPassword 'YOUR_KEY_PASSWORD'
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

3. **Build Release APK**:
```bash
cd c:\DisplayAdsAPI\AndroidTV
./gradlew assembleRelease
```

## Step 2: Prepare Store Assets

### 2.1 App Icon
- Create app icons in various sizes (48x48, 72x72, 96x96, 144x144, 192x192 dp)
- Place in `app/src/main/res/mipmap-*` folders

### 2.2 Screenshots
Take screenshots for Google Play listing:
- **Phone screenshots**: 320dp-3840dp (portrait/landscape)
- **7-inch tablets**: 320dp-3840dp
- **10-inch tablets**: 320dp-3840dp
- **TV screenshots**: 1920x1080 or 3840x2160

### 2.3 Feature Graphic
- Create a 1024x500 px promotional image
- Showcases your app's main functionality

### 2.4 App Description
**Short Description** (80 characters):
"Professional digital signage solution for Android TV displays"

**Full Description**:
```
Transform your Android TV into a professional digital signage display with our comprehensive solution.

FEATURES:
✓ Remote content management
✓ Support for images and videos
✓ Automatic content refresh
✓ Kiosk mode for unattended operation
✓ Real-time device monitoring
✓ QR code activation
✓ Centralized dashboard control

PERFECT FOR:
• Retail stores and restaurants
• Corporate offices and lobbies
• Educational institutions
• Healthcare facilities
• Hotels and hospitality

REQUIREMENTS:
• Android TV device (Android 5.0+)
• Network connection
• Digital Signage server (contact support)

SETUP:
1. Install app on your Android TV
2. Configure server connection
3. Activate device using QR code
4. Start displaying content remotely

Professional support available for enterprise deployments.
Contact: support@yourcompany.com
```

## Step 3: Google Play Console Setup

### 3.1 Create New App
1. Go to [Google Play Console](https://play.google.com/console)
2. Click "Create app"
3. Fill in app details:
   - **App name**: "Digital Signage TV"
   - **Default language**: English (US)
   - **App type**: App
   - **Category**: Business
   - **Target audience**: Everyone

### 3.2 App Content
1. **Content rating**: Complete questionnaire (likely "Everyone")
2. **Target audience**: 18+ (business use)
3. **Data safety**: Declare data collection practices
4. **Government apps**: No (unless applicable)

### 3.3 Store Listing
1. **App details**:
   - App name: "Digital Signage TV"
   - Short description: [Use above]
   - Full description: [Use above]

2. **Graphics**:
   - App icon: Upload 512x512 PNG
   - Feature graphic: Upload 1024x500 PNG
   - Screenshots: Upload for TV category

3. **Categorization**:
   - Category: Business
   - Tags: digital signage, tv display, kiosk

## Step 4: Upload APK/Bundle

### 4.1 Create App Bundle (Recommended)
```bash
cd c:\DisplayAdsAPI\AndroidTV
./gradlew bundleRelease
```

### 4.2 Upload to Play Console
1. Go to "Release" → "Production"
2. Click "Create new release"
3. Upload your AAB file (app-release.aab)
4. Add release notes:
```
Initial release of Digital Signage TV app.
Features:
- Remote content management
- Support for images and videos
- Kiosk mode operation
- Device monitoring and heartbeat
- QR code activation
```

## Step 5: Review and Publish

### 5.1 Pre-launch Report
- Google Play will test your app automatically
- Review any issues found
- Fix critical issues before publishing

### 5.2 Final Review
1. Check all sections are complete (green checkmarks)
2. Review store listing preview
3. Ensure content policy compliance

### 5.3 Publish
1. Click "Send to review"
2. Google review process takes 1-7 days
3. You'll receive email notification when approved

## Step 6: Post-Publication

### 6.1 Monitor Reviews
- Respond to user reviews
- Address common issues in updates

### 6.2 Analytics
- Monitor installation metrics
- Track user engagement
- Plan feature updates

### 6.3 Updates
- Release regular updates
- Increment version codes
- Provide clear release notes

## Troubleshooting Common Issues

### Upload Issues
- **APK signature**: Ensure consistent signing key
- **Version conflicts**: Increment version code
- **Permissions**: Review dangerous permissions

### Review Rejections
- **Metadata policy**: Ensure accurate descriptions
- **Content policy**: Remove any prohibited content
- **Target API**: Meet minimum requirements

### Device Compatibility
- **TV compatibility**: Test on various Android TV devices
- **API levels**: Support minimum Android 5.0 (API 21)
- **Hardware features**: Declare required features properly

## Support and Resources

- [Google Play Console Help](https://support.google.com/googleplay/android-developer/)
- [Android TV Development Guide](https://developer.android.com/tv)
- [Play Store Publishing Checklist](https://developer.android.com/distribute/best-practices/launch/launch-checklist)

## Contact
For technical support with this app:
- Email: support@yourcompany.com
- Documentation: [Link to your docs]
