export async function authFetch(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No access token found');
  }

  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      return authFetch(url, options);
    } else {
      throw new Error('Session expired');
    }
  }

  return response;
}

async function refreshToken() {
  try {
    const response = await fetch('http://127.0.0.1:8000/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      return true;
    }
  } catch (error) {
    console.error('Failed to refresh token:', error);
  }

  return false;
}