import React, { useEffect, useRef, useState } from 'react';
import ConstructionIcon from '@mui/icons-material/Construction';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScheduleIcon from '@mui/icons-material/Schedule';
import schengenBg from '../assets/schengen-bg-2.jpg';

const MVPBadge = () => {
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
        rootMargin: '0px 0px -100px 0px'
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

  return (
    <section
      ref={sectionRef}
      style={{
        backgroundImage: `linear-gradient(135deg, rgba(240, 253, 244, 0.75) 0%, rgba(220, 252, 231, 0.75) 100%), url(${schengenBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        position: 'relative',
      }}
      className="py-20 overflow-hidden"
    >
      <div className="container mx-auto px-6 md:px-8 relative z-10">
        

        {/* Title */}
        <div
          className={`text-center mb-6 transform transition-all duration-1000 delay-200 ${
            isVisible
              ? 'translate-y-0 opacity-100'
              : 'translate-y-10 opacity-0'
          }`}
        >
          <h3
            className="text-3xl md:text-4xl font-extrabold mb-4 italic"
            style={{
              fontFamily: '"Playfair Display", serif',
              color: '#047857',
              letterSpacing: '-0.03em',
            }}
          >
            Şu Anda: Schengen Ülkeleri (26 Ülke)
          </h3>
          <p
            className="text-lg max-w-2xl mx-auto leading-relaxed italic"
            style={{
              color: '#666666',
              fontFamily: '"Playfair Display", serif',
              fontWeight: '400',
            }}
          >
            Pilot sürecimizde Schengen vize sürecini mükemmelleştiriyoruz.
            Yakında ABD, İngiltere, Kanada ve daha fazlası!
          </p>
        </div>

        {/* Cards */}
        <div className="flex flex-col md:flex-row justify-center gap-6 md:gap-8 max-w-4xl mx-auto mt-12">
          {/* Current Card */}
          <div
            className={`flex-1 transform transition-all duration-1000 delay-400 ${
              isVisible
                ? 'translate-x-0 opacity-100'
                : '-translate-x-10 opacity-0'
            }`}
          >
            <div
              className="rounded-2xl p-8 transition-all duration-300 hover:-translate-y-2 h-full"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
              }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center"
                  style={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                  }}
                >
                  <CheckCircleIcon sx={{ fontSize: 28, color: 'white' }} />
                </div>
                <div
                  className="font-bold text-2xl"
                  style={{
                    color: '#047857',
                    fontFamily: '"Playfair Display", serif',
                  }}
                >
                  Şu An
                </div>
              </div>
              <ul className="space-y-4">
                {[
                  '26 Schengen Ülkesine özelleşmiş scrapping sistemi',
                  'Özelleşmiş form oluşturma sistemi',
                  'Niyet mektubu oluşturma',
                ].map((item, index) => (
                  <li
                    key={index}
                    className={`flex items-center gap-3 transform transition-all duration-500 ${
                      isVisible
                        ? 'translate-x-0 opacity-100'
                        : '-translate-x-5 opacity-0'
                    }`}
                    style={{ transitionDelay: `${600 + index * 100}ms` }}
                  >
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: '#10B981' }}
                    ></div>
                    <span
                      className="text-base font-medium"
                      style={{
                        color: '#1A1A1A',
                        fontFamily: '"Playfair Display", serif',
                      }}
                    >
                      {item}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Coming Soon Card */}
          <div
            className={`flex-1 transform transition-all duration-1000 delay-500 ${
              isVisible
                ? 'translate-x-0 opacity-100'
                : 'translate-x-10 opacity-0'
            }`}
          >
            <div
              className="rounded-2xl p-8 transition-all duration-300 hover:-translate-y-2 h-full relative overflow-hidden"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                border: '1px solid rgba(16, 185, 129, 0.15)',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
              }}
            >
              {/* Gradient overlay */}
              <div
                className="absolute inset-0 pointer-events-none"
                style={{
                  background: 'linear-gradient(135deg, rgba(240, 253, 244, 0.5) 0%, rgba(220, 252, 231, 0.3) 100%)',
                }}
              ></div>

              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-6">
                  <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center"
                    style={{
                      background: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
                      boxShadow: '0 4px 12px rgba(16, 185, 129, 0.25)',
                    }}
                  >
                    <ScheduleIcon sx={{ fontSize: 28, color: 'white' }} />
                  </div>
                  <div
                    className="font-bold text-2xl"
                    style={{
                      color: '#047857',
                      fontFamily: '"Playfair Display", serif',
                    }}
                  >
                    Yakında
                  </div>
                </div>
                <ul className="space-y-4">
                  {[
                    'ABD (DS-160)',
                    'İngiltere',
                    'Kanada',
                    'Avustralya'
                  ].map((item, index) => (
                    <li
                      key={index}
                      className={`flex items-center gap-3 transform transition-all duration-500 ${
                        isVisible
                          ? 'translate-x-0 opacity-100'
                          : 'translate-x-5 opacity-0'
                      }`}
                      style={{ transitionDelay: `${700 + index * 100}ms` }}
                    >
                      <div
                        className="w-2 h-2 rounded-full animate-pulse"
                        style={{ backgroundColor: '#10B981' }}
                      ></div>
                      <span
                        className="text-base font-medium"
                        style={{
                          color: '#666666',
                          fontFamily: '"Playfair Display", serif',
                        }}
                      >
                        {item}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Badge */}
        <div
          className={`text-center mt-16 mb-8 transform transition-all duration-1000 ${
            isVisible
              ? 'translate-y-0 opacity-100'
              : 'translate-y-10 opacity-0'
          }`}
        >
          <div
            className="inline-flex items-center gap-3 text-white px-6 py-2 rounded-full transition-all duration-300"
            style={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
              fontFamily: '"Roboto", sans-serif',
            }}
          >
            <ConstructionIcon className="animate-pulse" sx={{ fontSize: 24 }} />
            <span className="font-bold" style={{ letterSpacing: '0.02em' }}>
              MVP - Beta Aşamasında
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MVPBadge;
