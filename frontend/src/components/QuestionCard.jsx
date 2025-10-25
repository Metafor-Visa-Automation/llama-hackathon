import { useState, useRef } from 'react';
import { TextField, Button, Radio, RadioGroup, FormControlLabel, FormControl, Chip, IconButton } from '@mui/material';
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
  Schedule as ScheduleIcon,
  Euro as EuroIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

/**
 * QuestionCard Component
 * Renders different question types (text, textarea, radio, document upload) in a card format
 * Supports multiple document uploads for document type questions
 * 
 * @param {Object} props
 * @param {Object} props.question - Question object with id, type, question text, options, requires_document, etc.
 * @param {string} props.value - Current answer value
 * @param {Array<File>} props.documents - Array of uploaded document files
 * @param {Function} props.onChange - Handler for answer changes
 * @param {Function} props.onDocumentAdd - Handler for adding a document
 * @param {Function} props.onDocumentRemove - Handler for removing a document
 * @param {number} props.currentIndex - Current question index (0-based)
 * @param {number} props.totalQuestions - Total number of questions
 * @param {boolean} props.canGoNext - Whether next button should be enabled
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
  canGoNext,
  onNext,
  onPrevious,
  onSubmit
}) => {
  const isLastQuestion = currentIndex === totalQuestions - 1;
  const isFirstQuestion = currentIndex === 0;
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

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
   * Render input based on question type
   */
  const renderInput = () => {
    switch (question.type) {
      case 'text':
        return (
          <TextField
            fullWidth
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.placeholder}
            autoFocus
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                backgroundColor: '#F0FDF4',
                fontFamily: '"Playfair Display", serif',
                fontSize: '1.1rem',
                '& fieldset': {
                  borderColor: '#A7F3D0',
                  borderWidth: '2px',
                },
                '&:hover fieldset': {
                  borderColor: '#10B981',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#10B981',
                  borderWidth: '3px',
                },
              },
            }}
          />
        );

      case 'textarea':
        return (
          <TextField
            fullWidth
            multiline
            rows={4}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.placeholder}
            autoFocus
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                backgroundColor: '#F0FDF4',
                fontFamily: '"Playfair Display", serif',
                fontSize: '1.1rem',
                '& fieldset': {
                  borderColor: '#A7F3D0',
                  borderWidth: '2px',
                },
                '&:hover fieldset': {
                  borderColor: '#10B981',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#10B981',
                  borderWidth: '3px',
                },
              },
            }}
          />
        );

      case 'radio':
        return (
          <FormControl component="fieldset" fullWidth>
            <RadioGroup
              value={value}
              onChange={(e) => onChange(e.target.value)}
            >
              {question.options.map((option) => (
                <div
                  key={option.value}
                  onClick={() => onChange(option.value)}
                  style={{
                    backgroundColor: value === option.value ? '#F0FDF4' : '#FFFFFF',
                    border: value === option.value ? '3px solid #10B981' : '2px solid #E5E7EB',
                    borderRadius: '12px',
                    padding: '1.25rem 1.5rem',
                    marginBottom: '1rem',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: value === option.value 
                      ? '0 4px 20px rgba(16, 185, 129, 0.2)' 
                      : '0 2px 8px rgba(0, 0, 0, 0.05)',
                  }}
                  onMouseEnter={(e) => {
                    if (value !== option.value) {
                      e.currentTarget.style.borderColor = '#10B981';
                      e.currentTarget.style.backgroundColor = '#F9FAFB';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (value !== option.value) {
                      e.currentTarget.style.borderColor = '#E5E7EB';
                      e.currentTarget.style.backgroundColor = '#FFFFFF';
                    }
                  }}
                >
                  <FormControlLabel
                    value={option.value}
                    control={
                      <Radio
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    }
                    label={option.label}
                    sx={{
                      width: '100%',
                      margin: 0,
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        fontSize: '1.1rem',
                        fontWeight: '600',
                        color: '#1a1a1a',
                        flex: 1,
                      },
                    }}
                  />
                </div>
              ))}
            </RadioGroup>
          </FormControl>
        );

      case 'document':
        return (
          <div>
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

      default:
        return null;
    }
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
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0)',
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
        Soru {currentIndex + 1} / {totalQuestions}
      </div>

      {/* Question Text */}
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
        {question.question || question.title}
      </h2>

      {/* Description */}
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

      {/* Additional Info Chips */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
        {question.priority_score && getPriorityInfo(question.priority_score) && (() => {
          const priorityInfo = getPriorityInfo(question.priority_score);
          const PriorityIcon = priorityInfo.Icon;
          return (
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
          );
        })()}
        {question.mandatory && (
          <Chip 
            label="Zorunlu" 
            size="small"
            sx={{
              backgroundColor: '#FEE2E2',
              color: '#DC2626',
              fontFamily: '"Playfair Display", serif',
              fontWeight: '600'
            }}
          />
        )}
        {question.estimated_duration && (
          <Chip 
            icon={<ScheduleIcon sx={{ fontSize: 16 }} />}
            label={question.estimated_duration}
            size="small"
            sx={{
              backgroundColor: '#E0E7FF',
              color: '#4F46E5',
              fontFamily: '"Playfair Display", serif',
              '& .MuiChip-icon': {
                color: '#4F46E5'
              }
            }}
          />
        )}
        {question.cost_estimate && (
          <Chip 
            icon={<EuroIcon sx={{ fontSize: 16 }} />}
            label={question.cost_estimate}
            size="small"
            sx={{
              backgroundColor: '#FEF3C7',
              color: '#D97706',
              fontFamily: '"Playfair Display", serif',
              '& .MuiChip-icon': {
                color: '#D97706'
              }
            }}
          />
        )}
      </div>

      {/* Helpful Tips */}
      {question.helpful_tips && question.helpful_tips.length > 0 && (
        <div style={{
          backgroundColor: '#F0FDF4',
          border: '1px solid #A7F3D0',
          borderRadius: '12px',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '0.5rem'
          }}>
            <LightbulbIcon sx={{ fontSize: 20, color: '#059669' }} />
            <p style={{
              fontSize: '0.9rem',
              fontWeight: '600',
              color: '#059669',
              margin: 0,
              fontFamily: '"Playfair Display", serif',
            }}>
              Faydalı İpuçları:
            </p>
          </div>
          <ul style={{
            margin: 0,
            paddingLeft: '1.5rem',
            color: '#047857',
            fontFamily: '"Playfair Display", serif',
            fontSize: '0.9rem'
          }}>
            {question.helpful_tips.map((tip, idx) => (
              <li key={idx} style={{ marginBottom: '0.25rem' }}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Input Field */}
      <div style={{ marginBottom: '1.5rem' }}>
        {renderInput()}
      </div>

      {/* Source URLs */}
      {question.source_urls && question.source_urls.length > 0 && (
        <div style={{
          backgroundColor: '#F9FAFB',
          border: '1px solid #E5E7EB',
          borderRadius: '12px',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '0.75rem'
          }}>
            <LinkIcon sx={{ fontSize: 16, color: '#6B7280' }} />
            <p style={{
              fontSize: '0.85rem',
              fontWeight: '600',
              color: '#6B7280',
              margin: 0,
              fontFamily: '"Playfair Display", serif',
            }}>
              Kaynaklar
            </p>
          </div>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}>
            {question.source_urls.slice(0, 3).map((url, idx) => (
              <a
                key={idx}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontSize: '0.8rem',
                  color: '#3B82F6',
                  textDecoration: 'none',
                  fontFamily: '"Playfair Display", serif',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  display: 'block',
                  transition: 'color 0.2s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#2563EB'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#3B82F6'}
              >
                {url.length > 60 ? url.substring(0, 60) + '...' : url}
              </a>
            ))}
            {question.source_urls.length > 3 && (
              <p style={{
                fontSize: '0.75rem',
                color: '#9CA3AF',
                margin: 0,
                fontFamily: '"Playfair Display", serif',
              }}>
                +{question.source_urls.length - 3} kaynak daha
              </p>
            )}
          </div>
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
            disabled={!canGoNext}
            endIcon={<ArrowForward />}
            sx={{
              background: canGoNext 
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : '#CCCCCC',
              color: '#FFFFFF',
              padding: '0.875rem 2rem',
              borderRadius: '50px',
              fontSize: '1rem',
              fontWeight: '700',
              textTransform: 'none',
              fontFamily: '"Playfair Display", serif',
              boxShadow: canGoNext 
                ? '0 6px 20px rgba(16, 185, 129, 0.4)'
                : 'none',
              '&:hover': {
                background: canGoNext 
                  ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                  : '#CCCCCC',
                transform: canGoNext ? 'translateY(-2px)' : 'none',
                boxShadow: canGoNext 
                  ? '0 8px 25px rgba(16, 185, 129, 0.5)'
                  : 'none',
              },
              '&:disabled': {
                cursor: 'not-allowed',
              },
              transition: 'all 0.3s ease',
            }}
          >
            İleri
          </Button>
        ) : (
          <Button
            onClick={onSubmit}
            disabled={!canGoNext}
            endIcon={<Send />}
            sx={{
              background: canGoNext 
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : '#CCCCCC',
              color: '#FFFFFF',
              padding: '0.875rem 2rem',
              borderRadius: '50px',
              fontSize: '1rem',
              fontWeight: '700',
              textTransform: 'none',
              fontFamily: '"Playfair Display", serif',
              boxShadow: canGoNext 
                ? '0 6px 20px rgba(16, 185, 129, 0.4)'
                : 'none',
              '&:hover': {
                background: canGoNext 
                  ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
                  : '#CCCCCC',
                transform: canGoNext ? 'translateY(-2px)' : 'none',
                boxShadow: canGoNext 
                  ? '0 8px 25px rgba(16, 185, 129, 0.5)'
                  : 'none',
              },
              '&:disabled': {
                cursor: 'not-allowed',
              },
              transition: 'all 0.3s ease',
            }}
          >
            Gönder
          </Button>
        )}
      </div>
    </div>
  );
};

export default QuestionCard;

