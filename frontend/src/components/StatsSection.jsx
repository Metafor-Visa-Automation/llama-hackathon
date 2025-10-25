import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars
import SpeedIcon from '@mui/icons-material/Speed';
import PublicIcon from '@mui/icons-material/Public';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import AirplanemodeActiveIcon from '@mui/icons-material/AirplanemodeActive';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import vibeBg from '../assets/vibe-bg1.webp';

const StatsSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      }
    );

    const currentSection = sectionRef.current;

    if (currentSection) {
      observer.observe(currentSection);
    }

    return () => {
      if (currentSection) {
        observer.unobserve(currentSection);
      }
    };
  }, []);

  // Scroll-based animation for planes
  useEffect(() => {
    const handleScroll = () => {
      if (sectionRef.current) {
        const rect = sectionRef.current.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        
        // Calculate how much of the section is visible
        const sectionTop = rect.top;
        const sectionHeight = rect.height;
        
        // Progress from 0 to 1 as section scrolls through viewport
        const progress = Math.max(0, Math.min(1, 
          (windowHeight - sectionTop) / (windowHeight + sectionHeight)
        ));
        
        setScrollProgress(progress);
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial call

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const stats = [
    {
      icon: <SpeedIcon sx={{ fontSize: 40 }} />,
      value: '10dk',
      label: 'Ortalama Form Süresi',
      subtext: 'vs 2-3 saat manuel',
      color: '#10B981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
    {
      icon: <PublicIcon sx={{ fontSize: 40 }} />,
      value: '26',
      label: 'Schengen Ülkesi',
      subtext: 'Tam destek',
      color: '#10B981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
      value: '10x',
      label: 'Daha Hızlı',
      subtext: 'Geleneksel yönteme göre',
      color: '#10B981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
    {
      icon: <MonetizationOnIcon sx={{ fontSize: 40 }} />,
      value: '$0',
      label: 'Tamamen Ücretsiz',
      subtext: 'MVP süresince',
      color: '#10B981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    },
  ];

  return (
    <section
      ref={sectionRef}
      style={{
        backgroundImage: `url(${vibeBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
        position: 'relative',
        overflow: 'hidden',
      }}
      className="py-24"
    >
      {/* Overlay for better readability */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.85)',
          zIndex: 0,
        }}
      />

      {/* Flying Planes Layer */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 1,
          overflow: 'hidden',
          pointerEvents: 'none',
        }}
      >
        {/* Left Fade Gradient */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: '250px',
            background: 'linear-gradient(to right, rgba(255, 255, 255, 0.85) 0%, transparent 100%)',
            zIndex: 3,
          }}
        />

        {/* Right Fade Gradient */}
        <div
          style={{
            position: 'absolute',
            right: 0,
            top: 0,
            bottom: 0,
            width: '250px',
            background: 'linear-gradient(to left, rgba(255, 255, 255, 0.85) 0%, transparent 100%)',
            zIndex: 3,
          }}
        />

        {/* Plane 1 */}
        <div
          style={{
            position: 'absolute',
            top: '8%',
            left: '-120px',
            transform: `translateX(${scrollProgress * 125}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.5,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 42,
              color: '#10B981',
              filter: 'drop-shadow(0 4px 16px rgba(16, 185, 129, 0.4))',
            }}
          />
        </div>

        {/* Plane 2 */}
        <div
          style={{
            position: 'absolute',
            top: '18%',
            left: '-150px',
            transform: `translateX(${scrollProgress * 115}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.55,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 48,
              color: '#059669',
              filter: 'drop-shadow(0 4px 16px rgba(5, 150, 105, 0.4))',
            }}
          />
        </div>

        {/* Plane 3 */}
        <div
          style={{
            position: 'absolute',
            top: '32%',
            left: '-100px',
            transform: `translateX(${scrollProgress * 135}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.45,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 38,
              color: '#10B981',
              filter: 'drop-shadow(0 4px 16px rgba(16, 185, 129, 0.4))',
            }}
          />
        </div>

        {/* Plane 4 */}
        <div
          style={{
            position: 'absolute',
            top: '45%',
            left: '-130px',
            transform: `translateX(${scrollProgress * 120}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.6,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 52,
              color: '#047857',
              filter: 'drop-shadow(0 4px 16px rgba(4, 120, 87, 0.4))',
            }}
          />
        </div>

        {/* Plane 5 */}
        <div
          style={{
            position: 'absolute',
            top: '55%',
            left: '-90px',
            transform: `translateX(${scrollProgress * 145}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.5,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 44,
              color: '#064E3B',
              filter: 'drop-shadow(0 4px 16px rgba(6, 78, 59, 0.4))',
            }}
          />
        </div>

        {/* Plane 6 */}
        <div
          style={{
            position: 'absolute',
            top: '65%',
            left: '-110px',
            transform: `translateX(${scrollProgress * 130}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.55,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 46,
              color: '#10B981',
              filter: 'drop-shadow(0 4px 16px rgba(16, 185, 129, 0.4))',
            }}
          />
        </div>

        {/* Plane 7 */}
        <div
          style={{
            position: 'absolute',
            top: '78%',
            left: '-140px',
            transform: `translateX(${scrollProgress * 118}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.48,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 40,
              color: '#059669',
              filter: 'drop-shadow(0 4px 16px rgba(5, 150, 105, 0.4))',
            }}
          />
        </div>

        {/* Plane 8 */}
        <div
          style={{
            position: 'absolute',
            top: '88%',
            left: '-95px',
            transform: `translateX(${scrollProgress * 140}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.52,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 50,
              color: '#047857',
              filter: 'drop-shadow(0 4px 16px rgba(4, 120, 87, 0.4))',
            }}
          />
        </div>

        {/* Plane 9 */}
        <div
          style={{
            position: 'absolute',
            top: '24%',
            left: '-170px',
            transform: `translateX(${scrollProgress * 108}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.42,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 36,
              color: '#10B981',
              filter: 'drop-shadow(0 4px 16px rgba(16, 185, 129, 0.4))',
            }}
          />
        </div>

        {/* Plane 10 */}
        <div
          style={{
            position: 'absolute',
            top: '72%',
            left: '-125px',
            transform: `translateX(${scrollProgress * 128}vw) rotate(90deg)`,
            transition: 'transform 0.1s linear',
            opacity: 0.58,
          }}
        >
          <AirplanemodeActiveIcon
            sx={{
              fontSize: 45,
              color: '#064E3B',
              filter: 'drop-shadow(0 4px 16px rgba(6, 78, 59, 0.4))',
            }}
          />
        </div>
      </div>

      <div className="container mx-auto px-8 md:px-12 relative z-10">
        {/* Title Section */}
        <div
          className={`text-center mb-12 transform transition-all duration-1000 ${
            isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
          }`}
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <h2
              className="text-4xl md:text-5xl font-bold"
              style={{
                fontFamily: '"Playfair Display", serif',
                color: '#1A1A1A',
                letterSpacing: '-0.03em',
              }}
            >
              Neden{' '}
            </h2>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <span
                style={{
                  fontStyle: 'italic',
                  fontSize: '2.5rem',
                  color: '#064E3B',
                  fontWeight: '400',
                  fontFamily: '"Playfair Display", serif',
                }}
              >
                "visa flow
              </span>
              <FlightTakeoffIcon sx={{ fontSize: 36, color: '#064E3B', paddingTop: '0.5rem' }} />
              <span
                style={{
                  fontStyle: 'italic',
                  fontSize: '2.5rem',
                  color: '#064E3B',
                  fontWeight: '400',
                  fontFamily: '"Playfair Display", serif',
                }}
              >
                "
              </span>
            </div>
            <h2
              className="text-4xl md:text-5xl font-bold"
              style={{
                fontFamily: '"Playfair Display", serif',
                color: '#1A1A1A',
                letterSpacing: '-0.03em',
              }}
            >
              ?
            </h2>
          </div>
          <p
            className="text-lg max-w-2xl mx-auto"
            style={{
              color: '#666666',
              fontFamily: '"Playfair Display", serif',
              fontWeight: '400',
              lineHeight: '1.7',
            }}
          >
            Yapay zeka destekli platformumuzla vize başvurunuzu hızlı, kolay ve güvenli bir şekilde tamamlayın
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 max-w-7xl mx-auto mt-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={
                isVisible
                  ? { opacity: 1, y: 0 }
                  : { opacity: 0, y: 30 }
              }
              transition={{
                duration: 0.6,
                delay: 0.3 + index * 0.1,
                ease: [0.22, 1, 0.36, 1],
              }}
            >
              <div
                className="rounded-2xl p-8 h-full transition-all duration-500 hover:-translate-y-3 hover:scale-105 cursor-pointer group"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.98)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  border: '1.5px solid rgba(255, 255, 255, 0.9)',
                  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = `0 25px 70px ${stat.color}30, 0 10px 30px rgba(0, 0, 0, 0.15)`;
                  e.currentTarget.style.borderColor = `${stat.color}40`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.9)';
                }}
              >
                {/* Icon */}
                <div
                  className="w-20 h-20 rounded-2xl mb-6 flex items-center justify-center transition-all duration-500 group-hover:scale-110 group-hover:rotate-6"
                  style={{
                    background: stat.gradient,
                    color: 'white',
                    boxShadow: `0 8px 24px ${stat.color}40`,
                  }}
                >
                  {React.cloneElement(stat.icon, { sx: { fontSize: 44 } })}
                </div>

                {/* Value */}
                <div
                  className="text-5xl font-bold mb-2"
                  style={{
                    fontFamily: '"Playfair Display", serif',
                    color: stat.color,
                  }}
                >
                  {stat.value}
                </div>

                {/* Label */}
                <div
                  className="font-semibold mb-2 text-lg"
                  style={{
                    color: '#1A1A1A',
                    fontFamily: '"Playfair Display", serif',
                  }}
                >
                  {stat.label}
                </div>

                {/* Subtext */}
                <div
                  className="text-sm"
                  style={{
                    color: '#666666',
                    fontFamily: '"Playfair Display", serif',
                  }}
                >
                  {stat.subtext}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* MVP Disclaimer Badge */}
        <div
          className={`text-center mt-16 transform transition-all duration-1000 delay-200 ${
            isVisible ? 'scale-100 opacity-100' : 'scale-90 opacity-0'
          }`}
        >
          <div
            className="inline-flex items-center gap-3 px-8 py-3.5 rounded-full"
            style={{
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              border: '1.5px solid rgba(16, 185, 129, 0.35)',
              fontFamily: '"Playfair Display", serif',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.15)',
            }}
          >
            <AnalyticsIcon
              sx={{
                fontSize: 22,
                color: '#064E3B',
                filter: 'drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))'
              }}
            />
            <span
              className="font-medium text-sm"
              style={{ color: '#064E3B', letterSpacing: '0.02em' }}
            >
              MVP Performance Metrics - Test Verilerine Dayanır
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StatsSection;

