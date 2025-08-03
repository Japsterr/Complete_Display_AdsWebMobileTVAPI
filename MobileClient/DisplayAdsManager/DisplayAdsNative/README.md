# DisplayAds Mobile Manager

React Native mobile application for managing digital signage campaigns, media, and displays.

## 📱 Features

### Complete Dashboard Integration
- **Real-time Statistics** - Campaign, media, and display counts
- **Campaign Management** - View campaigns with status badges
- **Media Library** - Browse uploaded files with metadata
- **Display Monitoring** - Check device online/offline status
- **Analytics Dashboard** - Performance metrics and insights

### Authentication & Security
- **JWT Token Authentication** - Secure login with Django backend
- **Persistent Sessions** - AsyncStorage for token persistence
- **Network Detection** - Automatic API endpoint testing
- **Secure Logout** - Complete token cleanup

### Professional UI/UX
- **Blue/Purple Branding** - Consistent with web platform
- **Material Design** - Clean, modern interface
- **Status Badges** - Visual campaign and display indicators
- **Pull-to-Refresh** - Live data synchronization
- **Loading States** - Professional user feedback

## 🏗️ Technical Stack

- **React Native**: 0.75.4
- **TypeScript**: Full type safety
- **AsyncStorage**: Token persistence
- **Axios**: HTTP client for API calls
- **Android SDK**: Native Android features

## 🚀 Installation

### Prerequisites
- Node.js 22.14.0+
- Android Studio with SDK
- Android device or emulator

### Build & Install
```bash
cd MobileClient/DisplayAdsManager/DisplayAdsNative
npm install
npm install @react-native-async-storage/async-storage
.\android\gradlew.bat -p android assembleRelease

# Install on device
adb install android/app/build/outputs/apk/release/app-release.apk
```

## 🔐 Authentication

### Login Credentials
- **Email**: Your Django user email
- **Password**: Your Django user password
- **API Endpoint**: Auto-detected (192.168.3.73:8000)

### API Integration
- **Base URL**: `http://192.168.3.73:8000/api/v1`
- **Health Check**: `/health/`
- **Login**: `/login/`
- **Campaigns**: `/campaigns/`
- **Media**: `/media/`
- **Displays**: `/displays/`

## Step 3: Modify your app

Now that you have successfully run the app, let's make changes!

Open `App.tsx` in your text editor of choice and make some changes. When you save, your app will automatically update and reflect these changes — this is powered by [Fast Refresh](https://reactnative.dev/docs/fast-refresh).

When you want to forcefully reload, for example to reset the state of your app, you can perform a full reload:

- **Android**: Press the <kbd>R</kbd> key twice or select **"Reload"** from the **Dev Menu**, accessed via <kbd>Ctrl</kbd> + <kbd>M</kbd> (Windows/Linux) or <kbd>Cmd ⌘</kbd> + <kbd>M</kbd> (macOS).
- **iOS**: Press <kbd>R</kbd> in iOS Simulator.

## Congratulations! :tada:

You've successfully run and modified your React Native App. :partying_face:

### Now what?

- If you want to add this new React Native code to an existing application, check out the [Integration guide](https://reactnative.dev/docs/integration-with-existing-apps).
- If you're curious to learn more about React Native, check out the [docs](https://reactnative.dev/docs/getting-started).

# Troubleshooting

If you're having issues getting the above steps to work, see the [Troubleshooting](https://reactnative.dev/docs/troubleshooting) page.

# Learn More

To learn more about React Native, take a look at the following resources:

- [React Native Website](https://reactnative.dev) - learn more about React Native.
- [Getting Started](https://reactnative.dev/docs/environment-setup) - an **overview** of React Native and how setup your environment.
- [Learn the Basics](https://reactnative.dev/docs/getting-started) - a **guided tour** of the React Native **basics**.
- [Blog](https://reactnative.dev/blog) - read the latest official React Native **Blog** posts.
- [`@facebook/react-native`](https://github.com/facebook/react-native) - the Open Source; GitHub **repository** for React Native.
