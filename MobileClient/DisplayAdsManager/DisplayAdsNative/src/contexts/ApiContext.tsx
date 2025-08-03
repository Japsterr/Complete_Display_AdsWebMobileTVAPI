/**
 * API Context
 * Provides easy access to API services throughout the app
 */

import React, { createContext, useContext, ReactNode } from 'react';
import ApiService from '../services/ApiService';

const ApiContext = createContext(ApiService);

export function ApiProvider({ children }: { children: ReactNode }) {
  return (
    <ApiContext.Provider value={ApiService}>
      {children}
    </ApiContext.Provider>
  );
}

export function useApi() {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}
