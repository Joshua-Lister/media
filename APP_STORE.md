# Mobile App Store Deployment Guide

Complete guide for deploying the Citizen Journalism Platform to iOS App Store and Google Play Store.

## Table of Contents

1. [Overview](#overview)
2. [Option 1: Capacitor (Recommended)](#option-1-capacitor-recommended)
3. [Option 2: Progressive Web App (PWA)](#option-2-progressive-web-app-pwa)
4. [Option 3: React Native](#option-3-react-native)
5. [Comparison Matrix](#comparison-matrix)

---

## Overview

You have three main options for mobile deployment:

| Option | App Store | Google Play | Development Time | Code Reuse |
|--------|-----------|-------------|------------------|------------|
| **Capacitor** | ✅ Yes | ✅ Yes | 1-2 weeks | ~95% |
| **PWA** | ❌ No | ⚠️ Limited | 2-3 days | 100% |
| **React Native** | ✅ Yes | ✅ Yes | 2-3 months | ~30% |

---

## Option 1: Capacitor (Recommended)

**Best for:** Converting your React web app to native iOS/Android apps with minimal changes.

### What is Capacitor?

Capacitor wraps your React web app in a native container, giving you access to native device features while keeping your existing codebase.

### Pros
- ✅ Use 95% of existing React code
- ✅ Submit to both App Store and Play Store
- ✅ Access native features (camera, notifications, biometrics)
- ✅ Faster development than React Native
- ✅ Maintained by Ionic team (well-supported)

### Cons
- ❌ Slightly larger app size (~15-20MB base)
- ❌ Performance not quite as good as pure native
- ❌ WebView rendering (good enough for most apps)

---

### Step-by-Step: iOS App Store Deployment

#### Prerequisites

- **Mac computer** with macOS (required for iOS development)
- **Xcode** 14+ installed (free from App Store)
- **Apple Developer Account** ($99/year)
- **CocoaPods** installed: `sudo gem install cocoapods`
- **Node.js** 18+ and npm

#### Step 1: Install Capacitor

```bash
cd /home/joshua/personal/media/frontend

# Install Capacitor
npm install @capacitor/core @capacitor/cli
npm install @capacitor/ios @capacitor/android

# Install useful plugins
npm install @capacitor/camera @capacitor/push-notifications @capacitor/app @capacitor/haptics @capacitor/status-bar
```

#### Step 2: Initialize Capacitor

```bash
npx cap init

# You'll be prompted for:
# App name: Citizen Journalism
# App ID: com.yourdomain.citizenjournalism (reverse domain notation)
# Web asset directory: build
```

This creates `capacitor.config.ts`:

```typescript
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.yourdomain.citizenjournalism',
  appName: 'Citizen Journalism',
  webDir: 'build',
  server: {
    androidScheme: 'https',
    // For development, use your local backend
    // url: 'http://192.168.1.100:3000',
    // cleartext: true
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert']
    },
    StatusBar: {
      style: 'light',
      backgroundColor: '#0ea5e9'
    }
  }
};

export default config;
```

#### Step 3: Update API Configuration for Mobile

Create `frontend/src/config/api.ts`:

```typescript
import { Capacitor } from '@capacitor/core';

const getApiUrl = () => {
  // Use different API URLs based on platform
  if (Capacitor.isNativePlatform()) {
    // Production API for native apps
    return 'https://api.yourdomain.com/api/v1';
  } else {
    // Development or web
    return process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
  }
};

export const API_URL = getApiUrl();
```

Update your axios configuration to use this:

```typescript
// frontend/src/api/client.ts
import axios from 'axios';
import { API_URL } from '../config/api';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
```

#### Step 4: Build React App

```bash
# Build for production
npm run build

# Copy web assets to native project
npx cap add ios
npx cap sync ios
```

#### Step 5: Configure iOS Project

```bash
# Open Xcode
npx cap open ios
```

In Xcode:

1. **Update Bundle Identifier:**
   - Select project in left sidebar
   - Under "General" tab
   - Set Bundle Identifier to `com.yourdomain.citizenjournalism`

2. **Set App Icons:**
   - Create app icons using https://appicon.co (upload 1024x1024 image)
   - Download iOS icons
   - Drag into `App/Assets.xcassets/AppIcon.appiconset/`

3. **Set Display Name:**
   - Change "Display Name" to "Citizen Journalism"

4. **Configure Capabilities:**
   - Click "Signing & Capabilities" tab
   - Enable "Push Notifications" (if using)
   - Enable "Background Modes" → check "Remote notifications"

5. **Set Deployment Target:**
   - Set to iOS 13.0 or higher

6. **Update Info.plist:**
   Add required permissions:
   ```xml
   <key>NSCameraUsageDescription</key>
   <string>Take photos for article submissions</string>
   <key>NSPhotoLibraryUsageDescription</key>
   <string>Choose photos for article submissions</string>
   <key>NSMicrophoneUsageDescription</key>
   <string>Record audio for articles</string>
   ```

#### Step 6: Test on Simulator

```bash
# Run on iOS simulator
npx cap run ios
```

Or in Xcode: Click the ▶️ Play button

#### Step 7: Sign App with Developer Account

1. In Xcode, select your project
2. Under "Signing & Capabilities"
3. Check "Automatically manage signing"
4. Select your Team (Apple Developer Account)
5. Xcode will create provisioning profiles automatically

#### Step 8: Create App in App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" → "+" → "New App"
3. Fill in:
   - Platform: iOS
   - Name: Citizen Journalism
   - Primary Language: English
   - Bundle ID: com.yourdomain.citizenjournalism
   - SKU: citizenjournalism (unique identifier)
4. Click "Create"

#### Step 9: Prepare App Store Listing

You'll need:

- **App Icon:** 1024x1024px PNG (no transparency)
- **Screenshots:**
  - iPhone 6.7" (1290x2796): 3-10 screenshots
  - iPhone 6.5" (1284x2778): 3-10 screenshots
  - iPad Pro 12.9" (2048x2732): 3-10 screenshots (if supporting iPad)
- **App Preview Videos:** Optional but recommended
- **Description:** Up to 4000 characters
- **Keywords:** Up to 100 characters (comma-separated)
- **Support URL:** https://yourdomain.com/support
- **Marketing URL:** https://yourdomain.com
- **Privacy Policy URL:** https://yourdomain.com/privacy (REQUIRED)

**Sample Description:**

```
Citizen Journalism - Empower Your Voice

The Citizen Journalism Platform gives everyday people the power to report on stories that matter to them. Vote on topics you care about, read in-depth articles from community writers, and engage with quality journalism driven by public interest.

FEATURES:
• Vote on Topics: Decide what stories get covered
• Quality Ratings: Multi-criteria rating system (depth, bias, accuracy)
• Expert Writers: Connect with verified journalists and writers
• Community Driven: News that matters to your community
• Ad-Free Reading: Focus on content, not ads
• Offline Reading: Save articles for later

Perfect for readers who want:
✓ Unbiased news coverage
✓ Local community stories
✓ In-depth investigative journalism
✓ Transparent reporting

Join thousands of readers making journalism better.
```

#### Step 10: Archive and Upload to App Store

1. In Xcode, select "Any iOS Device (arm64)" as target
2. Product → Archive (wait 5-10 minutes)
3. When done, Organizer window opens
4. Click "Distribute App"
5. Select "App Store Connect"
6. Click "Upload"
7. Wait for processing (30 min - 2 hours)

#### Step 11: Submit for Review

1. Return to App Store Connect
2. Select your app version
3. Fill in "What's New in This Version"
4. Add screenshots and metadata
5. Set pricing (Free or Paid)
6. Select age rating
7. Submit for Review

**Review typically takes 1-3 days**

#### Step 12: Handle Review Feedback

Apple may request:
- Login credentials for test account (provide demo credentials)
- Explanation of features
- Privacy policy updates
- Bug fixes

Once approved, your app is live! 🎉

---

### Step-by-Step: Google Play Store Deployment

#### Prerequisites

- **Google Play Developer Account** ($25 one-time fee)
- **Android Studio** installed
- **Java JDK** 11+ installed

#### Step 1: Add Android Platform

```bash
cd /home/joshua/personal/media/frontend

# Add Android platform
npx cap add android

# Sync
npx cap sync android

# Open Android Studio
npx cap open android
```

#### Step 2: Configure Android Project

In Android Studio:

1. **Update Package Name:**
   - Open `android/app/build.gradle`
   - Change `applicationId "com.yourdomain.citizenjournalism"`

2. **Update App Name:**
   - Edit `android/app/src/main/res/values/strings.xml`
   ```xml
   <string name="app_name">Citizen Journalism</string>
   ```

3. **Add Icons:**
   - Use https://romannurik.github.io/AndroidAssetStudio/icons-launcher.html
   - Upload 512x512 icon
   - Download and replace in `android/app/src/main/res/mipmap-*/`

4. **Update Version:**
   - In `android/app/build.gradle`:
   ```gradle
   versionCode 1
   versionName "1.0.0"
   ```

#### Step 3: Generate Signing Key

```bash
# Generate keystore
keytool -genkey -v -keystore citizen-journalism.keystore \
  -alias citizenjournalism -keyalg RSA -keysize 2048 -validity 10000

# You'll be prompted for:
# - Keystore password (SAVE THIS!)
# - Your name, organization, etc.
```

**IMPORTANT:** Store this keystore file securely! You cannot update your app without it.

#### Step 4: Configure Signing

Create `android/key.properties`:

```properties
storeFile=/path/to/citizen-journalism.keystore
storePassword=your_keystore_password
keyAlias=citizenjournalism
keyPassword=your_key_password
```

**Add to .gitignore:**
```bash
echo "android/key.properties" >> .gitignore
echo "*.keystore" >> .gitignore
```

Update `android/app/build.gradle`:

```gradle
// Add before android {}
def keystorePropertiesFile = rootProject.file("key.properties")
def keystoreProperties = new Properties()
keystoreProperties.load(new FileInputStream(keystorePropertiesFile))

android {
    ...
    signingConfigs {
        release {
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### Step 5: Build Release APK/AAB

```bash
cd android

# Build AAB (required for Play Store)
./gradlew bundleRelease

# Output: android/app/build/outputs/bundle/release/app-release.aab
```

#### Step 6: Create App in Play Console

1. Go to https://play.google.com/console
2. Click "Create app"
3. Fill in:
   - App name: Citizen Journalism
   - Default language: English
   - App or game: App
   - Free or paid: Free
4. Accept declarations
5. Click "Create app"

#### Step 7: Set Up Store Listing

1. **Main store listing:**
   - App name: Citizen Journalism
   - Short description: (80 chars) "Community-driven journalism platform. Vote on topics, rate articles."
   - Full description: (4000 chars) Same as iOS
   - App icon: 512x512px PNG
   - Feature graphic: 1024x500px JPG/PNG
   - Phone screenshots: 2-8 screenshots (16:9 or 9:16)
   - 7-inch tablet screenshots: Optional
   - 10-inch tablet screenshots: Optional

2. **Categorization:**
   - Category: News & Magazines
   - Tags: journalism, news, community

3. **Contact details:**
   - Email, phone, website

4. **Privacy Policy:**
   - URL to your privacy policy (REQUIRED)

#### Step 8: Content Rating

1. Fill out questionnaire
2. Typical ratings: E (Everyone) or T (Teen)
3. Save rating

#### Step 9: Upload AAB

1. Go to "Production" → "Create new release"
2. Upload `app-release.aab`
3. Set version name: 1.0.0
4. Add release notes
5. Save

#### Step 10: Review and Publish

1. Complete all sections (pricing, countries, content rating)
2. Submit for review
3. **Review takes 1-7 days**

Once approved, your app is live on Google Play! 🎉

---

## Option 2: Progressive Web App (PWA)

**Best for:** Letting users "install" your web app without App Store submission.

### Pros
- ✅ No App Store approval needed
- ✅ Instant updates (just deploy to web)
- ✅ Works on iOS and Android
- ✅ Same codebase as website
- ✅ Fastest to implement (2-3 days)

### Cons
- ❌ **Cannot be listed in App Store or Play Store**
- ❌ Limited offline capabilities on iOS
- ❌ No access to some native features (Bluetooth, NFC, etc.)
- ❌ Users must manually "Add to Home Screen"
- ❌ Less discoverable than app stores

### Implementation

#### Step 1: Create Web App Manifest

Create `frontend/public/manifest.json`:

```json
{
  "name": "Citizen Journalism Platform",
  "short_name": "Citizen News",
  "description": "Community-driven journalism platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0ea5e9",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

#### Step 2: Create Service Worker

Create `frontend/public/service-worker.js`:

```javascript
const CACHE_NAME = 'citizen-journalism-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
];

// Install service worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Fetch with network-first strategy
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// Clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

#### Step 3: Register Service Worker

Update `frontend/src/index.tsx`:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Register service worker
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('SW registered:', registration);
      })
      .catch((error) => {
        console.log('SW registration failed:', error);
      });
  });
}
```

#### Step 4: Add Install Prompt

Create `frontend/src/components/InstallPrompt.tsx`:

```typescript
import React, { useEffect, useState } from 'react';

const InstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      setShowPrompt(false);
    }
    setDeferredPrompt(null);
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm">
      <h3 className="font-bold mb-2">Install App</h3>
      <p className="text-sm text-gray-600 mb-3">
        Install Citizen Journalism for quick access and offline reading.
      </p>
      <div className="flex gap-2">
        <button onClick={handleInstall} className="btn btn-primary flex-1">
          Install
        </button>
        <button onClick={() => setShowPrompt(false)} className="btn btn-secondary">
          Later
        </button>
      </div>
    </div>
  );
};

export default InstallPrompt;
```

#### Step 5: Generate Icons

Use https://realfavicongenerator.net/ to generate all required icons.

#### Step 6: Deploy

Deploy to your production server. Users can now:

**On Android:**
1. Open site in Chrome
2. Tap menu → "Add to Home Screen"

**On iOS:**
1. Open site in Safari
2. Tap Share → "Add to Home Screen"

---

## Option 3: React Native

**Best for:** Maximum performance and full native experience (but requires complete rewrite).

### Overview

React Native requires rewriting your app using React Native components instead of HTML/CSS. This is a significant undertaking.

### Estimated Timeline
- **Setup:** 1 week
- **UI Conversion:** 4-6 weeks
- **API Integration:** 2 weeks
- **Testing & Polish:** 2-3 weeks
- **Total:** 2-3 months

### Pros
- ✅ Best performance (truly native)
- ✅ Full access to all native APIs
- ✅ Best user experience
- ✅ Shared logic between iOS/Android

### Cons
- ❌ Complete rewrite required
- ❌ Different component library (no HTML/CSS)
- ❌ Separate codebase from web
- ❌ More complex development
- ❌ Longer development time

### Quick Start (If Pursuing)

```bash
npx react-native init CitizenJournalism
cd CitizenJournalism

# Install navigation
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context

# Install other dependencies
npm install axios react-query zustand
```

**Not recommended unless you need absolute best performance or have specific native requirements.**

---

## Comparison Matrix

| Feature | Capacitor | PWA | React Native |
|---------|-----------|-----|--------------|
| **Development Time** | 1-2 weeks | 2-3 days | 2-3 months |
| **Code Reuse** | 95% | 100% | 30% |
| **App Store** | ✅ Yes | ❌ No | ✅ Yes |
| **Play Store** | ✅ Yes | ❌ No | ✅ Yes |
| **Offline Support** | ✅ Good | ⚠️ Limited | ✅ Excellent |
| **Performance** | ⚠️ Good | ⚠️ Good | ✅ Excellent |
| **Push Notifications** | ✅ Yes | ⚠️ Limited | ✅ Full |
| **Camera Access** | ✅ Yes | ⚠️ Limited | ✅ Full |
| **Biometric Auth** | ✅ Yes | ❌ No | ✅ Yes |
| **App Size** | ~20MB | N/A | ~15MB |
| **Update Speed** | Instant | Instant | App Store review |
| **Maintenance** | Low | Low | High |
| **Learning Curve** | Low | Very Low | High |
| **Cost** | $$ | $ | $$$$ |

---

## Recommendation

**For your Citizen Journalism Platform, I recommend Capacitor:**

1. ✅ Quick to implement (1-2 weeks)
2. ✅ Reuse 95% of existing React code
3. ✅ Submit to both App Store and Google Play
4. ✅ Access to native features (camera, push notifications)
5. ✅ Good performance for content-driven app
6. ✅ Easy to maintain

**Start with iOS first** (larger user base for news apps), then add Android.

**Total cost for mobile:**
- Apple Developer: $99/year
- Google Play: $25 one-time
- **Total: $124 first year, $99/year after**

---

## Next Steps

1. **Set up Capacitor** (follow iOS deployment steps above)
2. **Test on simulator** to ensure functionality
3. **Create App Store Connect listing** (screenshots, description)
4. **Submit for review**
5. **Add Android** after iOS approval
6. **Monitor crash reports** and user feedback

Need help with any step? Check the detailed instructions above or ask for clarification!
