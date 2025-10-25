import React from 'react';
import metaLogo from '../assets/logos/Meta_Platforms_Inc._logo.svg.png';
import startupHouseLogo from '../assets/logos/ytustartuphouse_logo.jpeg';
import ytuLogo from '../assets/logos/Yıldız_Technical_University_logo_variant.svg.png';
import ollamaLogo from '../assets/logos/ollama.png';

const LogoMarquee = () => {
  // Logo listesi
  const brands = [
    { name: 'Meta', logo: metaLogo },
    { name: 'Startup House', logo: startupHouseLogo },
    {name: 'Ollama', logo: ollamaLogo},
    { name: 'YTÜ', logo: ytuLogo },
    { name: 'Meta', logo: metaLogo },
    { name: 'Startup House', logo: startupHouseLogo },
    {name: 'Ollama', logo: ollamaLogo},
    { name: 'YTÜ', logo: ytuLogo },
  ];

  // Logoları 2 kez tekrarla (seamless loop için)
  const duplicatedBrands = [...brands, ...brands];

  return (
    <section
      style={{
        backgroundColor: '#F9FAFB',
        borderTop: '1px solid #E5E7EB',
        borderBottom: '1px solid #E5E7EB',
        position: 'relative',
        overflow: 'hidden',
      }}
      className="py-6"
    >
      <div className="container mx-auto">
        {/* Marquee Container */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            overflow: 'hidden',
          }}
        >
          {/* Left Fade */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              bottom: 0,
              width: '150px',
              background: 'linear-gradient(to right, #F9FAFB 0%, transparent 100%)',
              zIndex: 10,
              pointerEvents: 'none',
            }}
          />

          {/* Right Fade */}
          <div
            style={{
              position: 'absolute',
              right: 0,
              top: 0,
              bottom: 0,
              width: '150px',
              background: 'linear-gradient(to left, #F9FAFB 0%, transparent 100%)',
              zIndex: 10,
              pointerEvents: 'none',
            }}
          />

          {/* Scrolling Logos */}
          <div
            className="logo-marquee-track"
            style={{
              display: 'flex',
              gap: '3rem',
              animation: 'marquee 30s linear infinite',
              willChange: 'transform',
              pointerEvents: 'none',
            }}
          >
            {duplicatedBrands.map((brand, index) => (
              <div
                key={index}
                className="brand-item"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minWidth: '180px',
                  height: '60px',
                  padding: '0.5rem 1.5rem',
                }}
              >
                {/* Logo Image */}
                <img
                  src={brand.logo}
                  alt={brand.name}
                  style={{
                    maxWidth: '100%',
                    maxHeight: '55px',
                    width: 'auto',
                    height: 'auto',
                    objectFit: 'contain',
                    filter: 'grayscale(100%)',
                    opacity: 0.5,
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CSS Animation */}
      <style>
        {`
          @keyframes marquee {
            0% {
              transform: translateX(0);
            }
            100% {
              transform: translateX(-50%);
            }
          }
        `}
      </style>
    </section>
  );
};

export default LogoMarquee;

