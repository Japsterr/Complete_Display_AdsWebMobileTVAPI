import '@testing-library/jest-dom';

// Basic mock for matchMedia used by some UI libs
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Helper to set auth token for protected route tests
export function setAuthToken(token: string = 'test-token') {
  window.localStorage.setItem('access_token', token);
}

export function clearAuthToken() {
  window.localStorage.removeItem('access_token');
}
