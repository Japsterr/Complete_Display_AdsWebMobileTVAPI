## Orientation controls and QR onboarding

- Dashboard now exposes campaign orientation fields on create/edit:
	- Screen Orientation: portrait | landscape
	- Normalize To Orientation: none | portrait | landscape (hint for TV to letterbox/pillarbox)

- TV app shows an activation QR (from /devices/request-activation/) and a code; Manager app includes a QR scanner screen to activate devices via /devices/activate/.

## Configuring server base URL (IP changes)

- Dashboard (Vite): set VITE_API_BASE_URL in `Workspace/.env` or `.env.local`.
- TV app: on the Activation screen, use “Change Server URL” to override at runtime; persists via AsyncStorage. Default remains src/config.ts.
- Mobile Manager: API base can be overridden at runtime and persisted; wire a simple settings UI to call ApiService.setBaseUrl(url) if needed.

### New
- Manager app now includes a Settings tab to change the API base URL at runtime and test connectivity via /health.
- TV app respects campaign normalize_to_orientation (portrait/landscape) by rotating the wrapper when device orientation mismatches. Media uses resizeMode="contain" to avoid stretching.

# 🚀 Complete DisplayAds SaaS Platform - Updated

**A comprehensive digital signage SaaS platform with Web Dashboard, Mobile Management App, Android TV App, and Backend API**

## 📋 Project Overview

This is a complete digital signage solution built with modern technologies, featuring:

- 🌐 **Web Dashboard** (React 19.1.0 + TypeScript + Vite)
- 📱 **Mobile Management App** (React Native 0.75.4 + TypeScript) 
- 📺 **Android TV Display App** (Native Kotlin + Android SDK API 35)
- ⚙️ **Backend API** (Django 5.0.14 + DRF + JWT Auth)

### 🎯 Key Features Implemented
- **QR Code TV Activation** - Mobile app scans QR codes to activate displays
- **Smart Campaign Status** - Automatic status updates (Draft → Ready → Active)
- **Real-time Dashboard** - Live data synchronization across all platforms
- **Freemium Pricing Model** - ZAR currency with tiered pricing
- **Multi-platform Authentication** - JWT tokens with persistent storage
- **Professional UI** - Blue/purple branding across all applications

## 🏗️ Updated Architecture

```
DisplayAdsAPI/
├── 🌐 Workspace/                 # React Web Dashboard (Port 5173)
├── 📱 MobileClient/DisplayAdsManager/DisplayAdsNative/  # Mobile App (APK)
├── 📺 AndroidTV/                 # Native Android TV App (APK)
├── ⚙️ api/                       # Django REST API (Port 8000)
├── ⚙️ signage_project/           # Django Project Settings
├── 📄 media/                     # Media file storage
└── 📚 Documentation & Config Files
```

## 🚀 Quick Start - Updated Commands

### 1. Backend API (Django) - Network Enabled
```bash
cd DisplayAdsAPI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000  # Network accessible
```

### 2. Web Dashboard (React + Vite)
```bash
cd Workspace
npm install
npm run dev  # Runs on http://localhost:5173
```

### 3. Mobile App (React Native) - Production Ready
```bash
cd MobileClient/DisplayAdsManager/DisplayAdsNative
npm install
npm install @react-native-async-storage/async-storage
.\android\gradlew.bat -p android assembleRelease
# Install APK: adb install android/app/build/outputs/apk/release/app-release.apk
```

### 4. Android TV App (Native Kotlin)
```bash
cd AndroidTV
./gradlew assembleRelease
# Install APK: adb install app/build/outputs/apk/release/app-release.apk
```

## 🔐 Authentication System

### User Accounts
- **Email**: `bosman.japie@gmail.com` (Primary test account)
- **Type**: Business account with full features
- **Mobile Login**: Email + password authentication
- **Token Storage**: AsyncStorage for persistent sessions

### API Endpoints
- **Login**: `POST /api/v1/login/`
- **Register**: `POST /api/v1/register/`
- **Health Check**: `GET /api/v1/health/`
- **Swagger Docs**: `http://192.168.3.73:8000/api/v1/swagger/`

