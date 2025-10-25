// Example usage of the form filling API from frontend

// Example user data structure
const exampleUserData = {
  // Personal Information
  surname: "Doe",
  surname_at_birth: "Smith",
  first_name: "John",
  date_of_birth: "15/03/1990",
  place_of_birth: "New York",
  country_of_birth: "United States",
  current_nationality: "American",
  sex: "Male",
  marital_status: "Single",
  
  // Passport Information
  passport_type: "Ordinary",
  passport_number: "123456789",
  passport_issue_date: "01/01/2020",
  passport_expiry_date: "01/01/2030",
  passport_issued_by: "US Department of State",
  
  // Address Information
  current_address: "123 Main Street",
  city: "New York",
  postal_code: "10001",
  country: "United States",
  phone_number: "+1-555-123-4567",
  email: "john.doe@example.com",
  
  // Travel Information
  purpose_of_journey: "Tourism",
  intended_arrival_date: "15/06/2024",
  intended_departure_date: "30/06/2024",
  member_state_of_first_entry: "Germany",
  number_of_entries_requested: "Single",
  
  // Additional Information (optional)
  family_members_in_eu: "No",
  eu_residence_permit: "No",
  previous_schengen_visa: "No",
  fingerprints_taken: "No",
  
  // Emergency Contact (optional)
  emergency_contact_name: "Jane Doe",
  emergency_contact_phone: "+1-555-987-6543",
  emergency_contact_email: "jane.doe@example.com"
};

// Function to fill Schengen visa form
async function fillSchengenForm(userData, authToken) {
  try {
    const response = await fetch('/api/v1/form-filling/fill-schengen-form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        user_data: userData,
        include_preview: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // Convert base64 PDF to blob for download
    const pdfBytes = Uint8Array.from(atob(result.filled_form_data), c => c.charCodeAt(0));
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schengen_visa_form_${result.filled_form_id}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    return result;
  } catch (error) {
    console.error('Error filling form:', error);
    throw error;
  }
}

// Function to preview form filling
async function previewFormFilling(userData, authToken) {
  try {
    const response = await fetch('/api/v1/form-filling/preview-form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        user_data: userData
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error previewing form:', error);
    throw error;
  }
}

// Function to validate form data
async function validateFormData(userData, authToken) {
  try {
    const response = await fetch('/api/v1/form-filling/validate-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error validating data:', error);
    throw error;
  }
}

// Function to get form filling history
async function getFormFillingHistory(authToken) {
  try {
    const response = await fetch('/api/v1/form-filling/history', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error getting history:', error);
    throw error;
  }
}

// Example usage in a React component
function VisaFormFilling() {
  const [userData, setUserData] = useState(exampleUserData);
  const [loading, setLoading] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleValidateData = async () => {
    setLoading(true);
    try {
      const results = await validateFormData(userData, authToken);
      setValidationResults(results);
    } catch (error) {
      console.error('Validation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewForm = async () => {
    setLoading(true);
    try {
      const previewResult = await previewFormFilling(userData, authToken);
      setPreview(previewResult);
    } catch (error) {
      console.error('Preview failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFillForm = async () => {
    setLoading(true);
    try {
      const result = await fillSchengenForm(userData, authToken);
      console.log('Form filled successfully:', result);
      alert('Form filled and downloaded successfully!');
    } catch (error) {
      console.error('Form filling failed:', error);
      alert('Form filling failed. Please check your data and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="visa-form-filling">
      <h2>Schengen Visa Form Filling</h2>
      
      {/* Form fields would go here */}
      <div className="form-fields">
        {/* Personal Information */}
        <div className="section">
          <h3>Personal Information</h3>
          <input
            type="text"
            placeholder="Surname"
            value={userData.surname}
            onChange={(e) => setUserData({...userData, surname: e.target.value})}
          />
          <input
            type="text"
            placeholder="First Name"
            value={userData.first_name}
            onChange={(e) => setUserData({...userData, first_name: e.target.value})}
          />
          {/* More fields... */}
        </div>
        
        {/* Other sections... */}
      </div>

      {/* Action buttons */}
      <div className="actions">
        <button onClick={handleValidateData} disabled={loading}>
          Validate Data
        </button>
        <button onClick={handlePreviewForm} disabled={loading}>
          Preview Form
        </button>
        <button onClick={handleFillForm} disabled={loading}>
          Fill & Download Form
        </button>
      </div>

      {/* Validation results */}
      {validationResults && (
        <div className="validation-results">
          <h3>Validation Results</h3>
          <div className={`status ${validationResults.is_valid ? 'valid' : 'invalid'}`}>
            {validationResults.is_valid ? 'Valid' : 'Invalid'}
          </div>
          {validationResults.issues.length > 0 && (
            <div className="issues">
              <h4>Issues:</h4>
              <ul>
                {validationResults.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
          {validationResults.recommendations.length > 0 && (
            <div className="recommendations">
              <h4>Recommendations:</h4>
              <ul>
                {validationResults.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Preview results */}
      {preview && (
        <div className="preview-results">
          <h3>Form Preview</h3>
          <div className="filled-fields">
            {Object.entries(preview.filled_fields).map(([key, value]) => (
              <div key={key} className="field">
                <strong>{key}:</strong> {value}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default VisaFormFilling;
