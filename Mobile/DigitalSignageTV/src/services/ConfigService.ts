import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE as DEFAULT_API_BASE } from '../config';

const KEY = 'API_BASE_URL_OVERRIDE';

class ConfigService {
  private cache: string | null = null;

  async getApiBase(): Promise<string> {
    if (this.cache) return this.cache;
    try {
      const v = await AsyncStorage.getItem(KEY);
      this.cache = ((v && v.length > 0 ? v : DEFAULT_API_BASE) as string).replace(/\/$/, '');
      return this.cache as string;
    } catch {
      this.cache = DEFAULT_API_BASE.replace(/\/$/, '');
      return this.cache as string;
    }
  }

  async setApiBase(url: string): Promise<void> {
    this.cache = url.replace(/\/$/, '');
    await AsyncStorage.setItem(KEY, this.cache);
  }
}

export default new ConfigService();
