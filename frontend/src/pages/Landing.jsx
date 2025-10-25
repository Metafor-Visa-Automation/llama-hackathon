import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import InteractiveWorldMap from '../components/InteractiveWorldMap';
import ProcessSteps from '../components/ProcessSteps';
import UserGreeting from '../components/UserGreeting';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';

/**
 * Landing Page Component for Visa Flow
 * Main landing page with interactive world map and application flow
 */
const Landing = () => {

  // Animation variants for hero section - Slower, more cinematic
  const badgeVariants = {
    hidden: { opacity: 0, scale: 0.8, y: -20 },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: {
        duration: 0.9,
        ease: [0.22, 1, 0.36, 1],
        delay: 0.3,
      },
    },
  };

  const headlineVariants = {
    hidden: { opacity: 0, y: 40 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 1.0,
        ease: [0.22, 1, 0.36, 1],
        delay: 0.7,
      },
    },
  };

  const textVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.9,
        ease: [0.22, 1, 0.36, 1],
        delay: 1.1,
      },
    },
  };

  const mapVariants = {
    hidden: { opacity: 0, x: 50, scale: 0.95 },
    visible: {
      opacity: 1,
      x: 0,
      scale: 1,
      transition: {
        duration: 1.2,
        ease: [0.22, 1, 0.36, 1],
        delay: 0.8,
      },
    },
  };

  return (
    <PageTransition>
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
      
      {/* User Greeting - Dynamic Island */}
      <UserGreeting />
      
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
            <div key="hero-content">
              {/* Brand text */}
              <motion.div
                key="badge-animation"
                initial="hidden"
                animate="visible"
                variants={badgeVariants}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '1.5rem'
                }}
              >
                <span
                  style={{
                    fontStyle: 'italic',
                    fontSize: '2.5rem',
                    color: '#064E3B',
                    fontWeight: '400'
                  }}
                >
                  visa flow
                </span>
                <FlightTakeoffIcon sx={{ fontSize: 36, color: '#064E3B', paddingTop: '0.5rem' }} />
              </motion.div>

              {/* Main Hero Headline - Bold & Attention-Grabbing */}
              <motion.h1
                key="headline-animation"
                initial="hidden"
                animate="visible"
                variants={headlineVariants}
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
                Hazırlayın!
              </motion.h1>

              {/* Supporting Text */}
              <motion.p
                key="text-animation"
                initial="hidden"
                animate="visible"
                variants={textVariants}
                style={{
                  fontSize: '1.25rem',
                  color: '#666666',
                  marginBottom: '2.5rem',
                  lineHeight: '1.7',
                  fontWeight: '400',
                  maxWidth: '95%'
                }}
              >
                Yapay zeka destekli çözümümüzle vize başvuru sürecinizi basitleştirin. İhtiyacınız olan niyet mektubunu yapay zeka destekli çözümümüzle hızlıca oluşturun. Seçtiğiniz ülkeye göre özelleştirilmiş rehberlik alın.
              </motion.p>
            </div>

            {/* Right Side - Interactive Map */}
            <motion.div
              key="map-animation"
              initial="hidden"
              animate="visible"
              variants={mapVariants}
            >
              <InteractiveWorldMap />
            </motion.div>
          </div>
        </div>
      </section>

      {/* 3-Step Process Section */}
      <ProcessSteps />

      <footer style={{ 
        backgroundImage: `url(${vibeBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        padding: '2rem 2rem', 
        textAlign: 'center', 
        borderTop: '1px solid #EEEEEE' 
      }}>
        <p style={{ color: '#666666', fontSize: '0.875rem', margin: 0 }}>© Metafor. Llama Hackathon 2025</p>
      </footer>
      </div>
    </PageTransition>
  );
};

export default Landing;

