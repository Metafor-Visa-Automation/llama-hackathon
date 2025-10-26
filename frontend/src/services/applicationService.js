/**
 * Generate visa checklist from AI API
 * @param {Object} params - Request parameters
 * @param {string} params.nationality - User's nationality (e.g., "Türkiye")
 * @param {string} params.destination_country - Destination country (e.g., "Almanya")
 * @param {string} params.visa_type - Type of visa (e.g., "tourist", "business", "student", "work")
 * @param {string} params.occupation - User's occupation (e.g., "Software Engineer")
 * @param {string} params.travel_purpose - Purpose of travel (e.g., "Tourism")
 * @param {boolean} params.force_refresh - Force refresh the cache (default: false)
 * @param {number} params.temperature - AI temperature (default: 0.3)
 * @returns {Promise<{success: boolean, data?: Object, error?: Object}>}
 */
export const generateVisaChecklist = async (params) => {
  try {
    console.log('🚀 Generating visa checklist with params:', params);

    const response = await fetch('https://d0b00d6a25a6.ngrok-free.app/api/v1/visa/generate-checklist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'accept': 'application/json'
      },
      body: JSON.stringify({
        nationality: params.nationality,
        destination_country: params.destination_country,
        visa_type: params.visa_type,
        occupation: params.occupation || 'Software Engineer',
        travel_purpose: params.travel_purpose,
        force_refresh: false,
        temperature: params.temperature || 0.3
      })
    });

    const data = await response.json();

    if (response.ok) {
      console.log('✅ Visa checklist generated successfully:', data);
      return { success: true, data };
    } else {
      console.error('❌ Failed to generate visa checklist:', { status: response.status, data });
      return { success: false, error: data };
    }
  } catch (error) {
    console.error('💥 Error generating visa checklist:', error);
    return { success: false, error: { message: error.message } };
  }
};

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
