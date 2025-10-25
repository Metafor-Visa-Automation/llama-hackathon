import { useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../components/PageTransition';
import QuestionCard from '../components/QuestionCard';
import vibeBg from '../assets/vibe-bg3.png';
import { ArrowBack } from '@mui/icons-material';

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
                {destinationCountry?.name ? `${destinationCountry.name} Vize Başvurunuz` : 'Vize Başvurunuz'}
              </h1>
              <p style={{
                color: '#666666',
                fontSize: '1.1rem',
                fontFamily: '"Playfair Display", serif',
              }}>
                Hoşgeldin {user?.name}, lütfen {destinationCountry?.name ? `${destinationCountry.name} vizesi için` : ''} soruları cevapla
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
              >
                <QuestionCard
                  question={questions[currentQuestion]}
                  value={answers[questions[currentQuestion].id]}
                  onChange={handleAnswer}
                  currentIndex={currentQuestion}
                  totalQuestions={totalQuestions}
                  canGoNext={canGoNext}
                  onNext={handleNext}
                  onPrevious={handlePrevious}
                  onSubmit={handleSubmit}
                />
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
