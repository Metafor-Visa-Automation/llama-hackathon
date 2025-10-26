import { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../components/PageTransition';
import QuestionCard from '../components/QuestionCard';
import ProgressStepper from '../components/ProgressStepper';
import vibeBg from '../assets/vibe-bg3.png';
import { ArrowBack, FlightTakeoff as FlightTakeoffIcon, CheckCircle, Error, Warning, Cancel, Info } from '@mui/icons-material';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, Box } from '@mui/material';

/**
 * Get user-friendly message and styling based on document status
 */
const getDocumentStatusInfo = (analysisData) => {
  const status = analysisData?.status;
  const ocrResult = analysisData?.ocr_result;

  // Check if OCR failed
  if (ocrResult && !ocrResult.success && ocrResult.error) {
    return {
      icon: <Warning sx={{ fontSize: '2.5rem', color: '#F59E0B' }} />,
      title: 'OCR İşlemi Başarısız',
      message: 'Belgenizden metin çıkarılamadı. Lütfen belgenizin net ve okunabilir olduğundan emin olun.',
      backgroundColor: '#FFFBEB',
      borderColor: '#F59E0B',
      textColor: '#92400E'
    };
  }

  switch (status) {
    case 'VALIDATED':
    case 'APPROVED':
      return {
        icon: <CheckCircle sx={{ fontSize: '2.5rem', color: '#10B981' }} />,
        title: 'Belge Onaylandı',
        message: 'Belgeniz kontrol edildi ve uygun bulundu. İşleme devam edebilirsiniz.',
        backgroundColor: '#F0FDF4',
        borderColor: '#10B981',
        textColor: '#064E3B'
      };

    case 'REJECTED':
      return {
        icon: <Cancel sx={{ fontSize: '2.5rem', color: '#EF4444' }} />,
        title: 'Belge Reddedildi',
        message: 'Belgeniz kontrol edildi ve uygun görülmedi. Lütfen belgenizi gözden geçirin ve tekrar yükleyin.',
        backgroundColor: '#FEF2F2',
        borderColor: '#EF4444',
        textColor: '#991B1B'
      };

    case 'PENDING_VALIDATION':
      return {
        icon: <Info sx={{ fontSize: '2.5rem', color: '#3B82F6' }} />,
        title: 'Belge İnceleniyor',
        message: 'Belgeniz başarıyla yüklendi ve şu anda inceleme aşamasında.',
        backgroundColor: '#EFF6FF',
        borderColor: '#3B82F6',
        textColor: '#1E3A8A'
      };

    default:
      return {
        icon: <Info sx={{ fontSize: '2.5rem', color: '#6B7280' }} />,
        title: 'Belge Durumu',
        message: 'Belgeniz sisteme yüklendi.',
        backgroundColor: '#F9FAFB',
        borderColor: '#6B7280',
        textColor: '#1F2937'
      };
  }
};
import { saveApplication } from '../services/applicationService';
import {
  setQuestions,
  setAnswer,
  nextQuestion,
  previousQuestion,
  markQuestionComplete,
  markQuestionIncomplete,
  setFormMetadata,
  resetForm,
} from '../store/formSlice';
import {
  createApplication,
  completeApplicationStep,
  incompleteApplicationStep,
  updateApplication,
} from '../store/applicationSlice';
import { Pencil } from 'lucide-react';

/**
 * FillForm Page Component - Cards Style
 * One question at a time with progress tracking
 * Questions are dynamically generated from AI response (currently using mock data)
 * Form state managed in Redux, documents stored locally
 */
