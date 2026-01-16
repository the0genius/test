export const colors = {
  primary: {
    base: '#22C55E',
    dark: '#16A34A',
    light: '#4ADE80',
    glow: '#22C55E20',
  },
  neutral: {
    white: '#FFFFFF',
    offWhite: '#FAFAFA',
    lightGray: '#F4F4F5',
    mediumGray: '#A1A1AA',
    darkGray: '#3F3F46',
    nearBlack: '#18181B',
  },
  semantic: {
    healthy: '#22C55E',
    moderate: '#F59E0B',
    unhealthy: '#EF4444',
    info: '#3B82F6',
  },
} as const;

export const gradients = {
  hero: ['#22C55E', '#16A34A'],
  background: ['#FFFFFF', '#F4F4F5'],
} as const;

export const typography = {
  fontFamily: {
    primary: 'Inter',
    fallback: 'System',
  },
  fontWeight: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
  fontSize: {
    display: 32,
    h1: 28,
    h2: 24,
    h3: 20,
    bodyLarge: 18,
    body: 16,
    bodySmall: 14,
    caption: 12,
    tiny: 10,
  },
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
} as const;

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
  green: {
    shadowColor: '#22C55E',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 8,
  },
} as const;
