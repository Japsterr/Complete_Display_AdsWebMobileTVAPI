# DisplayAds Frontend

Dark-themed React + Vite + TypeScript app using Chakra UI with a matte gray surface and peach/orange afterglow brand accents.

## Theme
- Central tokens: `src/theme/tokens.ts`
- Chakra theme: `src/theme/index.ts`
- Global dark public styles: `src/custom.css` (class `.public-dark` for marketing pages)

Key brand values:
- Brand color: `brand.500 = #ff6b35`
- Surfaces: bg `#1a1b1e`, card `#222325`, border `rgba(255,107,53,0.25)`

## Pages
- Public: Home, Features, Pricing, Contact, Documentation wrapped by `PublicLayout`.
- Auth: Login, Register.
- Dashboard: Media, Campaigns, Displays, Analytics, Settings.

## Dev
- Build: `npm run build`
- Preview: `npm run preview`
- Lint: `npm run lint`

## Notes
- Legacy light styles (fallback.css, App.css) are no longer referenced anywhere. You can delete them to reduce noise, but they won't affect the build.
- Analytics summary + CSV are wired in the app; ensure API service is up and auth tokens available.
