// Central theme tokens for brand and surfaces
export const colors = {
  // Brighter, more vivid brand orange with a warmer ramp
  brand: {
    50: '#fff3e8',
    100: '#ffe0c2',
    200: '#ffc592',
    300: '#ffa660',
    400: '#ff9133',
    500: '#ff7a1a',
    600: '#e96d10',
    700: '#c55c0e',
    800: '#a24a0c',
    900: '#7f3909',
  },
  // Two-tone dark surfaces (less harsh), with accent border
  surface: {
    bg: '#1d1f23',      // primary page background
    bgAlt: '#23262b',   // alternate dark band background
    card: '#24272d',    // card background
    cardAlt: '#2a2e35', // elevated card background
    border: 'rgba(255,122,26,0.30)',
    text: '#e8eaee',
    muted: '#aeb6bf',
  },
};

export const radii = {
  sm: '0.375rem',
  md: '0.5rem',
  lg: '0.75rem',
  xl: '1rem',
};

export const shadows = {
  // Softer but visible orange glow for focus/hover rings
  glow: '0 0 0 4px rgba(255,122,26,0.22), 0 10px 20px rgba(0,0,0,0.25)',
};
