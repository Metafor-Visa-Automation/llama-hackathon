import React, { useState, useEffect } from 'react';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

/**
 * BiometricPhotoChecklist Component
 * 
 * Displays comprehensive biometric photo requirements and validation results
 * for visa applications with interactive checklist functionality.
 */
const BiometricPhotoChecklist = ({ 
  checklistTemplate, 
  validationResult = null, 
  onPhotoUpload = null,
  applicationId = null 
}) => {
  const [uploadedPhoto, setUploadedPhoto] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Handle photo upload
  const handlePhotoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('photo', file);
      formData.append('application_id', applicationId || '');
      formData.append('checklist_template_id', checklistTemplate.checkId);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch('/api/v1/biometric-photo/validate-photo', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('firebase_token')}`
        }
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const result = await response.json();
        setUploadedPhoto(result);
        if (onPhotoUpload) {
          onPhotoUpload(result);
        }
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Photo upload error:', error);
      alert('Failed to upload photo. Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // Get validation status for each criterion
  const getCriterionStatus = (criterion) => {
    if (!validationResult) return 'pending';
    
    const issues = validationResult.issues || [];
    const recommendations = validationResult.recommendations || [];
    
    // Check if this criterion has any issues
    const hasIssue = issues.some(issue => 
      criterion.toLowerCase().includes(issue.toLowerCase()) ||
      issue.toLowerCase().includes(criterion.toLowerCase())
    );
    
    if (hasIssue) return 'error';
    
    // Check if this criterion is mentioned in recommendations
    const hasRecommendation = recommendations.some(rec => 
      criterion.toLowerCase().includes(rec.toLowerCase()) ||
      rec.toLowerCase().includes(criterion.toLowerCase())
    );
    
    if (hasRecommendation) return 'warning';
    
    return 'success';
  };

  // Render status icon
  const renderStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {checklistTemplate.docName}
        </h3>
        <p className="text-gray-600 mb-4">
          {checklistTemplate.docDescription}
        </p>
        
        {checklistTemplate.referenceUrl && (
          <a 
            href={checklistTemplate.referenceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 text-sm underline"
          >
            View official requirements →
          </a>
        )}
      </div>

      {/* Photo Upload Section */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-3">Upload Your Photo</h4>
        
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <input
              type="file"
              accept="image/jpeg,image/png"
              onChange={handlePhotoUpload}
              disabled={isUploading}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            
            {isUploading && (
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Uploading... {uploadProgress}%
                </p>
              </div>
            )}
          </div>

          {uploadedPhoto && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                <span className="text-green-800 font-medium">
                  Photo uploaded successfully!
                </span>
              </div>
              <p className="text-green-700 text-sm mt-1">
                Validation Score: {Math.round(uploadedPhoto.validation_score * 100)}%
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Requirements Checklist */}
      <div className="space-y-3">
        <h4 className="text-lg font-medium text-gray-900 mb-3">
          Photo Requirements Checklist
        </h4>
        
        {checklistTemplate.acceptanceCriteria.map((criterion, index) => {
          const status = getCriterionStatus(criterion);
          
          return (
            <div 
              key={index}
              className={`flex items-start space-x-3 p-3 rounded-lg border ${
                status === 'success' ? 'bg-green-50 border-green-200' :
                status === 'error' ? 'bg-red-50 border-red-200' :
                status === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                'bg-gray-50 border-gray-200'
              }`}
            >
              {renderStatusIcon(status)}
              <span className={`text-sm ${
                status === 'success' ? 'text-green-800' :
                status === 'error' ? 'text-red-800' :
                status === 'warning' ? 'text-yellow-800' :
                'text-gray-700'
              }`}>
                {criterion}
              </span>
            </div>
          );
        })}
      </div>

      {/* Validation Results */}
      {validationResult && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="text-lg font-medium text-blue-900 mb-3">
            Validation Results
          </h4>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-blue-800">
                Overall Score:
              </span>
              <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                validationResult.validation_score >= 0.8 ? 'bg-green-100 text-green-800' :
                validationResult.validation_score >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {Math.round(validationResult.validation_score * 100)}%
              </span>
            </div>

            {validationResult.issues && validationResult.issues.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-red-800 mb-2">Issues Found:</h5>
                <ul className="list-disc list-inside space-y-1">
                  {validationResult.issues.map((issue, index) => (
                    <li key={index} className="text-sm text-red-700">{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            {validationResult.recommendations && validationResult.recommendations.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-blue-800 mb-2">Recommendations:</h5>
                <ul className="list-disc list-inside space-y-1">
                  {validationResult.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-blue-700">{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Technical Specifications */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-lg font-medium text-gray-900 mb-3">
          Technical Specifications
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">File Types:</span>
            <span className="ml-2 text-gray-600">
              {checklistTemplate.validationRules.fileTypes?.join(', ') || 'JPEG, PNG'}
            </span>
          </div>
          
          <div>
            <span className="font-medium text-gray-700">Max File Size:</span>
            <span className="ml-2 text-gray-600">
              {Math.round(checklistTemplate.validationRules.maxFileSize / 1024 / 1024)}MB
            </span>
          </div>
          
          <div>
            <span className="font-medium text-gray-700">Min Resolution:</span>
            <span className="ml-2 text-gray-600">
              {checklistTemplate.validationRules.ocrValidationRules?.min_resolution_width || 600} x 
              {checklistTemplate.validationRules.ocrValidationRules?.min_resolution_height || 600} pixels
            </span>
          </div>
          
          <div>
            <span className="font-medium text-gray-700">Photo Age:</span>
            <span className="ml-2 text-gray-600">
              Within last {checklistTemplate.validationRules.ocrValidationRules?.max_photo_age_months || 6} months
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BiometricPhotoChecklist;
