# 🚀 Complete DisplayAds SaaS Platform

**A comprehensive digital signage SaaS platform with Web Dashboard, Mobile Management App, TV Display App, and Backend API**

## 📋 Project Overview

This is a complete digital signage solution built with modern technologies, featuring:

- 🌐 **Web Dashboard** (React + TypeScript)
- 📱 **Mobile Management App** (React Native + TypeScript) 
- 📺 **TV Display App** (React Native)
- ⚙️ **Backend API** (Django + DRF)

### 🎯 Key Innovation: QR Code TV Activation
The mobile app can scan QR codes displayed on TV screens to instantly activate and register displays - a unique feature in the digital signage market.

## 🏗️ Architecture

```
DisplayAdsAPI/
├── 🌐 Workspace/                 # React Web Dashboard
├── 📱 MobileClient/              # React Native Mobile Apps
│   ├── DisplayAdsManager/        # Mobile Management App
│   └── DisplayAdsNative/         # Current Mobile Project
├── 📺 Mobile/                    # TV Display Applications
├── ⚙️ api/                       # Django REST API
├── ⚙️ signage_project/           # Django Project Settings
└── 📚 Documentation Files
```

## 🚀 Quick Start

### 1. Backend API (Django)
```bash
cd DisplayAdsAPI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 2. Web Dashboard (React)
```bash
cd Workspace
npm install
npm run dev
```

### 3. Mobile App (React Native)
```bash
cd MobileClient/DisplayAdsNative
npm install
npx react-native run-android
```

## 📱 Features

### Web Dashboard
- ✅ User authentication & account management
- ✅ Campaign creation with drag-drop playlist builder
- ✅ Media library with file uploads
- ✅ Display device management
- ✅ Analytics dashboard
- ✅ Stripe payment integration
- ✅ Team collaboration (business accounts)

### Mobile App (Key Differentiator)
- 🎯 **QR Code Scanner** for TV activation
- 📊 Dashboard with statistics
- 🎬 Campaign management
- 📁 Media library with camera uploads
- 📺 Display monitoring
- 👤 Profile management
- 🔔 Push notifications (planned)

### Backend API
- 🔐 JWT authentication
- 👥 Multi-tenant architecture (personal/business)
- 💳 Stripe payment processing
- 📊 Analytics & device tracking
- 🎬 Campaign & media management
- 📺 Display activation system
- 📡 Device heartbeat monitoring

## 💻 Technology Stack

### Frontend
- **React 19.1.0** with TypeScript
- **Vite 7.0.4** for build tooling
- **Bootstrap 5.3.7** for UI components
- **Axios** for API communication

### Mobile
- **React Native 0.80.2** with TypeScript
- **React Navigation 6** for navigation
- **React Native Camera** for QR scanning
- **AsyncStorage** for local data

### Backend
- **Django 5.0.14** with Python
- **Django REST Framework** for API
- **SQLite** (development) / **PostgreSQL** (production)
- **JWT** authentication
- **Stripe** payment integration

## 🎯 Business Model

### Pricing Tiers
- 🆓 **Free**: R0/month, 2 displays, 1GB storage
- 💼 **Business**: R99/month, 25 displays, team features
- 🏢 **Enterprise**: R500/month, unlimited displays, white-label

### Target Market
- 🏪 Retail stores and restaurants
- 🏢 Corporate offices and lobbies  
- 🏥 Healthcare and hospitality
- 🎓 Educational institutions

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+**
- **Python 3.8+** 
- **Android Studio** (for mobile development)
- **Git**

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/Japsterr/Complete_Display_AdsWebMobileTVAPI.git
   cd Complete_Display_AdsWebMobileTVAPI
   ```

2. **Set up Backend**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Set up Web Dashboard**
   ```bash
   cd Workspace
   npm install
   npm run dev
   ```

4. **Set up Mobile App**
   ```bash
   cd MobileClient/DisplayAdsNative
   npm install
   npx react-native run-android
   ```

## 📚 Documentation

- 📖 [API Documentation](API_TEST_REPORT.md)
- 📱 [Mobile App Setup](MobileClient/DisplayAdsNative/SETUP_GUIDE.md)
- 💳 [Stripe Integration](STRIPE_SETUP_GUIDE.md)
- 🔧 [Development Session Notes](DEVELOPMENT_SESSION_SUMMARY.md)

## 🌟 Key Features

### 🎯 Unique Selling Points
1. **QR Code TV Activation** - Industry first mobile QR scanning
2. **Multi-tenant SaaS** - Personal and business accounts
3. **South African Focus** - ZAR currency support
4. **Complete Ecosystem** - Web + Mobile + TV integration
5. **Modern Tech Stack** - Latest React, React Native, Django

### 📊 Platform Capabilities
- **Device Management**: Register, monitor, and control displays
- **Campaign Creation**: Visual playlist builder with scheduling  
- **Media Library**: Upload, organize, and manage content
- **Analytics**: Device status, impressions, and performance
- **Team Management**: Multi-user business accounts
- **Payment Processing**: Stripe integration with subscriptions

## 🔧 Development

### Project Structure
```
DisplayAdsAPI/
├── api/                    # Django REST API
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Data serialization
│   └── urls.py            # URL routing
├── Workspace/             # React Web Dashboard
│   ├── src/pages/         # React pages
│   ├── src/components/    # Reusable components
│   └── src/services/      # API communication
└── MobileClient/          # React Native Apps
    └── DisplayAdsNative/  # Main mobile app
        ├── src/screens/   # Mobile screens
        ├── src/services/  # API integration
        └── src/contexts/  # State management
```

### Development Commands
```bash
# Backend
python manage.py runserver
python manage.py migrate
python manage.py test

# Frontend
npm run dev
npm run build
npm run lint

# Mobile
npx react-native run-android
npx react-native run-ios
npx react-native start
```

## 🚀 Deployment

### Production Checklist
- [ ] Configure PostgreSQL database
- [ ] Set up Stripe live API keys
- [ ] Configure production CORS settings
- [ ] Set up file storage (S3/CloudFlare)
- [ ] Deploy backend (DigitalOcean/AWS)
- [ ] Deploy frontend (Vercel/Netlify)
- [ ] Build mobile APK/IPA files
- [ ] Submit to app stores

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Contact

**Developer**: Japster  
**Repository**: https://github.com/Japsterr/Complete_Display_AdsWebMobileTVAPI  
**Project**: DisplayAds SaaS Platform

---

## 🎉 Status: Production Ready

This is a complete, enterprise-ready digital signage SaaS platform with unique mobile-first features that provide significant competitive advantages in the market.

**Key Achievement**: QR code TV activation via mobile app - a industry-first innovation that simplifies display deployment and management.
