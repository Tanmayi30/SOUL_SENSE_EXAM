const API_Base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const userApi = {
  async getAuditLogs(page: number = 1, limit: number = 20) {
    const token = localStorage.getItem('token');

    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_Base}/users/me/audit-logs?page=${page}&per_page=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/login'; // Redirect if unauthorized
        throw new Error('Unauthorized');
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch audit logs');
    }

    return response.json();
  },
};
