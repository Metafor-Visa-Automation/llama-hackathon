import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import InteractiveWorldMap from '../components/InteractiveWorldMap';
import ProcessSteps from '../components/ProcessSteps';
import vibeBg from '../assets/vibe-bg1.webp';

/**
 * Landing Page Component for Visa Flow
 * Main landing page with interactive world map and application flow
 */
const Landing = () => {
  /**
   * Handles the "Start Application" button click
   * @param {Object} data - Contains originCountry and destinationCountry
   */
  const handleStartApplication = (data) => {
    console.log('Starting application from:', data.originCountry, 'to:', data.destinationCountry);
    // TODO: Navigate to application page
  };

  return (
    <>
      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              transform: scale(1);
              box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
            }
            50% {
              transform: scale(1.02);
              box-shadow: 0 6px 30px rgba(16, 185, 129, 0.5);
            }
          }
        `}
      </style>
      <div className="min-h-screen" style={{
        backgroundImage: `url(${vibeBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}>
      {/* Hero Section - Split Layout */}
      <section style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: '4rem' }}>
        <div className="container mx-auto px-8">
          <div style={{ display: 'grid', gridTemplateColumns: '0.85fr 1.15fr', gap: '3rem', alignItems: 'center' }}>
            {/* Left Side - Text Content */}
            <div>
              {/* Brand Badge - Eye-Catching with Green Theme */}
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  padding: '0.6rem 1.5rem',
                  borderRadius: '50px',
                  marginBottom: '1.5rem',
                  boxShadow: '0 4px 20px rgba(16, 185, 129, 0.3)',
                  animation: 'pulse 2s ease-in-out infinite'
                }}
              >
                <FlightTakeoffIcon sx={{ fontSize: 20, color: '#FFFFFF' }} />
                <span
                  style={{
                    fontSize: '0.95rem',
                    fontWeight: '700',
                    color: '#FFFFFF',
                    letterSpacing: '0.12em',
                    textTransform: 'uppercase'
                  }}
                >
                  Visa Flow
                </span>
              </div>

              {/* Main Hero Headline - Bold & Attention-Grabbing */}
              <h1
                style={{
                  fontSize: '4rem',
                  fontWeight: '800',
                  color: '#1a1a1a',
                  marginBottom: '1.5rem',
                  lineHeight: '1.1',
                  letterSpacing: '-0.03em'
                }}
              >
                Vize Belgelerinizi{' '}
                <span
                  style={{
                    background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}
                >
                  10 Dakikada
                </span>{' '}
                Oluşturun!
              </h1>

              {/* Supporting Text */}
              <p
                style={{
                  fontSize: '1.25rem',
                  color: '#666666',
                  marginBottom: '2.5rem',
                  lineHeight: '1.7',
                  fontWeight: '400',
                  maxWidth: '95%'
                }}
              >
                Yapay zeka destekli çözümümüzle vize başvuru sürecinizi basitleştirin. İhtiyacınız olan tüm belgeleri yapay zeka destekli çözümümüzle hızlıca oluşturun. Seçtiğiniz ülkeye göre özelleştirilmiş rehberlik alın.
              </p>
            </div>

            {/* Right Side - Interactive Map */}
            <div>
              <InteractiveWorldMap
                onStartApplication={handleStartApplication}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 3-Step Process Section */}
      <ProcessSteps />

      {/*
      <footer style={{ backgroundColor: '#F5F5F5', padding: '4rem 2rem', textAlign: 'center', borderTop: '1px solid #EEEEEE' }}>
        <p style={{ color: '#666666', fontSize: '0.875rem', margin: 0 }}>© 2025 Visa Flow. Tüm hakları saklıdır.</p>
      </footer>
      */}
      </div>
    </>
  );
};

export default Landing;

