import { useNavigate } from 'react-router-dom';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg3.png';
import { ArrowBack } from '@mui/icons-material';

/**
 * CoverLetterGeneration Page Component
 * Page shown after completing the visa application form
 * Will eventually generate cover letter based on submitted information
 */
const CoverLetterGeneration = () => {
  const navigate = useNavigate();

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
          onClick={() => navigate('/dashboard')}
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
            fontSize: '1rem',
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
          <ArrowBack sx={{ fontSize: 20 }} />
          Geri Dön
        </button>

        {/* Main Content */}
        <div style={{
          maxWidth: '800px',
          width: '100%',
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRadius: '24px',
          padding: '3rem',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.8)',
          textAlign: 'center'
        }}>
          {/* Success Icon */}
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            backgroundColor: '#F0FDF4',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 2rem',
            border: '3px solid #10B981'
          }}>
            <svg 
              width="40" 
              height="40" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="#10B981" 
              strokeWidth="3" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>

          {/* Title */}
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            color: '#1a1a1a',
            marginBottom: '1rem',
            fontFamily: '"Playfair Display", serif',
          }}>
            Tebrikler! 🎉
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: '1.2rem',
            color: '#666666',
            marginBottom: '2rem',
            fontFamily: '"Playfair Display", serif',
            lineHeight: '1.6'
          }}>
            Vize başvuru formunuz başarıyla tamamlandı.
          </p>

          {/* Description */}
          <div style={{
            backgroundColor: '#F0FDF4',
            border: '1px solid #A7F3D0',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '2rem',
            textAlign: 'left'
          }}>
            <p style={{
              fontSize: '1rem',
              color: '#047857',
              margin: 0,
              fontFamily: '"Playfair Display", serif',
              lineHeight: '1.6'
            }}>
              📋 Başvurunuz kaydedildi ve işleme alındı. <br/>
              📧 Kısa süre içinde detaylı bilgilendirme e-postası alacaksınız. <br/>
              🎯 Dashboard üzerinden başvurunuzun durumunu takip edebilirsiniz.
            </p>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#FFFFFF',
                padding: '1rem 2.5rem',
                borderRadius: '50px',
                fontSize: '1.1rem',
                fontWeight: '700',
                textTransform: 'none',
                fontFamily: '"Playfair Display", serif',
                boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
                cursor: 'pointer',
                border: 'none',
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
              Dashboard'a Git
            </button>

            <button
              onClick={() => navigate('/')}
              style={{
                backgroundColor: '#FFFFFF',
                color: '#666666',
                padding: '1rem 2.5rem',
                borderRadius: '50px',
                fontSize: '1.1rem',
                fontWeight: '600',
                textTransform: 'none',
                fontFamily: '"Playfair Display", serif',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                cursor: 'pointer',
                border: '2px solid #E5E7EB',
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
              Ana Sayfa
            </button>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default CoverLetterGeneration;

