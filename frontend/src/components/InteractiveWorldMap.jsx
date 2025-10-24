import { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { ArrowRight } from 'lucide-react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';

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
   * @param {string} isoCode - Country ISO code
   * @param {boolean} isSchengen - Whether country is in Schengen zone
   * @param {boolean} isHovered - Whether country is currently hovered
   * @returns {string} - CSS color value
   */
  const getFillColor = (isoCode, isSchengen, isHovered = false) => {
    // Selected state - vibrant emerald green (fully painted)
    if (destinationCountry === isoCode) {
      return '#059669';
    }

    // Hovered state - medium green (noticeable hover effect)
    if (isHovered && isSchengen) {
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
   * Handles country click event from map
   * @param {Object} geo - Geography object
   */
  const handleCountryClick = (geo) => {
    const isoCode = geo.id;
    const isSchengen = SCHENGEN_CODES.includes(isoCode);

    // Only allow selection of Schengen countries
    if (isSchengen) {
      // Update destination country state - this will update both map and dropdown
      setDestinationCountry(isoCode);
      console.log('Country selected from map:', isoCode, SCHENGEN_COUNTRIES[isoCode]);
    }
  };

  /**
   * Handles destination country change from dropdown
   * @param {string} countryCode - ISO code of selected country
   */
  const handleDestinationChange = (countryCode) => {
    // Update destination country state - this will update both map and dropdown
    setDestinationCountry(countryCode);
    console.log('Country selected from dropdown:', countryCode, SCHENGEN_COUNTRIES[countryCode]);
  };

  /**
   * Handles start application button click
   */
  const handleStartApplication = () => {
    if (originCountry && destinationCountry) {
      console.log('Starting application:', {
        from: ORIGIN_COUNTRIES[originCountry],
        to: SCHENGEN_COUNTRIES[destinationCountry]
      });
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
        <div className="absolute top-6 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-emerald-800 to-emerald-700 text-white px-6 py-3 rounded-xl text-sm font-bold z-20 pointer-events-none shadow-2xl whitespace-nowrap backdrop-blur-sm border border-emerald-600" style={{ fontFamily: '"Playfair Display", serif' }}>
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
                            fill: getFillColor(isoCode, isSchengen, hoveredCountry === isoCode),
                            stroke: destinationCountry === isoCode ? '#047857' : (isSchengen ? '#86EFAC' : '#9CA3AF'),
                            strokeWidth: destinationCountry === isoCode ? 3 : (isSchengen ? 1.5 : 1),
                            outline: 'none',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            filter: destinationCountry === isoCode ? 'drop-shadow(0 6px 20px rgba(5, 150, 105, 0.35))' : 'none',
                          },
                          hover: {
                            fill: getFillColor(isoCode, isSchengen, true),
                            stroke: isSchengen ? '#059669' : '#9CA3AF',
                            strokeWidth: isSchengen ? 3 : 1,
                            outline: 'none',
                            cursor: isSchengen ? 'pointer' : 'default',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            filter: isSchengen ? 'drop-shadow(0 6px 16px rgba(5, 150, 105, 0.3))' : 'none',
                          },
                          pressed: {
                            fill: getFillColor(isoCode, isSchengen, false),
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
          <FormControl 
            sx={{ 
              flex: '1 1 200px', 
              minWidth: '200px',
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                backgroundColor: '#F0FDF4',
                fontWeight: 500,
                fontFamily: '"Playfair Display", serif',
                '& fieldset': {
                  borderColor: '#A7F3D0',
                  borderWidth: '2px',
                },
                '&:hover fieldset': {
                  borderColor: '#10B981',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#10B981',
                  borderWidth: '2px',
                },
              },
              '& .MuiInputLabel-root': {
                color: '#064E3B',
                fontWeight: 600,
                fontSize: '0.875rem',
                fontFamily: '"Playfair Display", serif',
                '&.Mui-focused': {
                  color: '#059669',
                },
                '&.MuiInputLabel-shrink': {
                  color: '#059669',
                },
              },
              '& .MuiSelect-select': {
                color: '#064E3B',
                padding: '0.75rem 1rem',
                fontFamily: '"Playfair Display", serif',
              }
            }}
          >
            <InputLabel id="origin-country-label" shrink>Nereden</InputLabel>
            <Select
              labelId="origin-country-label"
              value={originCountry}
              label="Nereden"
              onChange={(e) => setOriginCountry(e.target.value)}
              notched
            >
              {Object.entries(ORIGIN_COUNTRIES).map(([code, name]) => (
                <MenuItem 
                  key={code} 
                  value={code}
                  sx={{ fontFamily: '"Playfair Display", serif' }}
                >
                  {name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Destination Country Dropdown */}
          <FormControl 
            sx={{ 
              flex: '1 1 200px', 
              minWidth: '200px',
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                backgroundColor: destinationCountry ? '#F0FDF4' : '#F9FAFB',
                fontWeight: 500,
                fontFamily: '"Playfair Display", serif',
                '& fieldset': {
                  borderColor: destinationCountry ? '#A7F3D0' : '#E5E7EB',
                  borderWidth: '2px',
                },
                '&:hover fieldset': {
                  borderColor: '#10B981',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#10B981',
                  borderWidth: '2px',
                },
              },
              '& .MuiInputLabel-root': {
                color: '#064E3B',
                fontWeight: 600,
                fontSize: '0.875rem',
                fontFamily: '"Playfair Display", serif',
                '&.Mui-focused': {
                  color: '#059669',
                },
                '&.MuiInputLabel-shrink': {
                  color: '#059669',
                },
              },
              '& .MuiSelect-select': {
                color: destinationCountry ? '#064E3B' : '#9CA3AF',
                padding: '0.75rem 1rem',
                fontFamily: '"Playfair Display", serif',
              }
            }}
          >
            <InputLabel id="destination-country-label" shrink>
              Nereye
            </InputLabel>
            <Select
              labelId="destination-country-label"
              value={destinationCountry || ''}
              label="Nereye"
              onChange={(e) => handleDestinationChange(e.target.value)}
              displayEmpty
              notched
              renderValue={(selected) => {
                if (!selected) {
                  return <span style={{ color: '#9CA3AF', fontFamily: '"Playfair Display", serif' }}>Ülke Seçiniz</span>;
                }
                return SCHENGEN_COUNTRIES[selected];
              }}
            >
              {Object.entries(SCHENGEN_COUNTRIES).map(([code, name]) => (
                <MenuItem 
                  key={code} 
                  value={code}
                  sx={{ fontFamily: '"Playfair Display", serif' }}
                >
                  {name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

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
              flex: '0 0 auto',
              fontFamily: '"Playfair Display", serif'
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
