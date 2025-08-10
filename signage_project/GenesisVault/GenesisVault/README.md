# GenesisVault

GenesisVault is a modern React + Vite + TypeScript frontend for secure key management using the Keygen API.

## Features
- Login form (Keygen API authentication)
- Dashboard (user info, license management, machine list, etc.)
- Styled with Bootstrap 5 and React-Bootstrap
- Matte gray background with Genesis orange accents

## How to run
1. Install dependencies:
   ```
   npm install
   ```
2. Start the development server:
   ```
   npm run dev
   ```
3. Open [http://localhost:5173/](http://localhost:5173/) in your browser.

## Requirements
- Node.js 18+
- npm 9+
- Vite 5+
- React 19+
- See `package.json` for all dependencies

## Troubleshooting
- If you see ESM/CJS errors, ensure your Node.js is v18+ and your `vite.config.ts` uses ESM syntax (as it does by default).
- For missing plugins, run `npm install --save-dev @vitejs/plugin-react`.

---
