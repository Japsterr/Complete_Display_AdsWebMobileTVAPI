# MobileClient

This folder contains the mobile applications for DisplayAds.

Paths
- Phone (React Native - canonical): MobileClient/DisplayAdsManager/DisplayAdsNative/
- Android TV (native): AndroidTV/
- Legacy / experimental TV apps: Mobile/DigitalSignageTV/

Which to use
- For phone development and contributions, use the React Native app at the "DisplayAdsNative" path above. This is the active phone application and has the full src/ tree, package.json, and platform folders (android/, ios/).
- For Android TV specific work, use the `AndroidTV/` folder which contains native TV app code and publishing notes.
- The `Mobile/DigitalSignageTV/` folder contains older experimental TV signage projects and staged READMEs—these are archived; see docs/archived_markdown/ for preserved original docs.

Quick start (phone - React Native)
1. Install Node.js 18+ and Yarn or npm.
2. From the app root:
   - npm install
   - npm run start        # start Metro bundler
   - npm run android      # build & run on attached Android device or emulator
   - npm run ios          # build & run on iOS (macOS only)

Notes
- The React Native app targets React Native 0.75.x. Use Node >=18.
- For simulator vs device: emulators/simulators behave like physical devices but require platform tooling (Android Studio AVD, Xcode simulator).
- Keep mobile-specific secrets (API endpoints, tokens) out of repo. Use environment variables or a secured secret store when possible.

Where to find help
- See MobileClient/DisplayAdsManager/DisplayAdsNative/README.md for app-specific notes.
- See docs/archived_markdown/ for historical READMEs and archived docs.
