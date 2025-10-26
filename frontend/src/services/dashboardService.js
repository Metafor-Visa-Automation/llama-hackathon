const API_BASE_URL = '/api/v1';

export const getApplications = async (token) => {
  const response = await fetch(`${API_BASE_URL}/applications/applications`, {
    method: 'GET',
    headers: {
      'accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch applications' }));
    throw new Error(errorData.detail);
  }
  return response.json();
};
