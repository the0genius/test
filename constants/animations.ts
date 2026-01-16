import { Easing } from 'react-native-reanimated';

export const SPRING_CONFIG = {
  damping: 20,
  stiffness: 90,
  mass: 1,
};

export const TIMING_CONFIG = {
  fast: 200,
  medium: 300,
  slow: 500,
};

export const EASING = {
  easeOut: Easing.bezier(0.25, 0.1, 0.25, 1),
  easeInOut: Easing.bezier(0.42, 0, 0.58, 1),
  spring: Easing.bezier(0.175, 0.885, 0.32, 1.275),
};
