import { z } from 'zod';
import { PasswordResetComplete } from '../validation/schemas'; // We will add this type to schemas

const API_Base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const authApi = {
  async initiatePasswordReset(email: string): Promise<{ message: string }> {
    const response = await fetch(`${API_Base}/auth/password-reset/initiate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send reset code');
    }

    return response.json();
  },

  async completePasswordReset(data: {
    email: string;
    otp_code: string;
    new_password: string;
  }): Promise<{ message: string }> {
    const response = await fetch(`${API_Base}/auth/password-reset/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset password');
    }

    return response.json();
  },
};
