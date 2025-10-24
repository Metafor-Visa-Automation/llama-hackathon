import { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import InteractiveWorldMap from '../components/InteractiveWorldMap';
import ProcessSteps from '../components/ProcessSteps';

/**
 * Landing Page Component for Visa Flow
 * Main landing page with interactive world map and application flow
 */
const Landing = () => {
  const [selectedCountry, setSelectedCountry] = useState(null);

  /**
   * Handles country selection from the map
   * @param {string} countryCode - ISO code of selected country
   */
  const handleSelectCountry = (countryCode) => {
    setSelectedCountry(countryCode);
  };

  /**
   * Handles the "Start Application" button click
   */
  const handleStartApplication = () => {
    if (selectedCountry) {
      console.log('Starting application for:', selectedCountry);
      // TODO: Navigate to application page
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FFFFFF' }}>
      {/* Hero Section - Split Layout */}
      <section style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: '4rem' }}>
        <div className="container mx-auto px-8">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
            {/* Left Side - Text Content */}
            <div>
              <h1
                style={{
                  fontSize: '3.5rem',
                  fontWeight: '700',
                  color: '#000000',
                  marginBottom: '1.5rem',
                  lineHeight: '1.2',
                  letterSpacing: '-0.02em'
                }}
              >
                Visa Flow
              </h1>

              <p
                style={{
                  fontSize: '1.25rem',
                  color: '#666666',
                  marginBottom: '2rem',
                  lineHeight: '1.6',
                  fontWeight: '400'
                }}
              >
                Vize başvuru sürecinizi basitleştirin. İhtiyacınız olan tüm belgeleri yapay zeka destekli çözümümüzle hızlıca oluşturun. Seçtiğiniz ülkeye göre özelleştirilmiş rehberlik alın.
              </p>

              {/* CTA Button */}
              <button
                onClick={handleStartApplication}
                disabled={!selectedCountry}
                className={`
                  inline-flex items-center gap-2 px-8 py-4 text-base font-semibold rounded-full
                  transition-all duration-300 transform
                  ${selectedCountry
                    ? 'hover:scale-105 cursor-pointer shadow-lg hover:shadow-xl'
                    : 'cursor-not-allowed opacity-60'
                  }
                `}
                style={{
                  backgroundColor: selectedCountry ? '#000000' : '#CCCCCC',
                  color: '#FFFFFF',
                }}
              >
                Başvuruya Başla
                <ArrowRight size={20} />
              </button>

              {/* Helper Text */}
              {selectedCountry && (
                <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#666666' }}>
                  ✓ Ülke seçildi. Başvuruya devam edebilirsiniz.
                </p>
              )}
            </div>

            {/* Right Side - Interactive Map */}
            <div>
              <InteractiveWorldMap
                selectedCountry={selectedCountry}
                onSelectCountry={handleSelectCountry}
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
  );
};

export default Landing;