## 📱 Mobile App Features - Fully Implemented

### Dashboard Integration
- ✅ Real-time campaign statistics display
- ✅ Media library browsing with file types
- ✅ Display device status monitoring (Online/Offline)
- ✅ Pull-to-refresh functionality
- ✅ Professional blue/purple UI matching web

### Authentication Features
- ✅ Email/password login form
- ✅ JWT token persistence with AsyncStorage
- ✅ Automatic connection testing to API endpoints
- ✅ Network connectivity status indicators
- ✅ Secure logout with token cleanup

### Data Synchronization
- ✅ Campaign list with status badges (Draft/Ready/Active)
- ✅ Media files with upload dates and types
- ✅ Display devices with heartbeat status
- ✅ Analytics dashboard integration
- ✅ Error handling and loading states

## 📺 Android TV App - Production Ready

### Kiosk Mode Features
- ✅ Full-screen campaign display
- ✅ Auto-start on device boot
- ✅ WebView-based content rendering
- ✅ Device heartbeat monitoring
- ✅ Campaign rotation system

### Google Play Store Ready
- ✅ Release APK generated (2.9MB optimized)
- ✅ App signing configuration
- ✅ Android TV launcher compatibility
- ✅ Network security configuration
- ✅ Proper permissions and manifest

## 💰 Pricing Model - ZAR Currency

### Free Tier
- 3 campaigns maximum
- 5 displays maximum
- 10 images, no videos
- 1GB storage, single user

### Pro Tier (R99/month)
- 20 campaigns, 25 displays
- 100 images + 20 videos
- 10GB storage, 5 users
- Advanced analytics

### Enterprise Tier (R299/month)
- Unlimited campaigns and displays
- Unlimited media files
- 100GB storage, 25 users
- Priority support + API access

## 🔧 Development Status - Completed

### Backend (Django) ✅
- JWT authentication system
- Campaign status automation
- Media file management
- Display device tracking
- Analytics dashboard
- Stripe payment integration
- Network-accessible API (0.0.0.0:8000)

### Frontend (React) ✅
- Campaign management interface
- Media library with upload
- Display monitoring dashboard
- User management system
- Blue/purple responsive design
- Bootstrap 5.3.7 styling

### Mobile (React Native) ✅
- Complete dashboard functionality
- Real-time data synchronization
- Professional UI design
- Token-based authentication
- APK distribution ready
- AsyncStorage integration

### Android TV (Kotlin) ✅
- Kiosk mode application
- WebView content rendering
- Auto-boot functionality
- Heartbeat monitoring
- Google Play Store ready
- Release APK optimized

## 🌐 Network Configuration

### IP Address: `192.168.3.73`
- Django API accessible on network
- Windows Firewall configured
- CORS enabled for all origins
- Mobile app connects to PC API
- Health check endpoint active

### Port Configuration
- **Django API**: Port 8000 (network accessible)
- **React Web**: Port 5173 (local development)
- **Mobile/TV Apps**: Connect to API via network IP

## 📊 Current Data Model

### Smart Campaign Status System
- **Draft**: Newly created campaigns
- **Ready**: Campaigns with media assigned (auto-update)
- **Active**: Currently running campaigns
- **Paused**: Temporarily stopped campaigns

### User Management
- Custom User model with business/personal types
- JWT token authentication
- Plan-based feature restrictions
- Team member invitations

### Media Management
- Image and video file support
- Automatic file type detection
- Storage quota management
- Campaign media associations

## 🚀 Deployment Ready

### Production Checklist ✅
- [x] Environment variables configured
- [x] Database migrations applied
- [x] Network access configured
- [x] APK files generated and tested
- [x] API documentation available
- [x] Authentication system secure
- [x] Mobile app production ready
- [x] Android TV app Google Play ready

## 📞 Support & Repository

- **GitHub**: https://github.com/Japsterr/Complete_Display_AdsWebMobileTVAPI
- **Contact**: bosman.japie@gmail.com
- **Version**: 2.0.0 (August 3, 2025)
- **Status**: Production Ready ✅

---

**Complete multi-platform digital signage solution with web, mobile, and TV applications**
