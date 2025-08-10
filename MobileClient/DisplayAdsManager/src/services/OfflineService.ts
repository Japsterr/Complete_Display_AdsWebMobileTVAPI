import AsyncStorage from '@react-native-async-storage/async-storage';

const LAST_LOGIN_AT = 'OFFLINE_LAST_LOGIN_AT';

export type CacheKey = 'campaigns' | 'media' | 'displays' | 'dashboardStats';

export async function setLastLoginAt(date: Date = new Date()): Promise<void> {
  await AsyncStorage.setItem(LAST_LOGIN_AT, String(date.getTime()));
}

export async function getLastLoginAt(): Promise<Date | null> {
  const v = await AsyncStorage.getItem(LAST_LOGIN_AT);
  if (!v) return null;
  const n = Number(v);
  return isNaN(n) ? null : new Date(n);
}

export async function isOfflineAllowed(withinHours = 24): Promise<boolean> {
  const d = await getLastLoginAt();
  if (!d) return false;
  const ms = withinHours * 60 * 60 * 1000;
  return Date.now() - d.getTime() <= ms;
}

export async function saveCache<T>(key: CacheKey, data: T): Promise<void> {
  try { await AsyncStorage.setItem(`CACHE_${key}`, JSON.stringify({ t: Date.now(), data })); } catch {}
}

export async function loadCache<T>(key: CacheKey): Promise<T | null> {
  try {
    const v = await AsyncStorage.getItem(`CACHE_${key}`);
    if (!v) return null;
    const parsed = JSON.parse(v);
    return parsed?.data ?? null;
  } catch {
    return null;
  }
}
