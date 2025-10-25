import { useDispatch } from 'react-redux';
import { goToQuestion } from '../store/formSlice';
import { CheckCircle, RadioButtonUnchecked, Circle } from '@mui/icons-material';

/**
 * ProgressStepper Component
 * Shows progress bar with clickable steps at the top of the form
 * 
 * @param {Object} props
 * @param {Array} props.questions - Array of questions
 * @param {number} props.currentIndex - Current question index
 * @param {Array} props.completedQuestions - Array of completed question indices
 * @param {Object} props.documents - Documents object for validation
 */
const ProgressStepper = ({ questions, currentIndex, completedQuestions, documents }) => {
  const dispatch = useDispatch();

  const handleStepClick = (index) => {
    // Allow navigation to any question (user can go back/forward freely)
    dispatch(goToQuestion(index));
  };

  const isQuestionAnswered = (question, index) => {
    return completedQuestions.includes(index);
  };

  const getStepStatus = (index) => {
    if (index === currentIndex) return 'current';
    if (completedQuestions.includes(index)) return 'completed';
    return 'pending';
  };

  const getStepColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10B981';
      case 'current':
        return '#10B981'; // Primary brand green
      case 'pending':
        return '#E5E7EB';
      default:
        return '#E5E7EB';
    }
  };

  const progress = ((completedQuestions.length) / questions.length) * 100;

  return (
    <div style={{
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(20px)',
      borderRadius: '20px',
      padding: '1.75rem 2rem',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
      border: '1px solid rgba(255, 255, 255, 0.6)',
      marginTop: '2rem',
    }}>
      {/* Progress Summary */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.25rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{
            fontFamily: '"Playfair Display", serif',
            fontSize: '0.9rem',
            fontWeight: '600',
            color: '#666666',
            letterSpacing: '0.02em'
          }}>
            İlerleme
          </span>
          <span style={{
            fontFamily: '"Playfair Display", serif',
            fontSize: '0.85rem',
            fontWeight: '500',
            color: '#9CA3AF',
          }}>
            {completedQuestions.length} / {questions.length} tamamlandı
          </span>
        </div>
        <span style={{
          fontFamily: '"Playfair Display", serif',
          fontSize: '1.1rem',
          fontWeight: '700',
          color: '#059669',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}>
          {Math.round(progress)}%
        </span>
      </div>

      {/* Stepper */}
      <div style={{
        position: 'relative'
      }}>
        {/* Progress Bar Background */}
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          right: '16px',
          height: '3px',
          backgroundColor: '#E5E7EB',
          borderRadius: '2px',
          zIndex: 1
        }}>
          {/* Progress Bar Fill */}
          <div style={{
            height: '100%',
            backgroundColor: '#10B981',
            borderRadius: '2px',
            transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            width: `${progress}%`
          }} />
        </div>

        {/* Steps */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          position: 'relative',
          zIndex: 2
        }}>
          {questions.map((question, index) => {
            const status = getStepStatus(index);
            const isCurrent = index === currentIndex;
            const isCompleted = completedQuestions.includes(index);

            return (
              <div
                key={question.id}
                onClick={() => handleStepClick(index)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  cursor: 'pointer',
                  flex: 1,
                  maxWidth: '80px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (!isCurrent) {
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                {/* Step Circle */}
                <div style={{
                  width: isCurrent ? '36px' : '32px',
                  height: isCurrent ? '36px' : '32px',
                  borderRadius: '50%',
                  backgroundColor: '#FFFFFF',
                  border: `3px solid ${getStepColor(status)}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '0.5rem',
                  transition: 'all 0.3s ease',
                  boxShadow: isCurrent ? '0 4px 12px rgba(16, 185, 129, 0.3)' : '0 2px 4px rgba(0, 0, 0, 0.1)',
                }}>
                  {isCompleted ? (
                    <CheckCircle sx={{ fontSize: 18, color: '#10B981' }} />
                  ) : isCurrent ? (
                    <Circle sx={{ fontSize: 12, color: '#10B981' }} />
                  ) : (
                    <RadioButtonUnchecked sx={{ fontSize: 16, color: '#9CA3AF' }} />
                  )}
                </div>

                {/* Step Label (only show for current) */}
                {isCurrent && (
                  <div style={{
                    fontSize: '0.7rem',
                    color: '#10B981',
                    fontWeight: '600',
                    textAlign: 'center',
                    fontFamily: '"Playfair Display", serif',
                    maxWidth: '70px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    Soru {index + 1}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ProgressStepper;

