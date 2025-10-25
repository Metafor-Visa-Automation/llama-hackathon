import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion'; // eslint-disable-line no-unused-vars
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';

/**
 * LoadingScreen Component
 * Displays a premium loading animation while fetching visa requirements from AI
 */
const LoadingScreen = () => {
  const navigate = useNavigate();
  const { destinationCountry } = useSelector((state) => state.country);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [loadingComplete, setLoadingComplete] = useState(false);

  // Dynamic loading messages
  const loadingMessages = [
    `Sizin için en güncel ${destinationCountry?.name || 'vize'} vize verilerini getiriyoruz!`,
    `${destinationCountry?.name || 'Hedef ülke'} için gerekli belgeleri analiz ediyoruz...`,
    `Kişiselleştirilmiş başvuru rehberiniz hazırlanıyor...`,
    `Son güncellemeleri kontrol ediyoruz...`,
    `Neredeyse hazır! Birkaç saniye daha...`
  ];

  // Cycle through messages
  useEffect(() => {
    const messageInterval = setInterval(() => {
      setCurrentMessageIndex((prevIndex) => 
        prevIndex < loadingMessages.length - 1 ? prevIndex + 1 : prevIndex
      );
    }, 3000); // Change message every 3 seconds

    return () => clearInterval(messageInterval);
  }, [loadingMessages.length]);

  // Simulate loading (replace with actual AI API call)
  useEffect(() => {
    const loadingTimer = setTimeout(() => {
      setLoadingComplete(true);
      // Navigate to fill-form after showing success message
      setTimeout(() => {
        navigate('/fill-form');
      }, 1500);
    }, 10000); // 10 seconds simulated loading

    return () => clearTimeout(loadingTimer);
  }, [navigate]);

  return (
    <PageTransition>
      <div 
        className="min-h-screen flex items-center justify-center relative overflow-hidden"
        style={{
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        {/* Visa Flow Branding - Top Left */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          style={{
            position: 'fixed',
            top: '2rem',
            left: '2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            zIndex: 100
          }}
        >
          <span
            style={{
              fontStyle: 'italic',
              fontSize: '2rem',
              color: '#064E3B',
              fontWeight: '400',
              textShadow: '0 2px 10px rgba(255, 255, 255, 0.8)'
            }}
          >
            visa flow
          </span>
          <FlightTakeoffIcon sx={{ 
            fontSize: 32, 
            color: '#064E3B',
            paddingTop: '0.3rem',
            filter: 'drop-shadow(0 2px 10px rgba(255, 255, 255, 0.8))'
          }} />
        </motion.div>

        {/* Animated Background Gradients */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            position: 'absolute',
            top: '-20%',
            right: '-10%',
            width: '600px',
            height: '600px',
            background: 'radial-gradient(circle, rgba(16, 185, 129, 0.4) 0%, transparent 70%)',
            borderRadius: '50%',
            filter: 'blur(60px)',
            pointerEvents: 'none'
          }}
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, -90, 0],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            position: 'absolute',
            bottom: '-20%',
            left: '-10%',
            width: '700px',
            height: '700px',
            background: 'radial-gradient(circle, rgba(5, 150, 105, 0.3) 0%, transparent 70%)',
            borderRadius: '50%',
            filter: 'blur(80px)',
            pointerEvents: 'none'
          }}
        />

        {/* Main Content Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{
            position: 'relative',
            zIndex: 10,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            padding: '4rem 3rem',
            borderRadius: '32px',
            boxShadow: '0 25px 80px rgba(0, 0, 0, 0.15)',
            maxWidth: '600px',
            width: '90%',
            textAlign: 'center',
            border: '1px solid rgba(255, 255, 255, 0.8)'
          }}
        >
          {!loadingComplete ? (
            <>
              {/* Airplane Animation with Fade */}
              <div style={{ 
                position: 'relative', 
                height: '120px', 
                marginBottom: '2rem',
                overflow: 'hidden'
              }}>
                <motion.div
                  animate={{
                    x: [-100, 700],
                    y: [0, -20, 0, -15, 0],
                    opacity: [0, 1, 1, 1, 0]
                  }}
                  transition={{
                    x: {
                      duration: 4,
                      repeat: Infinity,
                      ease: "linear"
                    },
                    y: {
                      duration: 4,
                      repeat: Infinity,
                      ease: "easeInOut"
                    },
                    opacity: {
                      duration: 4,
                      repeat: Infinity,
                      ease: "linear",
                      times: [0, 0.1, 0.5, 0.9, 1]
                    }
                  }}
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)'
                  }}
                >
                  <FlightTakeoffIcon 
                    sx={{ 
                      fontSize: 64, 
                      color: '#10B981',
                      filter: 'drop-shadow(0 4px 12px rgba(16, 185, 129, 0.3))'
                    }} 
                  />
                </motion.div>

                {/* Flight Trail Effect */}
                <motion.div
                  animate={{
                    x: [-150, 650],
                    opacity: [0, 0.6, 0.6, 0]
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "linear",
                    times: [0, 0.15, 0.85, 1]
                  }}
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    width: '100px',
                    height: '3px',
                    background: 'linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.6), transparent)',
                    borderRadius: '10px'
                  }}
                />
              </div>

              {/* Loading Title with Gradient Animation */}
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                style={{
                  fontSize: '2.5rem',
                  fontWeight: '800',
                  marginBottom: '1rem',
                  fontFamily: '"Playfair Display", serif',
                  lineHeight: '1.2',
                  position: 'relative'
                }}
              >
                <motion.span
                  animate={{
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                  style={{
                    background: 'linear-gradient(90deg, #1a1a1a 0%, #10B981 25%, #34D399 50%, #10B981 75%, #1a1a1a 100%)',
                    backgroundSize: '200% auto',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    display: 'inline-block'
                  }}
                >
                  Hazırlanıyor
                </motion.span>
              </motion.h1>

              {/* Dynamic Messages */}
              <div style={{ 
                minHeight: '80px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                marginBottom: '2rem'
              }}>
                <AnimatePresence mode="wait">
                  <motion.p
                    key={currentMessageIndex}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.5 }}
                    style={{
                      fontSize: '1.25rem',
                      color: '#059669',
                      fontWeight: '600',
                      fontFamily: '"Playfair Display", serif',
                      lineHeight: '1.6'
                    }}
                  >
                    {loadingMessages[currentMessageIndex]}
                  </motion.p>
                </AnimatePresence>
              </div>

              {/* Progress Bar */}
              <div style={{
                width: '100%',
                height: '6px',
                backgroundColor: '#E5E7EB',
                borderRadius: '10px',
                overflow: 'hidden',
                position: 'relative'
              }}>
                <motion.div
                  animate={{
                    x: ['-100%', '100%']
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '50%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, #10B981, transparent)',
                    borderRadius: '10px'
                  }}
                />
              </div>
            </>
          ) : (
            // Success State
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ 
                  type: "spring",
                  stiffness: 200,
                  damping: 15
                }}
              >
                <CheckCircleOutlineIcon 
                  sx={{ 
                    fontSize: 80, 
                    color: '#10B981',
                    marginBottom: '1.5rem'
                  }} 
                />
              </motion.div>
              
              <h1 style={{
                fontSize: '2.5rem',
                fontWeight: '800',
                color: '#10B981',
                marginBottom: '1rem',
                fontFamily: '"Playfair Display", serif'
              }}>
                Hazır!
              </h1>
              
              <p style={{
                fontSize: '1.25rem',
                color: '#059669',
                fontFamily: '"Playfair Display", serif',
                fontWeight: '600'
              }}>
                Başvuru formunuza yönlendiriliyorsunuz...
              </p>
            </motion.div>
          )}
        </motion.div>

        {/* Floating Particles */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0, 1, 0]
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2
            }}
            style={{
              position: 'absolute',
              width: '4px',
              height: '4px',
              borderRadius: '50%',
              backgroundColor: '#10B981',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              pointerEvents: 'none'
            }}
          />
        ))}
      </div>
    </PageTransition>
  );
};

export default LoadingScreen;

