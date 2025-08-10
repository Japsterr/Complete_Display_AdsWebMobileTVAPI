import { extendTheme } from '@chakra-ui/react';
import { colors as tokenColors, radii, shadows } from './tokens';

export const theme = extendTheme({
  config: { initialColorMode: 'dark', useSystemColorMode: false },
  styles: {
    global: {
      body: { bg: tokenColors.surface.bg, color: tokenColors.surface.text },
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
          borderColor: 'brand.500',
          color: 'brand.500',
          _hover: { bg: 'rgba(255,107,53,0.08)' },
        },
      },
    },
  },
});
