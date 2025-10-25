import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../components/PageTransition';
import QuestionCard from '../components/QuestionCard';
import vibeBg from '../assets/vibe-bg3.png';
import { ArrowBack } from '@mui/icons-material';
// TODO: Replace with actual AI service call
import mockResponseData from '../ai_responses/response-fransa.json';

/**
 * FillForm Page Component -  Cards Style
 * One question at a time with progress tracking
 * Questions are dynamically generated from AI response (currently using mock data)
 */
const FillForm = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  // eslint-disable-next-line no-unused-vars
  const { originCountry, destinationCountry } = useSelector((state) => state.country);

  // Current question index
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [direction, setDirection] = useState(0); // For animation direction

  // Convert action_steps to questions format
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [documents, setDocuments] = useState({});

  useEffect(() => {
    // TODO: Replace this with actual AI service call
    // const fetchVisaRequirements = async () => {
    //   try {
    //     const response = await fetch('/api/visa-requirements', {
    //       method: 'POST',
    //       body: JSON.stringify({
    //         originCountry,
    //         destinationCountry
    //       })
    //     });
    //     const data = await response.json();
    //     processActionSteps(data.action_steps);
    //   } catch (error) {
    //     console.error('Error fetching visa requirements:', error);
    //   }
    // };
    // fetchVisaRequirements();

    // Using mock data for now
    if (mockResponseData && mockResponseData.action_steps) {
      processActionSteps(mockResponseData.action_steps);
    }
  }, []);

  /**
   * Process action steps from AI response into question format
   */
  const processActionSteps = (actionSteps) => {
    const processedQuestions = actionSteps.map(step => ({
      id: step.step_id,
      type: step.requires_document ? 'document' : 'textarea',
      question: step.title,
      title: step.title,
      description: step.description,
      placeholder: step.requires_document 
        ? 'Döküman yükleyiniz' 
        : 'Detaylı bilgi veriniz...',
      required: step.mandatory,
      mandatory: step.mandatory,
      requires_document: step.requires_document,
      category: step.category,
      priority_score: step.priority_score,
      estimated_duration: step.estimated_duration,
      cost_estimate: step.cost_estimate,
      detailed_instructions: step.detailed_instructions,
      common_mistakes: step.common_mistakes,
      helpful_tips: step.helpful_tips,
      source_urls: step.source_urls
    }));

    setQuestions(processedQuestions);

    // Initialize answers state
    const initialAnswers = {};
    const initialDocuments = {};
    processedQuestions.forEach(q => {
      initialAnswers[q.id] = '';
      initialDocuments[q.id] = []; // Array for multiple documents
    });
    setAnswers(initialAnswers);
    setDocuments(initialDocuments);
  };

  const totalQuestions = questions.length;
  const progress = totalQuestions > 0 ? ((currentQuestion + 1) / totalQuestions) * 100 : 0;

  const handleAnswer = (value) => {
    if (questions.length === 0) return;
    setAnswers(prev => ({
      ...prev,
      [questions[currentQuestion].id]: value
    }));
  };

  const handleDocumentAdd = (file) => {
    if (questions.length === 0) return;
    const questionId = questions[currentQuestion].id;
    setDocuments(prev => ({
      ...prev,
      [questionId]: [...(prev[questionId] || []), file]
    }));
  };

  const handleDocumentRemove = (index) => {
    if (questions.length === 0) return;
    const questionId = questions[currentQuestion].id;
    setDocuments(prev => ({
      ...prev,
      [questionId]: prev[questionId].filter((_, i) => i !== index)
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
    console.log('Form submitted:', { answers, documents });
    // TODO: Send to backend/AI for processing
    // This will include both text answers and uploaded documents
    alert('Başvurunuz başarıyla gönderildi!');
    navigate('/dashboard');
  };

  const isCurrentQuestionAnswered = () => {
    if (questions.length === 0) return false;
    
    const currentQ = questions[currentQuestion];
    
    // If it's a document question, check if at least one document is uploaded
    if (currentQ.requires_document) {
      const docs = documents[currentQ.id];
      return Array.isArray(docs) && docs.length > 0;
    }
    
    // For text/textarea questions, check if answer is provided
    const currentAnswer = answers[currentQ.id];
    return currentAnswer && currentAnswer.trim() !== '';
  };

  const canGoNext = isCurrentQuestionAnswered();

  // Show loading state while questions are being processed
  if (questions.length === 0) {
    return (
      <PageTransition>
        <div 
          className="min-h-screen flex items-center justify-center"
          style={{
            backgroundImage: `url(${vibeBg})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed'
          }}
        >
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            padding: '2rem',
            borderRadius: '24px',
            textAlign: 'center',
            fontFamily: '"Playfair Display", serif'
          }}>
            <h2 style={{ fontSize: '1.5rem', color: '#10B981', marginBottom: '1rem' }}>
              Vize gereksinimleriniz hazırlanıyor...
            </h2>
            <p style={{ color: '#666666' }}>Lütfen bekleyin</p>
          </div>
        </div>
      </PageTransition>
    );
  }

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
                  documents={documents[questions[currentQuestion].id] || []}
                  onChange={handleAnswer}
                  onDocumentAdd={handleDocumentAdd}
                  onDocumentRemove={handleDocumentRemove}
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
