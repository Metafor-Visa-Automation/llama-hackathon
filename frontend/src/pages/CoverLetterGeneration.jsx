import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

// Simulated AI-generated cover letter (will be replaced with actual API call)
const GENERATED_COVER_LETTER = `Sayın Konsolosluk Yetkilileri,

Ben [Adınız Soyadınız], [Mesleğiniz] olarak çalışmaktayım ve [Tarih] - [Tarih] tarihleri arasında Fransa'yı ziyaret etmeyi planlıyorum.

Seyahatimin ana amacı [turizm/iş/aile ziyareti] olup, bu süre zarfında [ziyaret edilecek yerler ve aktiviteler] gibi faaliyetlerde bulunmayı planlamaktayım.

Ekonomik durumum oldukça istikrarlıdır ve seyahat masraflarımı karşılayabilecek yeterli finansal kaynağa sahibim. Banka hesap özetlerim ve gelir belgelerim başvuru dosyamda mevcuttur.

Türkiye'de [iş yeriniz/kurumunuz] ile güçlü bağlarım bulunmaktadır. [İş pozisyonunuz] olarak [kaç yıldır] çalışmaktayım ve bu pozisyondan dolayı ülkeme dönmek zorundayım. Ayrıca, [ailevi bağlar veya diğer bağlar] nedeniyle Türkiye'ye geri dönüşüm garanti altındadır.

Seyahat sigortam, pasaport fotokopim ve diğer tüm gerekli belgeler başvuru dosyamda eksiksiz olarak yer almaktadır. Vize başvuru sürecine büyük önem veriyor ve tüm gereklilikleri eksiksiz yerine getirdiğimi düşünüyorum.

Konsolosluğunuzun değerli zamanını ayırdığı için teşekkür eder, başvurumun olumlu değerlendirilmesini saygılarımla arz ederim.

Saygılarımla,
[Adınız Soyadınız]
[Tarih]`;

/**
 * CoverLetterGeneration Page Component
 * Generates and displays AI-powered cover letter for visa application
 * Features editable text area and download functionality
 */
const CoverLetterGeneration = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [coverLetter, setCoverLetter] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // Simulate AI generation process
  useEffect(() => {
    const timer = setTimeout(() => {
      setCoverLetter(GENERATED_COVER_LETTER);
      setIsLoading(false);
    }, 3500); // 3.5 seconds for AI generation simulation

    return () => clearTimeout(timer);
  }, []);

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([coverLetter], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'niyet-mektubu.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
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
              overflow: 'hidden'
            }}>
              <AnimatePresence mode="wait">
                {isLoading ? (
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
                      border: '3px solid #A7F3D0'
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
                      marginBottom: 0,
                      fontFamily: '"Playfair Display", serif',
                      lineHeight: '1.6'
                    }}>
                      Başvurunuza en uygun niyet mektubu hazırlıyoruz. Bu işlem birkaç saniye sürecektir.
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
                {isLoading ? (
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

        {/* CSS Animation for loading dots */}
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
        `}</style>
      </div>
    </PageTransition>
  );
};

export default CoverLetterGeneration;
