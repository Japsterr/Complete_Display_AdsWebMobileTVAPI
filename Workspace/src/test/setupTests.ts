import '@testing-library/jest-dom';
import { server } from './server';

// Establish API mocking before all tests.
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
// Reset any runtime request handlers we may add during the tests.
afterEach(() => server.resetHandlers());
// Clean up after the tests are finished.
afterAll(() => server.close());

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
