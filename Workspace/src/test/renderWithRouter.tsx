import { ReactElement, PropsWithChildren } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render } from '@testing-library/react';
import App from '../App';

interface Options {
  route?: string;
  initialEntries?: string[];
  withAuth?: boolean;
}

export function renderApp(options: Options = {}) {
  const { route = '/', initialEntries = [route], withAuth = false } = options;
  if (withAuth) {
    window.localStorage.setItem('access_token', 'test-token');
  } else {
    window.localStorage.removeItem('access_token');
  }
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <App />
    </MemoryRouter>
  );
}

export function renderWithRouter(
  ui: ReactElement,
  { route = '/', initialEntries = [route] }: Omit<Options, 'withAuth'> = {}
) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      {ui}
    </MemoryRouter>
  );
}
