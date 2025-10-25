import { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../components/PageTransition';
import QuestionCard from '../components/QuestionCard';
import ProgressStepper from '../components/ProgressStepper';
import vibeBg from '../assets/vibe-bg3.png';
import { ArrowBack, FlightTakeoff as FlightTakeoffIcon } from '@mui/icons-material';
// TODO: Replace with actual AI service call
import mockResponseData from '../ai_responses/response-final.json';
import {
  setQuestions,
  setAnswer,
  nextQuestion,
  previousQuestion,
  markQuestionComplete,
  markQuestionIncomplete,
  setFormMetadata,
} from '../store/formSlice';
import {
  createApplication,
  completeApplicationStep,
  incompleteApplicationStep,
} from '../store/applicationSlice';

/**
 * FillForm Page Component - Cards Style
 * One question at a time with progress tracking
 * Questions are dynamically generated from AI response (currently using mock data)
 * Form state managed in Redux, documents stored locally
 */
const FillForm = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  // eslint-disable-next-line no-unused-vars
  const { originCountry, destinationCountry } = useSelector((state) => state.country);
  
  // Redux state
  const { 
    questions, 
    answers, 
    currentQuestionIndex,
    completedQuestions 
  } = useSelector((state) => state.form);

  // Local state for documents (not in Redux due to size)
  const [documents, setDocuments] = useState({});
  const [direction, setDirection] = useState(0); // For animation direction
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Process action steps from AI response into question format
   */
  const processActionSteps = useCallback((responseData) => {
    const processedQuestions = responseData.action_steps.map(step => ({
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

    // Dispatch to Redux
    dispatch(setQuestions(processedQuestions));

    // Set metadata
    dispatch(setFormMetadata({
      estimatedTotalTime: responseData.estimated_total_time || '',
      estimatedTotalCost: responseData.estimated_total_cost || ''
    }));

    // Create application object in store
    dispatch(createApplication({
      mockResponseData: responseData,
      user: user,
      destinationCountry: destinationCountry
    }));

    // Initialize local documents state
    const initialDocuments = {};
    processedQuestions.forEach(q => {
      initialDocuments[q.id] = []; // Array for multiple documents
    });
    setDocuments(initialDocuments);
    setIsLoading(false);
  }, [dispatch, user, destinationCountry]);

  useEffect(() => {
    // Load questions only if not already loaded
    if (questions.length === 0) {
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
        processActionSteps(mockResponseData);
      }
    } else {
      setIsLoading(false);
    }
  }, [questions.length, processActionSteps]);

  const totalQuestions = questions.length;

  const handleAnswer = (value) => {
    if (questions.length === 0) return;
    const questionId = questions[currentQuestionIndex].id;
    dispatch(setAnswer({ questionId, value }));
    checkQuestionCompletion();
  };

  const handleDocumentAdd = (file) => {
    if (questions.length === 0) return;
    const questionId = questions[currentQuestionIndex].id;
    setDocuments(prev => ({
      ...prev,
      [questionId]: [...(prev[questionId] || []), file]
    }));
    // Check if question is now complete
    setTimeout(() => checkQuestionCompletion(), 100);
  };

  const handleDocumentRemove = (index) => {
    if (questions.length === 0) return;
    const questionId = questions[currentQuestionIndex].id;
    setDocuments(prev => ({
      ...prev,
      [questionId]: prev[questionId].filter((_, i) => i !== index)
    }));
    // Check if question is still complete
    setTimeout(() => checkQuestionCompletion(), 100);
  };

  /**
   * Check if current question is complete and mark it
   */
  const checkQuestionCompletion = () => {
    if (questions.length === 0) return;

    const currentQ = questions[currentQuestionIndex];
    const questionId = currentQ.id;

    let isComplete = false;

    if (currentQ.requires_document) {
      const docs = documents[questionId];
      isComplete = Array.isArray(docs) && docs.length > 0;
    } else {
      const answer = answers[questionId];
      // Handle boolean values (for checkboxes)
      if (typeof answer === 'boolean') {
        isComplete = answer;
      } else {
        // Handle string values (for text inputs)
        isComplete = answer && typeof answer === 'string' && answer.trim() !== '';
      }
    }

    if (isComplete) {
      dispatch(markQuestionComplete(currentQuestionIndex));
      // Also update the application step
      dispatch(completeApplicationStep(questionId));
    } else {
      dispatch(markQuestionIncomplete(currentQuestionIndex));
      // Also update the application step
      dispatch(incompleteApplicationStep(questionId));
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < totalQuestions - 1) {
      setDirection(1);
      dispatch(nextQuestion());
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setDirection(-1);
      dispatch(previousQuestion());
    }
  };

  const handleSubmit = () => {
    console.log('Form submitted:', { answers, documents });
    // TODO: Send to backend/AI for processing
    // This will include both text answers and uploaded documents
    navigate('/cover-letter-generation');
  };

  const isCurrentQuestionAnswered = () => {
    if (questions.length === 0) return false;
    
    const currentQ = questions[currentQuestionIndex];
    const questionId = currentQ.id;
    
    // If it's a document question, check if at least one document is uploaded
    if (currentQ.requires_document) {
      const docs = documents[questionId];
      return Array.isArray(docs) && docs.length > 0;
    }
    
    // For text/textarea questions, check if answer is provided
    const currentAnswer = answers[questionId];
    // Handle boolean values (for checkboxes)
    if (typeof currentAnswer === 'boolean') {
      return currentAnswer;
    }
    // Handle string values (for text inputs)
    return currentAnswer && typeof currentAnswer === 'string' && currentAnswer.trim() !== '';
  };

  const canGoNext = isCurrentQuestionAnswered();

  // Show loading state while questions are being processed
  if (isLoading || questions.length === 0) {
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
        {/* Back Button & Visa Flow Branding */}
        <div style={{
          position: 'fixed',
          top: '2rem',
          left: '2rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          zIndex: 100
        }}>
          <button
            onClick={() => navigate('/')}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '48px',
              height: '48px',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              borderRadius: '50%',
              border: '1px solid rgba(255, 255, 255, 0.8)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              color: '#1a1a1a'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateX(-5px)';
              e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateX(0)';
              e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.15)';
            }}
          >
            <ArrowBack sx={{ fontSize: 24 }} />
          </button>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span style={{
              fontStyle: 'italic',
              fontSize: '2rem',
              color: '#064E3B',
              fontWeight: '400',
              textShadow: '0 2px 10px rgba(255, 255, 255, 0.8)'
            }}>
              visa flow
            </span>
            <FlightTakeoffIcon sx={{ 
              fontSize: 32, 
              color: '#064E3B',
              paddingTop: '0.3rem',
              filter: 'drop-shadow(0 2px 10px rgba(255, 255, 255, 0.8))'
            }} />
          </div>
        </div>

        {/* Main Container */}
        <div style={{ maxWidth: '800px', width: '100%', margin: '0 auto' }}>
          {/* Welcome Header - Only show on first question */}
          {currentQuestionIndex === 0 && (
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
                key={currentQuestionIndex}
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
                  question={questions[currentQuestionIndex]}
                  value={answers[questions[currentQuestionIndex].id]}
                  documents={documents[questions[currentQuestionIndex].id] || []}
                  onChange={handleAnswer}
                  onDocumentAdd={handleDocumentAdd}
                  onDocumentRemove={handleDocumentRemove}
                  currentIndex={currentQuestionIndex}
                  totalQuestions={totalQuestions}
                  canGoNext={canGoNext}
                  onNext={handleNext}
                  onPrevious={handlePrevious}
                  onSubmit={handleSubmit}
                />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Progress Stepper at Bottom */}
          <ProgressStepper
            questions={questions}
            currentIndex={currentQuestionIndex}
            completedQuestions={completedQuestions}
            documents={documents}
          />
        </div>
      </div>
    </PageTransition>
  );
};

export default FillForm;
