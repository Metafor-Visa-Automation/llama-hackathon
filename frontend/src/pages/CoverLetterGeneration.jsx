import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion'; // eslint-disable-line no-unused-vars
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';
import {
  ArrowBack,
  Edit as EditIcon,
  Download as DownloadIcon,
  AutoAwesome as AutoAwesomeIcon,
  CheckCircle as CheckCircleIcon,
  FlightTakeoff as FlightTakeoffIcon,
  Stars as StarsIcon,
  Lightbulb as LightbulbIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { Snackbar, Alert } from '@mui/material';
import { resetApplication } from '../store/applicationSlice';

/**
 * CoverLetterGeneration Page Component
 * Generates and displays AI-powered cover letter for visa application
 * Features editable text area and download functionality
 */
const CoverLetterGeneration = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { token } = useSelector((state) => state.auth);
  const { application } = useSelector((state) => state.application);

  // Get application_id from navigation state
  const applicationId = location.state?.application_id || application?.app_id;
  const applicationName = location.state?.application_name || application?.application_name;

  const [isLoading, setIsLoading] = useState(false);
  const [coverLetter, setCoverLetter] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [toastOpen, setToastOpen] = useState(false);
  const [error, setError] = useState(null);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerated, setIsGenerated] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('tr');

  // Show success toast if application was just saved
  useEffect(() => {
    if (application && application.app_id) {
      setToastOpen(true);

      // Reset application state after showing the message
      const timer = setTimeout(() => {
        dispatch(resetApplication());
      }, 6000); // After toast disappears

      return () => clearTimeout(timer);
    }
  }, [application, dispatch]);

  // Generate cover letter via API (triggered by button click)
  const handleGenerateCoverLetter = async () => {
    // Check if we have application_id
    if (!applicationId) {
      console.error('❌ Application ID is missing');
      console.log('📋 Location state:', location.state);
      console.log('📋 Application from Redux:', application);
      setError('Başvuru ID\'si bulunamadı. Lütfen tekrar deneyin.');
      return;
    }

    try {
      console.log('═══════════════════════════════════════════');
      console.log('🚀 COVER LETTER GENERATION STARTED');
      console.log('═══════════════════════════════════════════');

      setIsLoading(true);
      setError(null);
      setGenerationProgress(0);

      // Simulate progress animation
      const progressInterval = setInterval(() => {
        setGenerationProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      console.log('📋 Request Parameters:');
      console.log('  └─ Application ID:', applicationId);
      console.log('  └─ Application Name:', applicationName);
      console.log('  └─ Language:', selectedLanguage);
      console.log('  └─ Custom Instructions:', customInstructions || '(boş)');
      console.log('  └─ Token:', token ? '✓ Mevcut' : '✗ Eksik');

      // Prepare application_data from Redux store
      const applicationData = application ? {
        user_id: application.user_id,
        application_name: application.application_name,
        country_code: application.country_code,
        travel_purpose: application.travel_purpose,
        application_start_date: application.application_start_date,
        application_end_date: application.application_end_date,
        application_type: application.application_type,
        status: application.status,
        application_steps: application.application_steps,
        created_at: application.created_at,
        updated_at: application.updated_at
      } : {};

      console.log('📦 Application Data from Redux:', JSON.stringify(applicationData, null, 2));

      const requestBody = {
        application_id: applicationId,
        application_data: applicationData,
        letter_type: 'cover_letter',
        language: selectedLanguage,
        custom_instructions: customInstructions
      };

      console.log('📤 Request Body:', JSON.stringify(requestBody, null, 2));

      const requestUrl = '/api/v1/letters/generate';
      console.log('🔗 Request URL:', requestUrl);

      const startTime = Date.now();
      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'accept': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      const responseTime = Date.now() - startTime;
      console.log(`⏱️  Response Time: ${responseTime}ms`);

      clearInterval(progressInterval);
      setGenerationProgress(100);

      console.log('📥 Response Status:', response.status, response.statusText);
      console.log('📥 Response Headers:', Object.fromEntries(response.headers.entries()));

      const data = await response.json();
      console.log('📥 Response Data:', JSON.stringify(data, null, 2));

      if (response.ok && data.letter_content) {
        console.log('✅ Cover letter generated successfully');
        console.log('📄 Letter length:', data.letter_content.length, 'characters');
        setCoverLetter(data.letter_content);
        setIsGenerated(true);
        setIsLoading(false);
        console.log('═══════════════════════════════════════════');
        console.log('✅ COVER LETTER GENERATION COMPLETED');
        console.log('═══════════════════════════════════════════');
      } else {
        throw new Error(data.detail || data.message || 'Niyet mektubu oluşturulamadı');
      }
    } catch (err) {
      console.error('═══════════════════════════════════════════');
      console.error('❌ COVER LETTER GENERATION FAILED');
      console.error('═══════════════════════════════════════════');
      console.error('Error Type:', err.name);
      console.error('Error Message:', err.message);
      console.error('Error Stack:', err.stack);
      setError(err.message || 'Bir hata oluştu. Lütfen tekrar deneyin.');
      setIsLoading(false);
      setGenerationProgress(0);
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([coverLetter], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'niyet-mektubu.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleToastClose = () => {
    setToastOpen(false);
  };

  return (
    <PageTransition>
      <Snackbar
        open={toastOpen}
        autoHideDuration={6000}
        onClose={handleToastClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleToastClose} severity="success" sx={{ width: '100%', fontFamily: '"Playfair Display", serif' }}>
          '{application?.application_name}' başvurunuz başarıyla kaydedildi!
        </Alert>
      </Snackbar>
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
            onClick={() => navigate('/dashboard')}
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
        <div style={{
          maxWidth: '1400px',
          width: '100%',
          display: 'grid',
          gridTemplateColumns: '380px 1fr',
          gap: '2rem',
          alignItems: 'start'
        }}>
          {/* Left Side - Info Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            style={{
              position: 'sticky',
              top: '2rem'
            }}
          >
            {/* Custom Instructions Card - Show before generation */}
            {!isGenerated && !isLoading && !error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.98)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  borderRadius: '24px',
                  padding: '2rem',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.8)',
                  marginBottom: '1.5rem'
                }}
              >
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: '700',
                  color: '#1a1a1a',
                  marginBottom: '1rem',
                  fontFamily: '"Playfair Display", serif',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <AutoAwesomeIcon sx={{ fontSize: 24, color: '#10B981' }} />
                  Niyet Mektubu Oluştur
                </h3>

                <p style={{
                  fontSize: '0.95rem',
                  color: '#666666',
                  marginBottom: '1.5rem',
                  fontFamily: '"Playfair Display", serif',
                  lineHeight: '1.6'
                }}>
                  AI başvurunuza özel profesyonel bir niyet mektubu oluşturacak. İsterseniz özel talimatlar ekleyebilirsiniz.
                </p>

                {/* Language Selection */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    color: '#1a1a1a',
                    marginBottom: '0.5rem',
                    fontFamily: '"Playfair Display", serif'
                  }}>
                    Dil Seçimi
                  </label>
                  <select
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      fontSize: '0.875rem',
                      fontFamily: '"Playfair Display", serif',
                      color: '#1a1a1a',
                      backgroundColor: '#F9FAFB',
                      border: '2px solid #E5E7EB',
                      borderRadius: '12px',
                      outline: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#10B981';
                      e.target.style.backgroundColor = '#F0FDF4';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#E5E7EB';
                      e.target.style.backgroundColor = '#F9FAFB';
                    }}
                  >
                    <option value="tr">🇹🇷 Türkçe</option>
                    <option value="en">🇬🇧 English</option>
                    <option value="de">🇩🇪 Deutsch</option>
                    <option value="fr">🇫🇷 Français</option>
                    <option value="es">🇪🇸 Español</option>
                    <option value="it">🇮🇹 Italiano</option>
                    <option value="pt">🇵🇹 Português</option>
                    <option value="nl">🇳🇱 Nederlands</option>
                    <option value="ar">🇸🇦 العربية</option>
                    <option value="zh">🇨🇳 中文</option>
                    <option value="ja">🇯🇵 日本語</option>
                    <option value="ko">🇰🇷 한국어</option>
                    <option value="ru">🇷🇺 Русский</option>
                  </select>
                </div>

                {/* Custom Instructions Input */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    color: '#1a1a1a',
                    marginBottom: '0.5rem',
                    fontFamily: '"Playfair Display", serif'
                  }}>
                    Özel Talimatlar (İsteğe Bağlı)
                  </label>
                  <textarea
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    placeholder="Örn: Mektubun daha resmi olmasını istiyorum, iş deneyimlerimi vurgula, vs..."
                    style={{
                      width: '100%',
                      minHeight: '120px',
                      padding: '0.75rem',
                      fontSize: '0.875rem',
                      lineHeight: '1.6',
                      fontFamily: '"Playfair Display", serif',
                      color: '#1a1a1a',
                      backgroundColor: '#F9FAFB',
                      border: '2px solid #E5E7EB',
                      borderRadius: '12px',
                      resize: 'vertical',
                      outline: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#10B981';
                      e.target.style.backgroundColor = '#F0FDF4';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#E5E7EB';
                      e.target.style.backgroundColor = '#F9FAFB';
                    }}
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateCoverLetter}
                  disabled={!applicationId}
                  style={{
                    width: '100%',
                    background: applicationId
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                      : '#E5E7EB',
                    color: applicationId ? '#FFFFFF' : '#9CA3AF',
                    padding: '1rem 2rem',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '700',
                    fontFamily: '"Playfair Display", serif',
                    border: 'none',
                    cursor: applicationId ? 'pointer' : 'not-allowed',
                    boxShadow: applicationId ? '0 4px 12px rgba(16, 185, 129, 0.3)' : 'none',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem'
                  }}
                  onMouseEnter={(e) => {
                    if (applicationId) {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (applicationId) {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
                    }
                  }}
                >
                  <AutoAwesomeIcon sx={{ fontSize: 20 }} />
                  Niyet Mektubu Oluştur
                </button>

                {!applicationId && (
                  <p style={{
                    fontSize: '0.75rem',
                    color: '#EF4444',
                    marginTop: '0.5rem',
                    textAlign: 'center',
                    fontFamily: '"Playfair Display", serif'
                  }}>
                    Başvuru ID'si bulunamadı
                  </p>
                )}
              </motion.div>
            )}

            {/* AI Generation Status Card */}
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              borderRadius: '24px',
              padding: '2rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.8)',
              marginBottom: '1.5rem',
              position: 'relative',
              overflow: 'hidden',
              display: (isLoading || error || isGenerated) ? 'block' : 'none'
            }}>
              <AnimatePresence mode="wait">
                {error ? (
                  <motion.div
                    key="error"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    {/* Icon */}
                    <div style={{
                      width: '64px',
                      height: '64px',
                      borderRadius: '50%',
                      backgroundColor: '#FEF2F2',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.5rem',
                      border: '3px solid #FCA5A5'
                    }}>
                      <ErrorIcon sx={{ fontSize: 32, color: '#EF4444' }} />
                    </div>

                    {/* Title */}
                    <h2 style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: '#1a1a1a',
                      marginBottom: '0.75rem',
                      fontFamily: '"Playfair Display", serif'
                    }}>
                      Hata Oluştu
                    </h2>

                    {/* Description */}
                    <p style={{
                      fontSize: '1rem',
                      color: '#666666',
                      marginBottom: '1rem',
                      fontFamily: '"Playfair Display", serif',
                      lineHeight: '1.6'
                    }}>
                      {error}
                    </p>

                    <button
                      onClick={() => navigate('/dashboard')}
                      style={{
                        backgroundColor: '#EF4444',
                        color: '#FFFFFF',
                        padding: '0.75rem 1.5rem',
                        borderRadius: '12px',
                        fontSize: '0.95rem',
                        fontWeight: '600',
                        fontFamily: '"Playfair Display", serif',
                        border: 'none',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        width: '100%'
                      }}
                    >
                      Dashboard'a Dön
                    </button>
                  </motion.div>
                ) : isLoading ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    {/* Icon */}
                    <div style={{
                      width: '64px',
                      height: '64px',
                      borderRadius: '50%',
                      backgroundColor: '#F0FDF4',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.5rem',
                      border: '3px solid #A7F3D0',
                      animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                    }}>
                      <AutoAwesomeIcon sx={{ fontSize: 32, color: '#10B981' }} />
                    </div>

                    {/* Title */}
                    <h2 style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: '#1a1a1a',
                      marginBottom: '0.75rem',
                      fontFamily: '"Playfair Display", serif'
                    }}>
                      Hazırlanıyor...
                    </h2>

                    {/* Description */}
                    <p style={{
                      fontSize: '1rem',
                      color: '#666666',
                      marginBottom: '1rem',
                      fontFamily: '"Playfair Display", serif',
                      lineHeight: '1.6'
                    }}>
                      AI başvurunuza özel niyet mektubu oluşturuyor. Bu işlem birkaç saniye sürecektir.
                    </p>

                    {/* Progress Bar */}
                    <div style={{
                      width: '100%',
                      height: '8px',
                      backgroundColor: '#E5E7EB',
                      borderRadius: '999px',
                      overflow: 'hidden',
                      marginTop: '1rem'
                    }}>
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${generationProgress}%` }}
                        transition={{ duration: 0.3 }}
                        style={{
                          height: '100%',
                          background: 'linear-gradient(90deg, #10B981 0%, #059669 100%)',
                          borderRadius: '999px'
                        }}
                      />
                    </div>

                    <p style={{
                      fontSize: '0.875rem',
                      color: '#10B981',
                      marginTop: '0.5rem',
                      textAlign: 'center',
                      fontFamily: '"Playfair Display", serif',
                      fontWeight: '600'
                    }}>
                      %{generationProgress}
                    </p>
                  </motion.div>
                ) : (
                  <motion.div
                    key="ready"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    {/* Icon */}
                    <div style={{
                      width: '64px',
                      height: '64px',
                      borderRadius: '50%',
                      backgroundColor: '#DCFCE7',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.5rem',
                      border: '3px solid #10B981'
                    }}>
                      <CheckCircleIcon sx={{ fontSize: 32, color: '#059669' }} />
                    </div>

                    {/* Title */}
                    <h2 style={{
                      fontSize: '1.5rem',
                      fontWeight: '700',
                      color: '#1a1a1a',
                      marginBottom: '0.75rem',
                      fontFamily: '"Playfair Display", serif',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      Hazır!
                      <StarsIcon sx={{ fontSize: 24, color: '#10B981' }} />
                    </h2>

                    {/* Description */}
                    <p style={{
                      fontSize: '1rem',
                      color: '#666666',
                      marginBottom: 0,
                      fontFamily: '"Playfair Display", serif',
                      lineHeight: '1.6'
                    }}>
                      Niyet mektubunuz başarıyla oluşturuldu. İstediğiniz gibi düzenleyebilirsiniz.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Tips Card */}
            {!isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.98)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  borderRadius: '24px',
                  padding: '2rem',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.8)'
                }}
              >
                <h3 style={{
                  fontSize: '1.1rem',
                  fontWeight: '700',
                  color: '#1a1a1a',
                  marginBottom: '1rem',
                  fontFamily: '"Playfair Display", serif',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <LightbulbIcon sx={{ fontSize: 20, color: '#D97706' }} />
                  İpuçları
                </h3>
                
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem'
                }}>
                  {[
                    'Kişisel bilgilerinizi [parantez] içindeki alanlara ekleyin',
                    'Resmi ve saygılı bir dil kullanın',
                    'Türkiye\'ye dönüş bağlarınızı vurgulayın',
                    'Ekonomik durumunuzu net ifade edin'
                  ].map((tip, index) => (
                    <li key={index} style={{
                      fontSize: '0.9rem',
                      color: '#666666',
                      fontFamily: '"Playfair Display", serif',
                      paddingLeft: '1.5rem',
                      position: 'relative',
                      lineHeight: '1.5'
                    }}>
                      <span style={{
                        position: 'absolute',
                        left: 0,
                        color: '#10B981',
                        fontWeight: '700'
                      }}>•</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </motion.div>

          {/* Right Side - Cover Letter Editor */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              borderRadius: '24px',
              padding: '2.5rem',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.8)',
              minHeight: '600px',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {/* Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '2rem',
              paddingBottom: '1.5rem',
              borderBottom: '2px solid #F0FDF4'
            }}>
              <div>
                <h1 style={{
                  fontSize: '2rem',
                  fontWeight: '700',
                  color: '#1a1a1a',
                  marginBottom: '0.25rem',
                  fontFamily: '"Playfair Display", serif',
                }}>
                  Niyet Mektubu
                </h1>
                <p style={{
                  fontSize: '0.95rem',
                  color: '#666666',
                  margin: 0,
                  fontFamily: '"Playfair Display", serif',
                }}>
                  AI tarafından oluşturuldu • Düzenlenebilir
                </p>
              </div>

              {!isLoading && (
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={() => setIsEditing(!isEditing)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      backgroundColor: isEditing ? '#F0FDF4' : '#FFFFFF',
                      color: isEditing ? '#059669' : '#666666',
                      padding: '0.75rem 1.5rem',
                      borderRadius: '50px',
                      fontSize: '0.95rem',
                      fontWeight: '600',
                      fontFamily: '"Playfair Display", serif',
                      border: `2px solid ${isEditing ? '#10B981' : '#E5E7EB'}`,
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (!isEditing) {
                        e.currentTarget.style.borderColor = '#10B981';
                        e.currentTarget.style.backgroundColor = '#F9FAFB';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isEditing) {
                        e.currentTarget.style.borderColor = '#E5E7EB';
                        e.currentTarget.style.backgroundColor = '#FFFFFF';
                      }
                    }}
                  >
                    <EditIcon sx={{ fontSize: 18 }} />
                    {isEditing ? 'Düzenleniyor' : 'Düzenle'}
                  </button>

                  <button
                    onClick={handleDownload}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      color: '#FFFFFF',
                      padding: '0.75rem 1.5rem',
                      borderRadius: '50px',
                      fontSize: '0.95rem',
                      fontWeight: '700',
                      fontFamily: '"Playfair Display", serif',
                      border: 'none',
                      cursor: 'pointer',
                      boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
                    }}
                  >
                    <DownloadIcon sx={{ fontSize: 18 }} />
                    İndir
                  </button>
                </div>
              )}
            </div>

            {/* Cover Letter Content */}
            <div style={{ flex: 1, position: 'relative' }}>
              <AnimatePresence mode="wait">
                {!isGenerated && !isLoading ? (
                  // Initial State - Not Generated Yet
                  <motion.div
                    key="not-generated"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      minHeight: '500px',
                      textAlign: 'center'
                    }}
                  >
                    <div style={{
                      width: '120px',
                      height: '120px',
                      borderRadius: '50%',
                      backgroundColor: '#F0FDF4',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '2rem',
                      border: '4px solid #A7F3D0'
                    }}>
                      <AutoAwesomeIcon sx={{ fontSize: 60, color: '#10B981' }} />
                    </div>

                    <h2 style={{
                      fontSize: '2rem',
                      fontWeight: '700',
                      color: '#1a1a1a',
                      marginBottom: '1rem',
                      fontFamily: '"Playfair Display", serif'
                    }}>
                      Niyet Mektubunuz Burada Görünecek
                    </h2>

                    <p style={{
                      fontSize: '1.1rem',
                      color: '#666666',
                      maxWidth: '500px',
                      lineHeight: '1.8',
                      fontFamily: '"Playfair Display", serif'
                    }}>
                      Sol panelden özel talimatlarınızı girin ve "Niyet Mektubu Oluştur" butonuna basarak AI'ın sizin için profesyonel bir mektup yazmasını sağlayın.
                    </p>
                  </motion.div>
                ) : isLoading ? (
                  // Loading State
                  <motion.div
                    key="loading-content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      height: '100%',
                      minHeight: '400px'
                    }}
                  >
                    {/* Animated Dots */}
                    <div style={{
                      display: 'flex',
                      gap: '0.5rem',
                      marginBottom: '2rem'
                    }}>
                      {[0, 1, 2].map((i) => (
                        <div
                          key={i}
                          style={{
                            width: '12px',
                            height: '12px',
                            borderRadius: '50%',
                            backgroundColor: '#10B981',
                            animation: `bounce 1.4s infinite ease-in-out ${i * 0.16}s`
                          }}
                        />
                      ))}
                    </div>

                    <p style={{
                      fontSize: '1.5rem',
                      fontWeight: '600',
                      color: '#10B981',
                      fontFamily: '"Playfair Display", serif',
                      marginBottom: '0.5rem'
                    }}>
                      Yazılıyor...
                    </p>
                    
                    <p style={{
                      fontSize: '1rem',
                      color: '#9CA3AF',
                      fontFamily: '"Playfair Display", serif',
                    }}>
                      AI başvurunuza özel niyet mektubu oluşturuyor
                    </p>
                  </motion.div>
                ) : (
                  // Content State
                  <motion.textarea
                    key="content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                    value={coverLetter}
                    onChange={(e) => setCoverLetter(e.target.value)}
                    readOnly={!isEditing}
                    style={{
                      width: '100%',
                      height: '100%',
                      minHeight: '500px',
                      padding: '1.5rem',
                      fontSize: '1rem',
                      lineHeight: '1.8',
                      fontFamily: '"Playfair Display", serif',
                      color: '#1a1a1a',
                      backgroundColor: isEditing ? '#F0FDF4' : '#FAFAFA',
                      border: isEditing ? '2px solid #10B981' : '2px solid #E5E7EB',
                      borderRadius: '12px',
                      resize: 'vertical',
                      outline: 'none',
                      transition: 'all 0.3s ease',
                      cursor: isEditing ? 'text' : 'default'
                    }}
                  />
                )}
              </AnimatePresence>
            </div>

            {/* Action Buttons */}
            {!isLoading && (
              <div style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'flex-end',
                marginTop: '1.5rem',
                paddingTop: '1.5rem',
                borderTop: '2px solid #F0FDF4'
              }}>
                <button
                  onClick={() => navigate('/dashboard')}
                  style={{
                    backgroundColor: '#FFFFFF',
                    color: '#666666',
                    padding: '0.875rem 2rem',
                    borderRadius: '50px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    fontFamily: '"Playfair Display", serif',
                    border: '2px solid #E5E7EB',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#F9FAFB';
                    e.currentTarget.style.borderColor = '#10B981';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#FFFFFF';
                    e.currentTarget.style.borderColor = '#E5E7EB';
                  }}
                >
                  Dashboard'a Dön
                </button>

                <button
                  onClick={() => navigate('/')}
                  style={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: '#FFFFFF',
                    padding: '0.875rem 2rem',
                    borderRadius: '50px',
                    fontSize: '1rem',
                    fontWeight: '700',
                    fontFamily: '"Playfair Display", serif',
                    border: 'none',
                    cursor: 'pointer',
                    boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(16, 185, 129, 0.5)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                  }}
                >
                  Tamamla
                </button>
              </div>
            )}
          </motion.div>
        </div>

        {/* CSS Animation for loading dots and pulse */}
        <style>{`
          @keyframes bounce {
            0%, 80%, 100% {
              transform: scale(0.8);
              opacity: 0.5;
            }
            40% {
              transform: scale(1.2);
              opacity: 1;
            }
          }

          @keyframes pulse {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }
        `}</style>
      </div>
    </PageTransition>
  );
};

export default CoverLetterGeneration;
