import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars
import SpeedIcon from '@mui/icons-material/Speed';
import PublicIcon from '@mui/icons-material/Public';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import vibeBg from '../assets/vibe-bg1.webp';

const StatsSection = () => {
  const [isVisible, setIsVisible] = useState(false);
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

