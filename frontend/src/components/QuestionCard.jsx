import { TextField, Button, Radio, RadioGroup, FormControlLabel, FormControl } from '@mui/material';
import { ArrowBack, ArrowForward, Send } from '@mui/icons-material';

/**
 * QuestionCard Component
 * Renders different question types (text, textarea, radio) in a card format
 * 
 * @param {Object} props
 * @param {Object} props.question - Question object with id, type, question text, options, etc.
 * @param {string} props.value - Current answer value
 * @param {Function} props.onChange - Handler for answer changes
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
  onChange,
  currentIndex,
  totalQuestions,
  canGoNext,
  onNext,
  onPrevious,
  onSubmit
}) => {
  const isLastQuestion = currentIndex === totalQuestions - 1;
  const isFirstQuestion = currentIndex === 0;

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
          marginBottom: '2rem',
          fontFamily: '"Playfair Display", serif',
          lineHeight: '1.4',
        }}
      >
        {question.question}
      </h2>

      {/* Input Field */}
      <div style={{ marginBottom: '2rem' }}>
        {renderInput()}
      </div>

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