const FillForm = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user, token } = useSelector((state) => state.auth);
  const { application } = useSelector((state) => state.application);
  // eslint-disable-next-line no-unused-vars
  const { originCountry, destinationCountry } = useSelector((state) => state.country);
  const { checklistData } = useSelector((state) => state.visaChecklist);
  
  // Redux state
  const { 
    questions, 
    answers, 
    currentQuestionIndex,
    completedQuestions 
  } = useSelector((state) => state.form);

  // Local state for documents (not in Redux due to size)
  const [documents, setDocuments] = useState({});
  const [documentTypes, setDocumentTypes] = useState({}); // Store document type for each question
  const [direction, setDirection] = useState(0); // For animation direction
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false); // For document upload
  const [uploadStage, setUploadStage] = useState(''); // Track upload stage: 'uploading' or 'processing'
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [applicationName, setApplicationName] = useState('');

  // OCR Modal state
  const [ocrModalOpen, setOcrModalOpen] = useState(false);
  const [ocrResults, setOcrResults] = useState([]);

  useEffect(() => {
    if (application) {
      setApplicationName(application.application_name || `${destinationCountry?.name || 'Visa'} Application`);
    }
  }, [application, destinationCountry]);

  const handleTitleBlur = () => {
    setIsEditingTitle(false);
    dispatch(updateApplication({ application_name: applicationName }));
  };

  const handleTitleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleTitleBlur();
    }
  };

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
    const initialDocumentTypes = {};
    processedQuestions.forEach(q => {
      initialDocuments[q.id] = []; // Array for multiple documents
      initialDocumentTypes[q.id] = ''; // Initialize document type as empty
    });
    setDocuments(initialDocuments);
    setDocumentTypes(initialDocumentTypes);
    setIsLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps - captures initial values and prevents recreation

  useEffect(() => {
    // Load questions only if not already loaded
    if (questions.length === 0) {
      // Check if we have checklist data from API
      if (checklistData && checklistData.action_steps) {
        console.log('📋 Using checklist data from API:', checklistData);
        processActionSteps(checklistData);
      } else {
        console.warn('⚠️ No checklist data available, redirecting to home');
        // If no data is available, redirect to home
        navigate('/');
      }
    } else {
      setIsLoading(false);
    }
  }, [questions.length, processActionSteps, checklistData, navigate]);

  // Separate cleanup effect that only runs on unmount
  useEffect(() => {
    return () => {
      console.log('🧹 FillForm unmounting - cleaning up state');
      dispatch(resetForm());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - only runs on mount/unmount

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

  const handleDocumentTypeChange = (type) => {
    if (questions.length === 0) return;
    const questionId = questions[currentQuestionIndex].id;
    setDocumentTypes(prev => ({
      ...prev,
      [questionId]: type
    }));
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

  /**
   * Upload document to backend
   * Uses multipart/form-data with query parameters
   */
  const uploadDocument = async (file, docType) => {
    try {
      console.log('🔐 Upload Debug - Token:', token);
      console.log('👤 Upload Debug - User:', user);
      console.log('📄 Upload Debug - File:', file.name, file.type, file.size);
      console.log('🏷️ Upload Debug - Document Type:', docType);

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);

      // Use filename without extension as default document title
      const documentTitle = file.name.split('.')[0];

      // Build query parameters
      const queryParams = new URLSearchParams({
        document_type: docType || 'other',
        document_title: documentTitle,
        auto_ocr: 'true' // Enable automatic OCR processing
      });

      const uploadUrl = `/api/v1/documents/upload?${queryParams.toString()}`;
      console.log('📤 Upload URL:', uploadUrl);

      const response = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`
          // Don't set Content-Type - browser will set it with boundary for multipart/form-data
        },
        body: formData
      });

      const data = await response.json();
      console.log('📤 Upload Response Status:', response.status);
      console.log('📤 Upload Response Data:', data);

      if (response.status === 201 || response.status === 200) {
        console.log('✅ Document uploaded successfully:', data);
        return { success: true, data };
      } else {
        console.error('❌ Document upload failed:', data);
        return { success: false, error: data };
      }
    } catch (error) {
      console.error('💥 Document upload error:', error);
      return { success: false, error };
    }
  };

  /**
   * Process OCR for uploaded document
   */
  const processOCR = async (docId) => {
    try {
      console.log('🔍 Processing OCR for document:', docId);

      const response = await fetch(`/api/v1/documents/${docId}/process-ocr`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: ''
      });

      const data = await response.json();
      console.log('🔍 OCR Response Status:', response.status);
      console.log('🔍 OCR Response Data:', data);

      if (response.status === 200 || response.status === 201) {
        console.log('✅ OCR processing completed:', data);
        return { success: true, data };
      } else {
        console.error('❌ OCR processing failed:', data);
        return { success: false, error: data };
      }
    } catch (error) {
      console.error('💥 OCR processing error:', error);
      return { success: false, error };
    }
  };

  /**
   * Get OCR analysis for a document
   */
  const getOCRAnalysis = async (docId) => {
    try {
      console.log('📊 Fetching OCR analysis for document:', docId);

      const response = await fetch(`/api/v1/documents/${docId}/ocr-analysis`, {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      console.log('📊 Analysis Response Status:', response.status);
      console.log('📊 Analysis Response Data:', data);

      if (response.status === 200) {
        console.log('✅ Analysis retrieved successfully:', data);
        return { success: true, data };
      } else {
        console.error('❌ Analysis retrieval failed:', data);
        return { success: false, error: data };
      }
    } catch (error) {
      console.error('💥 Analysis retrieval error:', error);
      return { success: false, error };
    }
  };

  const handleNext = async () => {
    if (currentQuestionIndex >= totalQuestions - 1) return;

    const currentQ = questions[currentQuestionIndex];
    const questionId = currentQ.id;

    // Handle requires_document: true
    if (currentQ.requires_document) {
      const docs = documents[questionId];
      const docType = documentTypes[questionId];

      // Validate that document type is selected
      if (!docType) {
        alert('Lütfen döküman tipini seçin.');
        return;
      }

      // If there are documents to upload
      if (Array.isArray(docs) && docs.length > 0) {
        setIsUploading(true);
        setUploadStage('uploading');

        try {
          // Upload all documents for this question with the selected document type
          const uploadPromises = docs.map(doc => uploadDocument(doc, docType));
          const uploadResults = await Promise.all(uploadPromises);

          // Check if all uploads were successful
          const allUploadsSuccess = uploadResults.every(result => result.success);

          if (allUploadsSuccess) {
            console.log('✅ All documents uploaded successfully');

            // Change stage to OCR processing
            setUploadStage('processing');

            // Trigger OCR processing for all uploaded documents
            const ocrPromises = uploadResults.map(result => {
              const docId = result.data?.doc_id;
              if (docId) {
                console.log('🔍 Triggering OCR for doc_id:', docId);
                return processOCR(docId);
              }
              return Promise.resolve({ success: false, error: 'No doc_id returned' });
            });

            const ocrResultsData = await Promise.all(ocrPromises);

            // Check OCR results
            const allOCRSuccess = ocrResultsData.every(result => result.success);

            // Fetch analysis for successfully processed documents
            const analysisPromises = ocrResultsData.map(async (result, index) => {
              const docId = uploadResults[index].data?.doc_id;
              if (result.success && docId) {
                console.log('📊 Fetching analysis for doc_id:', docId);
                return await getOCRAnalysis(docId);
              }
              return { success: false, error: 'OCR processing failed or no doc_id' };
            });

            const analysisResults = await Promise.all(analysisPromises);

            // Prepare combined results for modal display
            const resultsWithFiles = ocrResultsData.map((result, index) => ({
              fileName: uploadResults[index].data?.file_name || docs[index].name,
              docId: uploadResults[index].data?.doc_id,
              success: result.success,
              ocrData: result.data,
              analysisData: analysisResults[index]?.data,
              analysisSuccess: analysisResults[index]?.success || false,
              error: result.error
            }));

            // Store results and show modal
            setOcrResults(resultsWithFiles);
            setOcrModalOpen(true);

            if (allOCRSuccess) {
              console.log('✅ All OCR processing completed successfully');
            } else {
              console.warn('⚠️ Some OCR processing failed, but continuing anyway');
            }

            // Mark step as completed regardless of OCR status
            dispatch(markQuestionComplete(currentQuestionIndex));
            dispatch(completeApplicationStep(questionId));
          } else {
            alert('Döküman yükleme başarısız. Lütfen tekrar deneyin.');
          }
        } catch (error) {
          console.error('Upload error:', error);
          alert('Döküman yükleme sırasında bir hata oluştu.');
        } finally {
          setIsUploading(false);
          setUploadStage('');
        }
      }
    }
    // Handle requires_document: false (checkmark questions)
    else {
      const answer = answers[questionId];

      // If checkmark is checked (answer is true)
      if (answer === true) {
        dispatch(markQuestionComplete(currentQuestionIndex));
        dispatch(completeApplicationStep(questionId));
      }

      // Move to next question
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

  const handleOcrModalClose = () => {
    setOcrModalOpen(false);
    // Move to next question after closing modal
    setDirection(1);
    dispatch(nextQuestion());
  };

  const handleSubmit = async () => {
    console.log('Form submitted:', { answers, documents });
    if (!application) {
      console.error("Application data is not available to submit.");
      alert("Uygulama verisi bulunamadı. Lütfen tekrar deneyin.");
      return;
    }

    setIsSubmitting(true);
    try {
      const applicationToSend = {
        application_name: application.application_name,
        country_code: application.country_code,
        travel_purpose: application.travel_purpose,
        application_start_date: application.application_start_date,
        application_end_date: application.application_end_date || new Date().toISOString(),
        application_steps: application.application_steps,
      };

      const result = await saveApplication(applicationToSend, token);

      if (result.success) {
        dispatch(updateApplication(result.data));
        // Navigate with application_id from saved result
        navigate('/cover-letter-generation', {
          state: {
            application_id: result.data.app_id,
            application_name: result.data.application_name
          }
        });
      } else {
        alert('Uygulama kaydedilemedi. Lütfen tekrar deneyin.');
        console.error("Failed to save application:", result.error);
      }
    } catch (error) {
      alert('Uygulama kaydedilirken bir hata oluştu.');
      console.error("Error during application save:", error);
    } finally {
      setIsSubmitting(false);
    }
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
        {/* Back Button & Otovize Branding */}
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
              otovize
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
              <div
                style={{
                  flex: '1',
                  textAlign: 'center',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
                  {isEditingTitle ? (
                    <input
                      type="text"
                      value={applicationName}
                      onChange={(e) => setApplicationName(e.target.value)}
                      onBlur={handleTitleBlur}
                      onKeyDown={handleTitleKeyDown}
                      autoFocus
                      style={{
                        fontSize: '2rem',
                        fontWeight: '800',
                        color: '#1a1a1a',
                        fontFamily: '"Playfair Display", serif',
                        border: 'none',
                        outline: 'none',
                        width: '100%',
                        backgroundColor: 'transparent',
                        borderBottom: '2px solid #10B981',
                      }}
                    />
                  ) : (
                    <h1
                      style={{
                        fontSize: '2rem',
                        fontWeight: '800',
                        color: '#1a1a1a',
                        marginBottom: '0.5rem',
                        fontFamily: '"Playfair Display", serif',
                      }}
                    >
                      {applicationName}
                    </h1>
                  )}
                  {!isEditingTitle && (
                    <button 
                      onClick={() => setIsEditingTitle(true)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '0.5rem',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                      className="hover:bg-gray-100 transition-colors"
                    >
                      <Pencil size={20} color="#666666" />
                    </button>
                  )}
                </div>
                <p
                  style={{
                    color: '#666666',
                    fontSize: '1rem',
                    fontFamily: '"Playfair Display", serif',
                  }}
                >
                  Hoşgeldin {user?.name}, lütfen {destinationCountry?.name ? `${destinationCountry.name} vizesi için` : ''} soruları cevapla
                </p>
              </div>
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
                  documentType={documentTypes[questions[currentQuestionIndex].id] || ''}
                  onChange={handleAnswer}
                  onDocumentAdd={handleDocumentAdd}
                  onDocumentRemove={handleDocumentRemove}
                  onDocumentTypeChange={handleDocumentTypeChange}
                  currentIndex={currentQuestionIndex}
                  totalQuestions={totalQuestions}
                  canGoNext={canGoNext}
                  onNext={handleNext}
                  onPrevious={handlePrevious}
                  onSubmit={handleSubmit}
                  isUploading={isUploading}
                  uploadStage={uploadStage}
                  isSubmitting={isSubmitting}
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

        {/* OCR Results Modal */}
        <Dialog
          open={ocrModalOpen}
          onClose={handleOcrModalClose}
          maxWidth="sm"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: '20px',
              padding: '1rem',
              fontFamily: '"Playfair Display", serif',
              backgroundColor: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
            }
          }}
        >
          <DialogTitle sx={{
            fontFamily: '"Playfair Display", serif',
            fontSize: '1.75rem',
            fontWeight: 700,
            color: '#1a1a1a',
            textAlign: 'center',
            paddingBottom: '1rem'
          }}>
            OCR İşlem Sonuçları
          </DialogTitle>

          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {ocrResults.map((result, index) => {
                // Get status info if analysis data is available
                const statusInfo = result.analysisSuccess && result.analysisData
                  ? getDocumentStatusInfo(result.analysisData)
                  : null;

                return (
                  <Box
                    key={index}
                    sx={{
                      padding: '1.5rem',
                      borderRadius: '12px',
                      backgroundColor: statusInfo?.backgroundColor || (result.success ? '#F0FDF4' : '#FEF2F2'),
                      border: `2px solid ${statusInfo?.borderColor || (result.success ? '#10B981' : '#EF4444')}`,
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '1rem'
                    }}
                  >
                    {/* Icon */}
                    <Box sx={{ flexShrink: 0, marginTop: '0.25rem' }}>
                      {statusInfo ? statusInfo.icon : (
                        result.success ? (
                          <CheckCircle sx={{ fontSize: '2rem', color: '#10B981' }} />
                        ) : result.error?.status_code === 503 ? (
                          <Warning sx={{ fontSize: '2rem', color: '#F59E0B' }} />
                        ) : (
                          <Error sx={{ fontSize: '2rem', color: '#EF4444' }} />
                        )
                      )}
                    </Box>

                    {/* Content */}
                    <Box sx={{ flex: 1 }}>
                      <Typography
                        variant="h6"
                        sx={{
                          fontFamily: '"Playfair Display", serif',
                          fontWeight: 600,
                          fontSize: '1.1rem',
                          color: '#1a1a1a',
                          marginBottom: '0.5rem'
                        }}
                      >
                        {result.fileName}
                      </Typography>

                      {result.success ? (
                        <>
                          {/* Show status info if available */}
                          {statusInfo ? (
                            <Box sx={{ marginTop: '0.5rem' }}>
                              <Typography
                                sx={{
                                  fontFamily: '"Playfair Display", serif',
                                  fontSize: '1rem',
                                  fontWeight: 700,
                                  color: statusInfo.textColor,
                                  marginBottom: '0.5rem'
                                }}
                              >
                                {statusInfo.title}
                              </Typography>
                              <Typography
                                sx={{
                                  fontFamily: '"Inter", sans-serif',
                                  fontSize: '0.875rem',
                                  color: statusInfo.textColor,
                                  lineHeight: 1.6
                                }}
                              >
                                {statusInfo.message}
                              </Typography>
                            </Box>
                          ) : (
                            <Typography
                              sx={{
                                fontFamily: '"Inter", sans-serif',
                                fontSize: '0.875rem',
                                color: '#10B981',
                                fontWeight: 600
                              }}
                            >
                              ✓ OCR işlemi başarıyla tamamlandı
                            </Typography>
                          )}

                          {result.success && !result.analysisSuccess && (
                            <Typography
                              sx={{
                                fontFamily: '"Inter", sans-serif',
                                fontSize: '0.75rem',
                                color: '#F59E0B',
                                fontStyle: 'italic',
                                marginTop: '0.5rem'
                              }}
                            >
                              ⚠️ Analiz bilgisi alınamadı
                            </Typography>
                          )}
                        </>
                      ) : (
                        <Typography
                          sx={{
                            fontFamily: '"Inter", sans-serif',
                            fontSize: '0.875rem',
                            color: result.error?.status_code === 503 ? '#F59E0B' : '#EF4444',
                            fontWeight: 500
                          }}
                        >
                          {result.error?.detail || result.error?.message || 'OCR işlemi başarısız oldu'}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </DialogContent>

          <DialogActions sx={{ padding: '1.5rem', justifyContent: 'center' }}>
            <Button
              onClick={handleOcrModalClose}
              variant="contained"
              sx={{
                fontFamily: '"Playfair Display", serif',
                fontSize: '1rem',
                fontWeight: 600,
                padding: '0.75rem 2.5rem',
                borderRadius: '12px',
                backgroundColor: '#10B981',
                color: '#FFFFFF',
                textTransform: 'none',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                '&:hover': {
                  backgroundColor: '#059669',
                  boxShadow: '0 6px 16px rgba(16, 185, 129, 0.4)',
                }
              }}
            >
              Devam Et
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    </PageTransition>
  );
};

export default FillForm;
