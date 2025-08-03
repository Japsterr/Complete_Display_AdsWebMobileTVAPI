# 🛠️ Android Studio Setup Checklist

## 📥 Installation Steps

### 1. Download Android Studio
- [x] Go to https://developer.android.com/studio
- [ ] Download Windows installer (.exe)
- [ ] Wait for ~1GB download to complete

### 2. Run the Installer
- [ ] Run the downloaded .exe file as Administrator
- [ ] Choose "Standard" installation type
- [ ] Accept all default settings
- [ ] Let it download additional components (~2-3GB more)

### 3. Initial Android Studio Setup
- [ ] Open Android Studio
- [ ] Complete the setup wizard
- [ ] Install Android SDK (API level 33 or 34)
- [ ] Install Android Virtual Device (AVD) if you want emulator

### 4. Configure Environment Variables
- [ ] Add Android SDK to PATH
- [ ] Set ANDROID_HOME environment variable

### 5. Test Installation
- [ ] Run `adb version` in terminal
- [ ] Should show Android Debug Bridge version

## 🎯 What We're Installing

### Android Studio Components:
- **Android SDK**: Tools to build Android apps
- **ADB (Android Debug Bridge)**: Connect to devices/emulators
- **Build Tools**: Compile and package apps
- **Platform Tools**: Essential development utilities

### Why We Need This:
- **React Native** compiles to native Android code
- **Android SDK** builds the APK file
- **ADB** installs and runs the app on devices
- **Metro Bundler** serves JavaScript to the app

## 📱 After Installation

### Test Your Setup:
```bash
# These should all work:
adb version
npx react-native --version
cd C:\DisplayAdsAPI\MobileClient\DisplayAdsManager
npm install
npx react-native run-android
```

### Connect Your Phone:
1. Enable "Developer Options" on Android phone
2. Enable "USB Debugging" 
3. Connect phone via USB
4. Run `adb devices` to see connected devices

## 🚀 Expected Timeline
- **Download**: 10-15 minutes (depending on internet)
- **Installation**: 15-20 minutes
- **Initial setup**: 5-10 minutes
- **Total**: ~45 minutes

## 🎯 End Goal
After this setup, you'll be able to:
- Build real Android apps
- Test on your phone or emulator
- Publish to Google Play Store
- Develop React Native apps in VS Code

## ❓ Need Help?
If you get stuck at any step, just ask! This is a one-time setup that opens up native mobile development.
