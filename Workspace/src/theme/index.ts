import { extendTheme } from '@chakra-ui/react';
import { colors as tokenColors, radii, shadows } from './tokens';

export const theme = extendTheme({
  config: { initialColorMode: 'dark', useSystemColorMode: false },
  styles: {
    global: {
      'html, body': {
        backgroundColor: tokenColors.surface.bg,
        color: tokenColors.surface.text,
      },
      'section.alt': {
        backgroundColor: tokenColors.surface.bgAlt,
      },
    },
  },
  colors: {
    brand: tokenColors.brand,
    surface: tokenColors.surface,
  },
  radii,
  shadows,
  components: {
    Button: {
      baseStyle: { borderRadius: 'xl' },
      variants: {
        solid: {
          bg: 'brand.500',
          _hover: { bg: 'brand.400', boxShadow: shadows.glow },
        },
        outline: {
          borderColor: 'brand.400',
          color: 'brand.400',
          _hover: { boxShadow: shadows.glow },
        },
      },
    },
  },
});
