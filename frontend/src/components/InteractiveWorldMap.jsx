import { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

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

// GeoJSON data URL
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

/**
 * InteractiveWorldMap Component
 * Displays an interactive world map highlighting Schengen countries
 * @param {Object} props
 * @param {string|null} props.selectedCountry - Currently selected country ISO code
 * @param {Function} props.onSelectCountry - Callback when a country is clicked
 */
const InteractiveWorldMap = ({ selectedCountry, onSelectCountry }) => {
  const [hoveredCountry, setHoveredCountry] = useState(null);

  /**
   * Determines the fill color of a country based on its state
   * @param {Object} geo - Geography object
   * @returns {string} - CSS color value
   */
  const getFillColor = (geo) => {
    const isoCode = geo.id;
    const isSchengen = SCHENGEN_CODES.includes(isoCode);

    // Selected state - dark blue
    if (selectedCountry === isoCode) {
      return '#1E40AF';
    }

    // Hovered state - medium blue
    if (hoveredCountry === isoCode && isSchengen) {
      return '#3B82F6';
    }

    // Schengen countries - light blue
    if (isSchengen) {
      return '#DBEAFE';
    }

    // Default state - light gray
    return '#F3F4F6';
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
      onSelectCountry(isoCode);
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
        <div className="absolute top-6 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-900 to-blue-800 text-white px-6 py-3 rounded-xl text-sm font-bold z-20 pointer-events-none shadow-2xl whitespace-nowrap backdrop-blur-sm border border-blue-700">
          {SCHENGEN_COUNTRIES[hoveredCountry]}
        </div>
      )}

      {/* Map Container with Premium Styling - No Border */}
      <div className="rounded-3xl overflow-hidden shadow-2xl" style={{ backgroundColor: '#FFFFFF' }}>
        {/* Map with Gradient Background */}
        <div style={{
          padding: '2.5rem 2rem',
          background: 'linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%)',
          position: 'relative'
        }}>
          {/* Decorative Elements */}
          <div style={{
            position: 'absolute',
            top: '-100px',
            right: '-100px',
            width: '300px',
            height: '300px',
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none'
          }}></div>
          <div style={{
            position: 'absolute',
            bottom: '-150px',
            left: '-150px',
            width: '350px',
            height: '350px',
            background: 'radial-gradient(circle, rgba(30, 64, 175, 0.08) 0%, transparent 70%)',
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
                            stroke: '#CBD5E1',
                            strokeWidth: 0.75,
                            outline: 'none',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          },
                          hover: {
                            fill: getFillColor(geo),
                            stroke: '#1E40AF',
                            strokeWidth: isSchengen ? 2 : 0.75,
                            outline: 'none',
                            cursor: isSchengen ? 'pointer' : 'default',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            filter: 'drop-shadow(0 4px 12px rgba(30, 64, 175, 0.2))',
                          },
                          pressed: {
                            fill: getFillColor(geo),
                            stroke: '#1E40AF',
                            strokeWidth: 2.5,
                            outline: 'none',
                            filter: 'drop-shadow(0 8px 16px rgba(30, 64, 175, 0.25))',
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

        {/* Premium Legend */}
        <div style={{
          backgroundColor: '#FFFFFF',
          padding: '1.75rem',
          borderTop: '1px solid #F1F5F9',
          display: 'flex',
          justifyContent: 'center',
          gap: '2.5rem',
          flexWrap: 'wrap'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '14px',
              height: '14px',
              borderRadius: '4px',
              backgroundColor: '#DBEAFE',
              border: '1px solid #BAE6FD',
              boxShadow: '0 2px 4px rgba(30, 64, 175, 0.08)'
            }}></div>
            <span style={{ color: '#0C4A6E', fontSize: '0.9rem', fontWeight: '600', letterSpacing: '0.01em' }}>Schengen Ülkeleri</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '14px',
              height: '14px',
              borderRadius: '4px',
              backgroundColor: '#1E40AF',
              border: '1px solid #1E3A8A',
              boxShadow: '0 2px 4px rgba(30, 64, 175, 0.15)'
            }}></div>
            <span style={{ color: '#0C4A6E', fontSize: '0.9rem', fontWeight: '600', letterSpacing: '0.01em' }}>Seçili Ülke</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveWorldMap;
