# DisplayAds — Mobile & TV (consolidated)

This file documents the mobile manager app (React Native) and Android TV app.

Mobile quick start
- cd MobileClient/DisplayAdsManager/DisplayAdsNative
- npm install
- npm run android (or assembleRelease)

TV quick start
- Android TV app lives in `AndroidTV/` — build with Gradle and install the release APK.
- For quick testing use the `tv-simulator.html` in the repo.

Activation flow
- TV requests an activation code from the API and shows it as a QR.
- Mobile scans the QR and posts to /api/v1/devices/activate/ to assign the device.

Notes
- APKs and build artifacts are not stored in the repository. Build locally to produce signed APK bundles.
