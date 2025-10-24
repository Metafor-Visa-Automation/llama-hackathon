import { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { ArrowRight } from 'lucide-react';

// Schengen countries ISO codes with names
const SCHENGEN_COUNTRIES = {
  'AUT': 'Avusturya', 'BEL': 'Belçika', 'CZE': 'Çek Cumhuriyeti', 'DNK': 'Danimarka',
  'EST': 'Estonya', 'FIN': 'Finlandiya', 'FRA': 'Fransa', 'DEU': 'Almanya',
  'GRC': 'Yunanistan', 'HUN': 'Macaristan', 'ISL': 'İzlanda', 'ITA': 'İtalya',
  'LVA': 'Letonya', 'LTU': 'Litvanya', 'LUX': 'Lüksemburg', 'MLT': 'Malta',
  'NLD': 'Hollanda', 'NOR': 'Norveç', 'POL': 'Polonya', 'PRT': 'Portekiz',
  'SVK': 'Slovakya', 'SVN': 'Slovenya', 'ESP': 'İspanya', 'SWE': 'İsveç', 'CHE': 'İsviçre'
};

const SCHENGEN_CODES = Object.keys(SCHENGEN_COUNTRIES);

// Common origin countries for Turkish users
const ORIGIN_COUNTRIES = {
  'TUR': 'Türkiye',
  'USA': 'Amerika Birleşik Devletleri',
  'GBR': 'Birleşik Krallık',
  'CAN': 'Kanada',
  'AUS': 'Avustralya',
  'JPN': 'Japonya',
  'KOR': 'Güney Kore',
  'CHN': 'Çin',
  'IND': 'Hindistan',
  'BRA': 'Brezilya',
  'MEX': 'Meksika',
  'RUS': 'Rusya',
  'SAU': 'Suudi Arabistan',
  'ARE': 'Birleşik Arap Emirlikleri'
};

// GeoJSON data URL
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

/**
 * InteractiveWorldMap Component
 * Displays an interactive world map highlighting Schengen countries with country selection
 * @param {Object} props
 * @param {Function} props.onStartApplication - Callback when application is started
 */
const InteractiveWorldMap = ({ onStartApplication }) => {
  const [hoveredCountry, setHoveredCountry] = useState(null);
  const [originCountry, setOriginCountry] = useState('TUR'); // Default to Turkey
  const [destinationCountry, setDestinationCountry] = useState(null);

  /**
   * Determines the fill color of a country based on its state
   * @param {Object} geo - Geography object
   * @returns {string} - CSS color value
   */
  const getFillColor = (geo) => {
    const isoCode = geo.id;
    const isSchengen = SCHENGEN_CODES.includes(isoCode);

    // Selected state - vibrant emerald green (fully painted)
    if (destinationCountry === isoCode) {
      return '#059669';
    }

    // Hovered state - medium green (noticeable hover effect)
    if (hoveredCountry === isoCode && isSchengen) {
      return '#10B981';
    }

    // Schengen countries - light mint green
    if (isSchengen) {
      return '#D1FAE5';
    }

    // Default state - light gray
    return '#F5F5F5';
  };

  /**
   * Handles country click event
   * @param {Object} geo - Geography object
   */
  const handleCountryClick = (geo) => {
    const isoCode = geo.id;
    const isSchengen = SCHENGEN_CODES.includes(isoCode);

    // Only allow selection of Schengen countries
    if (isSchengen) {
      setDestinationCountry(isoCode);
    }
  };

  /**
   * Handles start application button click
   */
  const handleStartApplication = () => {
    if (originCountry && destinationCountry) {
      onStartApplication({ originCountry, destinationCountry });
    }
  };

  /**
   * Handles country mouse enter event
   * @param {Object} geo - Geography object
   */
  const handleMouseEnter = (geo) => {
    const isoCode = geo.id;
    const isSchengen = SCHENGEN_CODES.includes(isoCode);

    if (isSchengen) {
      setHoveredCountry(isoCode);
    }
  };

  /**
   * Handles country mouse leave event
   */
  const handleMouseLeave = () => {
    setHoveredCountry(null);
  };

  return (
    <div className="relative w-full">
      {/* Tooltip - shows country name on hover */}
      {hoveredCountry && (
        <div className="absolute top-6 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-emerald-800 to-emerald-700 text-white px-6 py-3 rounded-xl text-sm font-bold z-20 pointer-events-none shadow-2xl whitespace-nowrap backdrop-blur-sm border border-emerald-600">
          {SCHENGEN_COUNTRIES[hoveredCountry]}
        </div>
      )}

      {/* Map Container with Premium Styling - No Border */}
      <div className="rounded-3xl overflow-hidden shadow-2xl" style={{ backgroundColor: '#FFFFFF' }}>
        {/* Map with Gradient Background */}
        <div style={{
          padding: '2.5rem 2rem',
          background: 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
          position: 'relative'
        }}>
          {/* Decorative Elements */}
          <div style={{
            position: 'absolute',
            top: '-100px',
            right: '-100px',
            width: '300px',
            height: '300px',
            background: 'radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none'
          }}></div>
          <div style={{
            position: 'absolute',
            bottom: '-150px',
            left: '-150px',
            width: '350px',
            height: '350px',
            background: 'radial-gradient(circle, rgba(5, 150, 105, 0.1) 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none'
          }}></div>

          {/* Map */}
          <div style={{ position: 'relative', zIndex: 10 }}>
            <ComposableMap
              projection="geoMercator"
              projectionConfig={{
                scale: 147,
                center: [15, 45]
              }}
              width={800}
              height={600}
              style={{ width: '100%', height: 'auto' }}
            >
              <Geographies geography={geoUrl}>
                {({ geographies }) =>
                  geographies.map((geo) => {
                    const isoCode = geo.id;
                    const isSchengen = SCHENGEN_CODES.includes(isoCode);

                    return (
                      <Geography
                        key={geo.rsmKey}
                        geography={geo}
                        onClick={() => handleCountryClick(geo)}
                        onMouseEnter={() => handleMouseEnter(geo)}
                        onMouseLeave={handleMouseLeave}
                        style={{
                          default: {
                            fill: getFillColor(geo),
                            stroke: destinationCountry === isoCode ? '#047857' : (isSchengen ? '#86EFAC' : '#9CA3AF'),
                            strokeWidth: destinationCountry === isoCode ? 3 : (isSchengen ? 1.5 : 1),
                            outline: 'none',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            filter: destinationCountry === isoCode ? 'drop-shadow(0 6px 20px rgba(5, 150, 105, 0.35))' : 'none',
                          },
                          hover: {
                            fill: getFillColor(geo),
                            stroke: isSchengen ? '#059669' : '#9CA3AF',
                            strokeWidth: isSchengen ? 3 : 1,
                            outline: 'none',
                            cursor: isSchengen ? 'pointer' : 'default',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            filter: isSchengen ? 'drop-shadow(0 6px 16px rgba(5, 150, 105, 0.3))' : 'none',
                          },
                          pressed: {
                            fill: getFillColor(geo),
                            stroke: '#047857',
                            strokeWidth: 3.5,
                            outline: 'none',
                            filter: 'drop-shadow(0 8px 24px rgba(5, 150, 105, 0.4))',
                          },
                        }}
                      />
                    );
                  })
                }
              </Geographies>
            </ComposableMap>
          </div>
        </div>

        {/* Country Selection and CTA Section */}
        <div style={{
          backgroundColor: '#FFFFFF',
          padding: '2rem 2.5rem',
          borderTop: '1px solid #E5E7EB',
          display: 'flex',
          alignItems: 'center',
          gap: '1.5rem',
          flexWrap: 'wrap'
        }}>
          {/* Origin Country Dropdown */}
          <div style={{ flex: '1 1 200px', minWidth: '200px' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#064E3B',
              marginBottom: '0.5rem'
            }}>
              Nereden
            </label>
            <select
              value={originCountry}
              onChange={(e) => setOriginCountry(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                fontSize: '1rem',
                fontWeight: '500',
                color: '#064E3B',
                backgroundColor: '#F0FDF4',
                border: '2px solid #A7F3D0',
                borderRadius: '12px',
                outline: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10B981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#A7F3D0';
                e.target.style.boxShadow = 'none';
              }}
            >
              {Object.entries(ORIGIN_COUNTRIES).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>

          {/* Destination Country Dropdown */}
          <div style={{ flex: '1 1 200px', minWidth: '200px' }}>
            <label style={{
              display: 'block',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: '#064E3B',
              marginBottom: '0.5rem'
            }}>
              Nereye
            </label>
            <select
              value={destinationCountry || ''}
              onChange={(e) => setDestinationCountry(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                fontSize: '1rem',
                fontWeight: '500',
                color: destinationCountry ? '#064E3B' : '#9CA3AF',
                backgroundColor: destinationCountry ? '#F0FDF4' : '#F9FAFB',
                border: destinationCountry ? '2px solid #A7F3D0' : '2px solid #E5E7EB',
                borderRadius: '12px',
                outline: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#10B981';
                e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = destinationCountry ? '#A7F3D0' : '#E5E7EB';
                e.target.style.boxShadow = 'none';
              }}
            >
              <option value="" disabled>Ülke Seçiniz</option>
              {Object.entries(SCHENGEN_COUNTRIES).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>

          {/* CTA Button */}
          <button
            onClick={handleStartApplication}
            disabled={!originCountry || !destinationCountry}
            className={`
              inline-flex items-center gap-2 px-6 py-3 text-base font-semibold rounded-full
              transition-all duration-300 transform
              ${originCountry && destinationCountry
                ? 'hover:scale-105 cursor-pointer'
                : 'cursor-not-allowed opacity-50'
              }
            `}
            style={{
              background: originCountry && destinationCountry
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : '#CCCCCC',
              color: '#FFFFFF',
              boxShadow: originCountry && destinationCountry
                ? '0 6px 20px rgba(16, 185, 129, 0.4)'
                : 'none',
              border: 'none',
              whiteSpace: 'nowrap',
              flex: '0 0 auto'
            }}
          >
            Başvuruya Başla
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InteractiveWorldMap;
