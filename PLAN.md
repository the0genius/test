# NutriScan Implementation Plan

## 1. Project Bootstrap
- Initialize an Expo Router TypeScript app and set up the repository structure from the spec.
- Install required dependencies (Expo modules, Firebase, NativeWind, Zustand, React Query, Lottie).
- Configure app.json, tsconfig, babel, and tailwind/nativewind settings.

## 2. Design Tokens & Theming
- Implement `constants/theme.ts` with the color palette, typography scale, spacing, radius, and shadows.
- Add `constants/animations.ts` for global animation configuration.
- Create a basic typography component or theme provider if needed.

## 3. Navigation & Layout
- Configure root `_layout.tsx` and tab layout for Home, History, Favorites, Profile.
- Set up modal routes for product details, contribution flow, and settings.
- Provide auth stack for welcome/login/register flows.

## 4. Core UI Components
- Build reusable UI elements (Button, Card, Input, Badge, Progress indicators, BottomSheet, Toast, Skeleton).
- Provide common state components (Loading, Error, Empty).
- Add animation helpers and GlowEffect.

## 5. Scanner Experience
- Implement `BarcodeScanner` with Expo Camera/Barcode modules.
- Create `ScanOverlay`, `ScanAnimation`, and `TorchButton`.
- Add recent scans carousel and scan feedback (haptics, animations).
- Implement `useBarcodeScan` logic: cache → API → Firestore → not-found flow.

## 6. Product Detail Modal
- Build health score visualization with circular progress and animated number.
- Implement Quick Facts, Nutrition Facts accordion, Ingredients, and Alternatives.
- Add save/share actions and ensure accessibility.

## 7. Contribution Flow
- Create multi-step photo capture flow and progress indicator.
- Implement OCR pipeline with Cloud Vision via Cloud Functions.
- Build processing and success screens with Lottie animations.
- Add offline queue for pending contributions.

## 8. Data & Services
- Implement Open Food Facts API client and Firebase config.
- Build SQLite schema and cache/sync strategies.
- Add utilities for health score calculation and nutrition parsing.

## 9. User Features
- Implement authentication, profile, settings, and preferences.
- Build history and favorites with search, filters, and pagination.
- Add analytics tracking for key events.

## 10. Quality & Release
- Add tests and linting checks.
- Validate performance targets, error states, and offline behavior.
- Prepare release assets (icons, splash, localization scaffolding).
