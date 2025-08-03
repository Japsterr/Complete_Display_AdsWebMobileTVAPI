import { loadStripe } from '@stripe/stripe-js';
import api from './api';

export interface PlanFeatures {
  name: string;
  price: number;
  currency: string;
  stripe_price_id?: string;
  features: string[];
}

export interface StripeConfig {
  publishable_key: string;
  currency: string;
  plans: {
    free: PlanFeatures;
    business: PlanFeatures;
    enterprise: PlanFeatures;
  };
}

export class StripeService {
  private static instance: StripeService;
  private config: StripeConfig | null = null;

  public static getInstance(): StripeService {
    if (!StripeService.instance) {
      StripeService.instance = new StripeService();
    }
    return StripeService.instance;
  }

  /**
   * Get Stripe configuration from backend
   */
  async getConfig(): Promise<StripeConfig> {
    if (!this.config) {
      try {
        const response = await api.get('/payments/stripe-config/');
        this.config = response.data;
      } catch (error) {
        console.error('Failed to load Stripe config:', error);
        throw new Error('Unable to load payment configuration');
      }
    }
    return this.config!;
  }

  /**
   * Create checkout session and redirect to Stripe Checkout
   */
  async createCheckoutSession(planType: 'business' | 'enterprise'): Promise<void> {
    try {
      // Get checkout session from backend
      const response = await api.post('/payments/create-checkout-session/', {
        plan_type: planType
      });
      const { checkout_url } = response.data;

      // Redirect to Stripe Checkout
      window.location.href = checkout_url;
    } catch (error: any) {
      console.error('Failed to create checkout session:', error);
      
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('Failed to initiate payment process');
    }
  }

  /**
   * Format currency amount for display
   */
  formatAmount(amount: number, currency: string = 'ZAR'): string {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  /**
   * Check if user can upgrade to a specific plan
   */
  async canUpgrade(targetPlan: 'business' | 'enterprise'): Promise<boolean> {
    try {
      const response = await api.get('/auth/profile/');
      const currentPlan = response.data.account_type;
      
      // Free users can upgrade to anything
      if (currentPlan === 'free') return true;
      
      // Business users can only upgrade to enterprise
      if (currentPlan === 'business' && targetPlan === 'enterprise') return true;
      
      // Enterprise users can't upgrade further
      return false;
    } catch (error) {
      console.error('Failed to check upgrade eligibility:', error);
      return false;
    }
  }

  /**
   * Get plan information
   */
  async getPlanInfo(planType: 'free' | 'business' | 'enterprise'): Promise<PlanFeatures | null> {
    try {
      const config = await this.getConfig();
      return config.plans[planType] || null;
    } catch (error) {
      console.error('Failed to get plan info:', error);
      return null;
    }
  }
}

// Export singleton instance
export const stripeService = StripeService.getInstance();
export default stripeService;
