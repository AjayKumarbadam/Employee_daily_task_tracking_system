const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  getToken() {
    return localStorage.getItem('edsts_token');
  }

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);

      if (response.status === 401) {
        localStorage.removeItem('edsts_token');
        localStorage.removeItem('edsts_user');
        window.location.reload();
        throw new Error('Your session has expired. Please sign in again.');
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMessage = data.detail || 'An unexpected error occurred. Please try again.';
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      throw error;
    }
  }

  // Auth APIs
  login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  getCurrentUser() {
    return this.request('/auth/me');
  }

  // Tasks APIs
  getTasks(params = {}) {
    const query = new URLSearchParams();
    if (params.priority) query.append('priority', params.priority);
    if (params.assigned_user_id) query.append('assigned_user_id', params.assigned_user_id);
    if (params.is_overdue !== undefined) query.append('is_overdue', params.is_overdue);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/tasks${queryString}`);
  }

  getTaskById(taskId) {
    return this.request(`/tasks/${taskId}`);
  }

  createTask(taskData) {
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  updateTask(taskId, taskData) {
    return this.request(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  assignTask(taskId, userId) {
    return this.request(`/tasks/${taskId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  getTaskStatuses() {
    return this.request('/tasks/statuses');
  }

  // Daily Updates APIs
  submitDailyUpdate(updateData) {
    return this.request('/daily-updates', {
      method: 'POST',
      body: JSON.stringify(updateData),
    });
  }

  getDailyUpdates(params = {}) {
    const query = new URLSearchParams();
    if (params.task_id) query.append('task_id', params.task_id);
    if (params.user_id) query.append('user_id', params.user_id);
    if (params.update_date) query.append('update_date', params.update_date);
    if (params.from_date) query.append('from_date', params.from_date);
    if (params.to_date) query.append('to_date', params.to_date);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/daily-updates${queryString}`);
  }

  // Users APIs
  getUsers(params = {}) {
    const query = new URLSearchParams();
    if (params.department) query.append('department', params.department);
    if (params.is_active !== undefined) query.append('is_active', params.is_active);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/users${queryString}`);
  }

  createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  updateUser(userId, userData) {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  toggleUserStatus(userId, activate = true) {
    return this.request(`/users/${userId}/${activate ? 'activate' : 'deactivate'}`, {
      method: 'PATCH',
    });
  }

  // Dashboard APIs
  getManagerDashboard(date = null) {
    const query = date ? `?target_date=${date}` : '';
    return this.request(`/dashboard/manager${query}`);
  }

  getEmployeeDashboard(date = null) {
    const query = date ? `?target_date=${date}` : '';
    return this.request(`/dashboard/employee${query}`);
  }
}

export const api = new ApiService();
