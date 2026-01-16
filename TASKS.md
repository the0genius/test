# NutriScan Task List

## Phase 1: Foundation
- [ ] Initialize Expo project with TypeScript
- [ ] Set up folder structure per specification
- [ ] Configure Tailwind/NativeWind
- [ ] Install dependencies
- [ ] Set up Firebase project configuration
- [ ] Create design tokens and theme
- [ ] Build basic navigation structure (Expo Router)

## Phase 2: Core UI Components
- [ ] Build UI components in `components/ui`
  - [ ] Button
  - [ ] Card
  - [ ] Input
  - [ ] Badge
  - [ ] ProgressBar
  - [ ] CircularProgress
  - [ ] BottomSheet
  - [ ] Toast
  - [ ] Skeleton
  - [ ] AnimatedNumber
  - [ ] GlowEffect
- [ ] Create common states
  - [ ] LoadingState
  - [ ] ErrorState
  - [ ] EmptyState
- [ ] Set up Lottie animations
- [ ] Verify components on iOS/Android simulators

## Phase 3: Scanner Feature
- [ ] Implement camera with barcode detection
- [ ] Build scan overlay with animations
- [ ] Create product detail modal
- [ ] Implement health score calculation
- [ ] Connect Open Food Facts API
- [ ] Add local SQLite caching

## Phase 4: Contribution Feature
- [ ] Build multi-step photo capture flow
- [ ] Implement OCR with Cloud Vision
- [ ] Create processing/success screens
- [ ] Add offline contribution queue
- [ ] Set up Cloud Functions

## Phase 5: User Features
- [ ] Implement authentication (email, Google, Apple, guest)
- [ ] Build history tab with search/filter
- [ ] Build favorites tab
- [ ] Create profile screen
- [ ] Add settings screens

## Phase 6: Polish
- [ ] Add animations and haptics
- [ ] Optimize performance
- [ ] Refine error handling
- [ ] Implement analytics events
- [ ] Testing and bug fixes

## Acceptance Checklist
- [ ] Barcode scanning works (EAN-13, UPC-A, QR)
- [ ] Health scores display with indicators
- [ ] Nutrition breakdown and ingredients analysis
- [ ] Contribution flow with OCR
- [ ] Offline support with syncing
- [ ] Authentication and user features
- [ ] Accessibility and RTL readiness
- [ ] Build succeeds for iOS and Android
