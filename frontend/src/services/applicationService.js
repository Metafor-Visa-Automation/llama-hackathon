export const saveApplication = async (applicationData, token) => {
  try {
    const response = await fetch(`/api/v1/applications/applications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'accept': 'application/json'
      },
      body: JSON.stringify(applicationData)
    });

    const data = await response.json();

    if (response.status === 201) {
      console.log('Application saved successfully:', data);
      return { success: true, data };
    } else {
      console.error('Failed to save application:', { status: response.status, data });
      return { success: false, error: data };
    }
  } catch (error) {
    console.error('Error saving application:', error);
    return { success: false, error };
  }
};
