import { useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';
import { TextField, Button, Radio, RadioGroup, FormControlLabel, FormControl } from '@mui/material';
import { ArrowBack, ArrowForward, Send } from '@mui/icons-material';

/**
 * FillForm Page Component - Jotform Cards Style
 * One question at a time with progress tracking
 * Questions will eventually come from AI
 */
const FillForm = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  // Country selection data (will be used in future updates)
  // eslint-disable-next-line no-unused-vars
  const { originCountry, destinationCountry } = useSelector((state) => state.country);

  // Current question index
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [direction, setDirection] = useState(0); // For animation direction

  // Mock questions (will be replaced with AI-generated questions)
  const [answers, setAnswers] = useState({
    fullName: '',
    passportNumber: '',
    travelPurpose: '',
    travelDuration: '',
    accommodationInfo: '',
    previousVisas: '',
    financialStatus: ''
  });

  // Question definitions
  const questions = [
    {
      id: 'fullName',
      type: 'text',
      question: 'Tam adınız nedir?',
      placeholder: 'Örn: Ahmet Yılmaz',
      required: true
    },
    {
      id: 'passportNumber',
      type: 'text',
      question: 'Pasaport numaranız nedir?',
      placeholder: 'Örn: U12345678',
      required: true
    },
    {
      id: 'travelPurpose',
      type: 'radio',
      question: 'Seyahat amacınız nedir?',
      options: [
        { value: 'tourism', label: 'Turizm' },
        { value: 'business', label: 'İş' },
        { value: 'education', label: 'Eğitim' },
        { value: 'family', label: 'Aile Ziyareti' }
      ],
      required: true
    },
    {
      id: 'travelDuration',
      type: 'text',
      question: 'Ne kadar süreyle seyahat edeceksiniz?',
      placeholder: 'Örn: 15 gün',
      required: true
    },
    {
      id: 'accommodationInfo',
      type: 'textarea',
      question: 'Nerede kalacaksınız?',
      placeholder: 'Otel adı veya adres',
      required: true
    },
    {
      id: 'previousVisas',
      type: 'radio',
      question: 'Daha önce Schengen vizesi aldınız mı?',
      options: [
        { value: 'yes', label: 'Evet' },
        { value: 'no', label: 'Hayır' }
      ],
      required: true
    },
    {
      id: 'financialStatus',
      type: 'textarea',
      question: 'Seyahatinizi nasıl finanse edeceksiniz?',
      placeholder: 'Mali durumunuzu açıklayın',
      required: true
    }
  ];

  const totalQuestions = questions.length;
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;

  const handleAnswer = (value) => {
    setAnswers(prev => ({
      ...prev,
      [questions[currentQuestion].id]: value
    }));
  };

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setDirection(1);
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setDirection(-1);
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = () => {
    console.log('Form submitted:', answers);
    // TODO: Send to backend/AI for processing
    alert('Başvurunuz başarıyla gönderildi!');
    navigate('/');
  };

  const isCurrentQuestionAnswered = () => {
    const currentAnswer = answers[questions[currentQuestion].id];
    return currentAnswer && currentAnswer.trim() !== '';
  };

  const canGoNext = isCurrentQuestionAnswered();

  // Animation variants for card transitions
  const cardVariants = {
    enter: (direction) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      x: 0,
      opacity: 1
    },
    exit: (direction) => ({
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  };

  const renderQuestionInput = () => {
    const question = questions[currentQuestion];
    const value = answers[question.id];

    switch (question.type) {
      case 'text':
        return (
          <TextField
            fullWidth
            value={value}
            onChange={(e) => handleAnswer(e.target.value)}
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
            onChange={(e) => handleAnswer(e.target.value)}
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
              onChange={(e) => handleAnswer(e.target.value)}
            >
              {question.options.map((option) => (
                <div
                  key={option.value}
                  onClick={() => handleAnswer(option.value)}
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
    <PageTransition>
      <div 
        className="min-h-screen flex items-center justify-center px-4 py-8"
        style={{
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          style={{
            position: 'fixed',
            top: '2rem',
            left: '2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            padding: '0.75rem 1.5rem',
            borderRadius: '50px',
            border: '1px solid rgba(255, 255, 255, 0.8)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            fontFamily: '"Playfair Display", serif',
            fontWeight: '600',
            color: '#1a1a1a',
            zIndex: 100
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateX(-4px)';
            e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateX(0)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.15)';
          }}
        >
          <ArrowBack sx={{ fontSize: 20 }} />
          <span>Geri Dön</span>
        </button>

        {/* Main Container */}
        <div style={{ maxWidth: '800px', width: '100%', margin: '0 auto' }}>
          {/* Welcome Header - Only show on first question */}
          {currentQuestion === 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                textAlign: 'center',
                marginBottom: '2rem',
                backgroundColor: 'rgba(255, 255, 255, 0.85)',
                backdropFilter: 'blur(20px)',
                padding: '1.5rem',
                borderRadius: '24px',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              }}
            >
              <h1
                style={{
                  fontSize: '2rem',
                  fontWeight: '800',
                  color: '#1a1a1a',
                  marginBottom: '0.5rem',
                  fontFamily: '"Playfair Display", serif',
                }}
              >
                Vize Başvuru Formu
              </h1>
              <p style={{ 
                color: '#666666', 
                fontSize: '1.1rem',
                fontFamily: '"Playfair Display", serif',
              }}>
                Hoşgeldin {user?.name}, lütfen soruları cevaplayın
              </p>
            </motion.div>
          )}

          {/* Question Card */}
          <div style={{ overflow: 'hidden', width: '100%' }}>
            <AnimatePresence initial={false} custom={direction} mode="wait">
              <motion.div
                key={currentQuestion}
                custom={direction}
                variants={cardVariants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{
                  x: { type: "spring", stiffness: 300, damping: 30 },
                  opacity: { duration: 0.2 }
                }}
                style={{
                  width: '100%',
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '24px',
                  padding: '2.5rem',
                  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.8)',
                }}
              >
                {/* Question Number */}
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
                  Soru {currentQuestion + 1} / {totalQuestions}
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
                  {questions[currentQuestion].question}
                </h2>

                {/* Input Field */}
                <div style={{ marginBottom: '2rem' }}>
                  {renderQuestionInput()}
                </div>

                {/* Navigation Buttons */}
                <div style={{ 
                  display: 'flex', 
                  gap: '1rem',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  {/* Previous Button */}
                  {currentQuestion > 0 && (
                    <Button
                      onClick={handlePrevious}
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
                  {currentQuestion < totalQuestions - 1 ? (
                    <Button
                      onClick={handleNext}
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
                      onClick={handleSubmit}
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
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Progress Bar - Modern & Compact */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            style={{
              marginTop: '2rem',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              backdropFilter: 'blur(20px)',
              padding: '1.75rem 2rem',
              borderRadius: '20px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
              border: '1px solid rgba(255, 255, 255, 0.6)',
            }}
          >
            {/* Progress Percentage & Label */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
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
                  Soru {currentQuestion + 1} / {totalQuestions}
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
            
            {/* Question Step Indicators */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: '0.75rem',
              gap: '0.35rem'
            }}>
              {questions.map((_, index) => (
                <div
                  key={index}
                  style={{
                    flex: 1,
                    height: index === currentQuestion ? '8px' : '6px',
                    backgroundColor: index <= currentQuestion ? '#10B981' : '#E5E7EB',
                    borderRadius: '4px',
                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  }}
                />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
};

export default FillForm;
