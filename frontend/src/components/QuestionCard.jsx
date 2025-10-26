import { useState, useRef } from 'react';
import { TextField, Button, Chip, IconButton, Tooltip, FormControlLabel, Checkbox, CircularProgress, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import {
  ArrowBack,
  ArrowForward,
  Send,
  CloudUpload,
  CheckCircle,
  Close,
  InsertDriveFile,
  Link as LinkIcon,
  PriorityHigh,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  FiberManualRecord as CircleIcon,
  CheckBox as CheckBoxIcon,
  CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon
} from '@mui/icons-material';

/**
 * QuestionCard Component
 * Renders action steps dynamically based on response-final.json structure
 * Automatically shows document upload area when requires_document is true
 * Displays priority badges, source URLs, and step descriptions
 *
 * @param {Object} props
 * @param {Object} props.question - Action step object from response-final.json
 *   - step_id: Unique identifier for the step
 *   - title: Step title/question
 *   - description: Detailed description of the step
 *   - priority_score: 1-5 priority score (5 = highest)
 *   - requires_document: Boolean indicating if document upload is needed
 *   - source_urls: Array of reference URLs
 * @param {string} props.value - Current answer value (for text/textarea inputs)
 * @param {Array<File>} props.documents - Array of uploaded document files
 * @param {Function} props.onChange - Handler for answer changes
 * @param {Function} props.onDocumentAdd - Handler for adding a document
 * @param {Function} props.onDocumentRemove - Handler for removing a document
 * @param {number} props.currentIndex - Current question index (0-based)
 * @param {number} props.totalQuestions - Total number of questions
 * @param {Function} props.onNext - Handler for next button
 * @param {Function} props.onPrevious - Handler for previous button
 * @param {Function} props.onSubmit - Handler for submit button
 */
const QuestionCard = ({
  question,
  value,
  documents = [],
  onChange,
  onDocumentAdd,
  onDocumentRemove,
  currentIndex,
  totalQuestions,
  onNext,
  onPrevious,
  onSubmit,
  isUploading = false,
  uploadStage = '',
  isSubmitting = false,
  documentType,
  onDocumentTypeChange
}) => {
  const isLastQuestion = currentIndex === totalQuestions - 1;
  const isFirstQuestion = currentIndex === 0;
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Get upload status text based on stage
  const getUploadStatusText = () => {
    if (uploadStage === 'uploading') {
      return 'Belgeleriniz yükleniyor...';
    } else if (uploadStage === 'processing') {
      return 'Belgeleriniz kontrol ediliyor...';
    }
    return 'Yükleniyor...';
  };

  // Document type options
  const documentTypes = [
    { value: 'passport', label: 'Pasaport' },
    { value: 'bank_statement', label: 'Banka Ekstresi' },
    { value: 'biometric_photo', label: 'Biyometrik Fotoğraf' },
    { value: 'birth_certificate', label: 'Doğum Belgesi' },
    { value: 'business_letter', label: 'İş Mektubu' },
    { value: 'employment_letter', label: 'Çalışma Mektubu' },
    { value: 'employment_certificate', label: 'Çalışma Belgesi' },
    { value: 'payslip', label: 'Maaş Bordrosu' },
    { value: 'hotel_reservation', label: 'Otel Rezervasyonu' },
    { value: 'flight_reservation', label: 'Uçak Rezervasyonu' },
    { value: 'travel_insurance', label: 'Seyahat Sigortası' },
    { value: 'invitation_letter', label: 'Davet Mektubu' },
    { value: 'previous_visas', label: 'Önceki Vizeler' },
    { value: 'student_certificate', label: 'Öğrenci Belgesi' },
    { value: 'academic_transcript', label: 'Akademik Transkript' },
    { value: 'tax_return', label: 'Vergi Beyannamesi' },
    { value: 'property_deed', label: 'Tapu Belgesi' },
    { value: 'social_security', label: 'Sosyal Güvenlik' },
    { value: 'insurance', label: 'Sigorta' },
    { value: 'other', label: 'Diğer' }
  ];

  /**
   * Handle file drop - supports multiple files
   */
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => onDocumentAdd(file));
  };

  /**
   * Handle drag over
   */
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  /**
   * Handle drag leave
   */
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  /**
   * Handle file input change - supports multiple files
   */
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    files.forEach(file => onDocumentAdd(file));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Format file size
   */
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  /**
   * Get file icon color based on extension
   */
  const getFileColor = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    const colorMap = {
      pdf: '#EF4444',
      doc: '#3B82F6',
      docx: '#3B82F6',
      jpg: '#10B981',
      jpeg: '#10B981',
      png: '#10B981',
      default: '#6B7280'
    };
    return colorMap[ext] || colorMap.default;
  };

  /**
   * Get priority display info based on score
   */
  const getPriorityInfo = (score) => {
    switch(score) {
      case 5:
        return {
          label: 'Çok Yüksek Öncelik',
          color: '#DC2626',
          bgColor: '#FEE2E2',
          Icon: ErrorIcon
        };
      case 4:
        return {
          label: 'Yüksek Öncelik',
          color: '#EA580C',
          bgColor: '#FFEDD5',
          Icon: PriorityHigh
        };
      case 3:
        return {
          label: 'Orta Öncelik',
          color: '#D97706',
          bgColor: '#FEF3C7',
          Icon: WarningIcon
        };
      case 2:
        return {
          label: 'Düşük Öncelik',
          color: '#059669',
          bgColor: '#D1FAE5',
          Icon: InfoIcon
        };
      case 1:
        return {
          label: 'Çok Düşük Öncelik',
          color: '#047857',
          bgColor: '#D1FAE5',
          Icon: CircleIcon
        };
      default:
        return null;
    }
  };

  /**
   * Render input based on question configuration
   * - If requires_document is true, show document upload area
   * - Otherwise, show a simple text area for notes/comments
   */
  const renderInput = () => {
    // If the step requires a document, show the document upload interface
    if (question.requires_document) {
      return (
        <div>
          {/* Document Type Dropdown */}
          <FormControl
            fullWidth
            sx={{
              marginBottom: '1.5rem',
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                fontFamily: '"Playfair Display", serif',
              }
            }}
          >
            <InputLabel
              sx={{
                fontFamily: '"Playfair Display", serif',
                fontWeight: 600,
                color: '#059669',
                '&.Mui-focused': {
                  color: '#059669'
                }
              }}
            >
              Döküman Tipi Seçin
            </InputLabel>
            <Select
              value={documentType || ''}
              onChange={(e) => onDocumentTypeChange(e.target.value)}
              label="Döküman Tipi Seçin"
              sx={{
                fontFamily: '"Playfair Display", serif',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#D1FAE5',
                  borderWidth: '2px',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#10B981',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#059669',
                  borderWidth: '2px',
                }
              }}
            >
              {documentTypes.map((type) => (
                <MenuItem
                  key={type.value}
                  value={type.value}
                  sx={{
                    fontFamily: '"Playfair Display", serif',
                    '&:hover': {
                      backgroundColor: '#F0FDF4'
                    },
                    '&.Mui-selected': {
                      backgroundColor: '#D1FAE5',
                      '&:hover': {
                        backgroundColor: '#A7F3D0'
                      }
                    }
                  }}
                >
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            multiple
          />

          {/* Upload Area */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            style={{
              border: isDragging ? '3px dashed #10B981' : '2px dashed #A7F3D0',
              borderRadius: '16px',
              padding: documents.length > 0 ? '1.5rem' : '3rem 2rem',
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragging ? '#F0FDF4' : '#FAFAFA',
              transition: 'all 0.3s ease',
              marginBottom: documents.length > 0 ? '1rem' : 0
            }}
          >
            <CloudUpload
              sx={{
                fontSize: documents.length > 0 ? 40 : 64,
                color: '#10B981',
                marginBottom: documents.length > 0 ? '0.5rem' : '1rem'
              }}
            />
            <p style={{
              fontFamily: '"Playfair Display", serif',
              fontSize: documents.length > 0 ? '0.95rem' : '1.1rem',
              fontWeight: '600',
              color: '#1a1a1a',
              marginBottom: documents.length > 0 ? 0 : '0.5rem'
            }}>
              {documents.length > 0
                ? '+ Daha fazla döküman ekle'
                : 'Dökümanları yüklemek için tıklayın veya sürükleyin'}
            </p>
            {documents.length === 0 && (
              <p style={{
                fontFamily: '"Playfair Display", serif',
                fontSize: '0.9rem',
                color: '#666666',
                margin: 0
              }}>
                PDF, JPG, PNG, DOC, DOCX formatları desteklenir
              </p>
            )}
          </div>

          {/* Uploaded Documents Grid */}
          {documents.length > 0 && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
              gap: '0.75rem',
              marginTop: '1rem'
            }}>
              {documents.map((doc, index) => (
                <div
                  key={index}
                  style={{
                    border: '1px solid #E5E7EB',
                    borderRadius: '12px',
                    padding: '1rem',
                    backgroundColor: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
                    e.currentTarget.style.borderColor = '#10B981';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)';
                    e.currentTarget.style.borderColor = '#E5E7EB';
                  }}
                >
                  {/* File Icon */}
                  <div style={{
                    flexShrink: 0,
                    width: '40px',
                    height: '40px',
                    borderRadius: '8px',
                    backgroundColor: getFileColor(doc.name) + '15',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <InsertDriveFile sx={{ color: getFileColor(doc.name), fontSize: 24 }} />
                  </div>

                  {/* File Info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{
                      fontFamily: '"Playfair Display", serif',
                      fontSize: '0.9rem',
                      fontWeight: '600',
                      color: '#1a1a1a',
                      margin: 0,
                      marginBottom: '0.25rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {doc.name}
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <p style={{
                        fontFamily: '"Playfair Display", serif',
                        fontSize: '0.75rem',
                        color: '#666666',
                        margin: 0
                      }}>
                        {formatFileSize(doc.size)}
                      </p>
                      <CheckCircle sx={{ color: '#10B981', fontSize: 14 }} />
                    </div>
                  </div>

                  {/* Remove Button */}
                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      onDocumentRemove(index);
                    }}
                    size="small"
                    sx={{
                      padding: '4px',
                      color: '#9CA3AF',
                      '&:hover': {
                        backgroundColor: '#FEE2E2',
                        color: '#EF4444'
                      }
                    }}
                  >
                    <Close sx={{ fontSize: 18 }} />
                  </IconButton>
                </div>
              ))}
            </div>
          )}

          {/* Document Counter */}
          {documents.length > 0 && (
            <div style={{
              marginTop: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Chip
                icon={<CheckCircle />}
                label={`${documents.length} döküman yüklendi`}
                size="small"
                sx={{
                  backgroundColor: '#F0FDF4',
                  color: '#059669',
                  fontFamily: '"Playfair Display", serif',
                  fontWeight: '600',
                  '& .MuiChip-icon': {
                    color: '#10B981'
                  }
                }}
              />
            </div>
          )}
        </div>
      );
    }

    // Otherwise, show a checkbox to mark the step as completed
    // The 'value' will be 'true' or 'false' string for checkbox state
    const isChecked = value === 'true' || value === true;

    return (
      <div style={{
        backgroundColor: isChecked ? '#F0FDF4' : '#FAFAFA',
        border: isChecked ? '2px solid #10B981' : '2px solid #E5E7EB',
        borderRadius: '16px',
        padding: '1.5rem 2rem',
        transition: 'all 0.3s ease',
        boxShadow: isChecked ? '0 4px 20px rgba(16, 185, 129, 0.15)' : '0 2px 8px rgba(0, 0, 0, 0.05)',
      }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', width: '100%', margin: 0 }}>
          <Checkbox
            checked={isChecked}
            onChange={(e) => onChange(e.target.checked)}
            icon={<CheckBoxOutlineBlankIcon sx={{ fontSize: 32 }} />}
            checkedIcon={<CheckBoxIcon sx={{ fontSize: 32 }} />}
            sx={{
              color: '#10B981',
              '&.Mui-checked': {
                color: '#059669',
              },
              '& .MuiSvgIcon-root': {
                transition: 'all 0.2s ease',
              },
              padding: 0,
              marginRight: '1rem',
              marginTop: '0.2rem'
            }}
          />
          <div style={{ flex: 1 }}>
            <p style={{
              fontFamily: '"Playfair Display", serif',
              fontSize: '1.1rem',
              fontWeight: '600',
              color: isChecked ? '#059669' : '#1a1a1a',
              margin: 0,
              marginBottom: '0.25rem',
              transition: 'color 0.3s ease'
            }}>
              {isChecked ? 'Bu adımı tamamladım' : 'Bu adımı tamamlandı olarak işaretle'}
            </p>
            <p style={{
              fontFamily: '"Playfair Display", serif',
              fontSize: '0.85rem',
              color: '#666666',
              margin: 0
            }}>
              {isChecked
                ? 'Harika! Bir sonraki adıma geçebilirsiniz.'
                : 'Bu adım tamamlandığında işaretleyin'}
            </p>
          </div>
        </div>

        {isChecked && (
          <div style={{
            marginTop: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid #D1FAE5',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <CheckCircle sx={{ color: '#10B981', fontSize: 20 }} />
            <p style={{
              fontFamily: '"Playfair Display", serif',
              fontSize: '0.9rem',
              fontWeight: '600',
              color: '#059669',
              margin: 0
            }}>
              Tamamlandı olarak işaretlendi
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      style={{
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.98)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderRadius: '24px',
        padding: '2.5rem',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        border: '1px solid rgba(255, 255, 255, 0.8)',
        overflow: 'hidden',
      }}
    >
      {/* Question Number Badge */}
      <div
        style={{
          display: 'inline-block',
          backgroundColor: '#F0FDF4',
          color: '#059669',
          padding: '0.5rem 1rem',
          borderRadius: '50px',
          fontSize: '0.875rem',
          fontWeight: '700',
          fontFamily: '"Playfair Display", serif',
          marginBottom: '1.5rem',
        }}
      >
        Adım {currentIndex + 1} / {totalQuestions}
      </div>

      {/* Question Text - Use title from response-final.json */}
      <h2
        style={{
          fontSize: '1.75rem',
          fontWeight: '700',
          color: '#1a1a1a',
          marginBottom: '1rem',
          fontFamily: '"Playfair Display", serif',
          lineHeight: '1.4',
        }}
      >
        {question.title}
      </h2>

      {/* Description - Use description from response-final.json */}
      {question.description && (
        <p style={{
          fontSize: '1rem',
          color: '#666666',
          marginBottom: '1.5rem',
          fontFamily: '"Playfair Display", serif',
          lineHeight: '1.6',
        }}>
          {question.description}
        </p>
      )}

      {/* Priority Badge - Use priority_score from response-final.json */}
      {question.priority_score && getPriorityInfo(question.priority_score) && (() => {
        const priorityInfo = getPriorityInfo(question.priority_score);
        const PriorityIcon = priorityInfo.Icon;
        return (
          <div style={{ marginBottom: '1.5rem' }}>
            <Chip
              icon={<PriorityIcon sx={{ fontSize: 16 }} />}
              label={priorityInfo.label}
              size="small"
              sx={{
                backgroundColor: priorityInfo.bgColor,
                color: priorityInfo.color,
                fontFamily: '"Playfair Display", serif',
                fontWeight: '700',
                fontSize: '0.8rem',
                border: `1.5px solid ${priorityInfo.color}30`,
                '& .MuiChip-icon': {
                  color: priorityInfo.color
                }
              }}
            />
          </div>
        );
      })()}

      {/* Input Field - Dynamically shows document upload or notes based on requires_document */}
      <div style={{ marginBottom: '1.5rem' }}>
        {renderInput()}
      </div>

      {/* Source URLs - Use source_urls from response-final.json */}
      {question.source_urls && question.source_urls.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <Tooltip
            title={
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem',
                padding: '0.25rem'
              }}>
                {question.source_urls.map((url, idx) => (
                  <a
                    key={idx}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      fontSize: '0.8rem',
                      color: '#FFFFFF',
                      textDecoration: 'underline',
                      fontFamily: '"Playfair Display", serif',
                      display: 'block',
                      wordBreak: 'break-all'
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {url}
                  </a>
                ))}
              </div>
            }
            arrow
            placement="top"
            componentsProps={{
              tooltip: {
                sx: {
                  backgroundColor: 'rgba(0, 0, 0, 0.9)',
                  maxWidth: '400px',
                  padding: '0.75rem',
                  fontSize: '0.8rem'
                }
              }
            }}
          >
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: '#F9FAFB',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F3F4F6';
              e.currentTarget.style.borderColor = '#10B981';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#F9FAFB';
              e.currentTarget.style.borderColor = '#E5E7EB';
            }}
            >
              <LinkIcon sx={{ fontSize: 16, color: '#6B7280' }} />
              <p style={{
                fontSize: '0.85rem',
                fontWeight: '600',
                color: '#6B7280',
                margin: 0,
                fontFamily: '"Playfair Display", serif',
              }}>
                Kaynaklar ({question.source_urls.length})
              </p>
            </div>
          </Tooltip>
        </div>
      )}

      {/* Navigation Buttons */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {/* Previous Button */}
        {!isFirstQuestion && (
          <Button
            onClick={onPrevious}
            startIcon={<ArrowBack />}
            sx={{
              color: '#666666',
              padding: '0.75rem 1.5rem',
              borderRadius: '50px',
              fontSize: '1rem',
              fontWeight: '600',
              textTransform: 'none',
              fontFamily: '"Playfair Display", serif',
              '&:hover': {
                backgroundColor: '#F5F5F5',
              },
            }}
          >
            Geri
          </Button>
        )}

        <div style={{ flex: 1 }} />

        {/* Next/Submit Button */}
        {!isLastQuestion ? (
          <Button
            onClick={onNext}
            disabled={isUploading}
            endIcon={isUploading ? <CircularProgress size={20} sx={{ color: '#FFFFFF' }} /> : <ArrowForward />}
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#FFFFFF',
              padding: '0.875rem 2rem',
              borderRadius: '50px',
              fontSize: '1rem',
              fontWeight: '700',
              textTransform: 'none',
              fontFamily: '"Playfair Display", serif',
              boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(16, 185, 129, 0.5)',
              },
              '&:disabled': {
                background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                color: '#FFFFFF',
              },
              transition: 'all 0.3s ease',
            }}
          >
            {isUploading ? getUploadStatusText() : 'İleri'}
          </Button>
        ) : (
          <Button
            onClick={onSubmit}
            disabled={isSubmitting}
            endIcon={isSubmitting ? <CircularProgress size={20} sx={{ color: '#FFFFFF' }} /> : <Send />}
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#FFFFFF',
              padding: '0.875rem 2rem',
              borderRadius: '50px',
              fontSize: '1rem',
              fontWeight: '700',
              textTransform: 'none',
              fontFamily: '"Playfair Display", serif',
              boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(16, 185, 129, 0.5)',
              },
              '&:disabled': {
                background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                color: '#FFFFFF',
              },
              transition: 'all 0.3s ease',
            }}
          >
            {isSubmitting ? 'Kaydediliyor...' : 'Devam Et'}
          </Button>
        )}
      </div>
    </div>
  );
};

export default QuestionCard;
