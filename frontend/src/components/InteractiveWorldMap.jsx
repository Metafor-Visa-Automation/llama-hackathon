import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { ArrowRight } from 'lucide-react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { setOriginCountry, setDestinationCountry } from '../store/countrySlice';

// Schengen countries ISO codes with names (ISO2 format for SimpleMaps)
const SCHENGEN_COUNTRIES = {
  'AT': 'Avusturya',
  'BE': 'Belçika', 
  'CZ': 'Çek Cumhuriyeti',
  'DK': 'Danimarka',
  'EE': 'Estonya',
  'FI': 'Finlandiya',
  'FR': 'Fransa',
  'DE': 'Almanya',
  'GR': 'Yunanistan',
  'HU': 'Macaristan',
  'IS': 'İzlanda',
  'IT': 'İtalya',
  'LV': 'Letonya',
  'LT': 'Litvanya',
  'LU': 'Lüksemburg',
  'MT': 'Malta',
  'NL': 'Hollanda',
  'NO': 'Norveç',
  'PL': 'Polonya',
  'PT': 'Portekiz',
  'SK': 'Slovakya',
  'SI': 'Slovenya',
  'ES': 'İspanya',
  'SE': 'İsveç',
  'CH': 'İsviçre'
};

const SCHENGEN_CODES = Object.keys(SCHENGEN_COUNTRIES);

// Common origin countries for Turkish users (ISO2 format)
const ORIGIN_COUNTRIES = {
  'TR': 'Türkiye',
  'US': 'Amerika Birleşik Devletleri',
  'GB': 'Birleşik Krallık',
  'CA': 'Kanada',
  'AU': 'Avustralya',
  'JP': 'Japonya',
  'KR': 'Güney Kore',
  'CN': 'Çin',
  'IN': 'Hindistan',
  'BR': 'Brezilya',
  'MX': 'Meksika',
  'RU': 'Rusya',
  'SA': 'Suudi Arabistan',
  'AE': 'Birleşik Arap Emirlikleri'
};

/**
 * InteractiveWorldMap Component using SimpleMaps
 * Displays an interactive world map highlighting Schengen countries with country selection
 * @param {Object} props
 * @param {Function} props.onStartApplication - Callback when application is started
 */
const InteractiveWorldMap = ({ onStartApplication }) => {
  const dispatch = useDispatch();
  const originCountry = useSelector((state) => state.country.originCountry);
  const destinationCountry = useSelector((state) => state.country.destinationCountry);
  
  const [mapLoaded, setMapLoaded] = useState(false);
  const mapInitialized = useRef(false);
  const scriptsLoaded = useRef(false);

  /**
   * Load SimpleMaps scripts dynamically
   */
  useEffect(() => {
    if (scriptsLoaded.current) return;

    const loadScript = (src, id) => {
      return new Promise((resolve, reject) => {
        // Check if script already exists
        if (document.getElementById(id)) {
          resolve();
          return;
        }

        const script = document.createElement('script');
        script.src = src;
        script.id = id;
        script.async = false;
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
      });
    };

    // Load scripts in sequence (mapdata first, then engine)
    loadScript('/simplemaps/simplemaps_worldmap_mapdata.js', 'simplemaps-mapdata')
      .then(() => loadScript('/simplemaps/simplemaps_worldmap.js', 'simplemaps-engine'))
      .then(() => {
        scriptsLoaded.current = true;
        setMapLoaded(true);
      })
      .catch((error) => {
        console.error('Error loading SimpleMaps scripts:', error);
      });

    // Cleanup function
    return () => {
      // Don't remove scripts on cleanup to avoid reloading
    };
  }, []);

  /**
   * Initialize SimpleMaps with custom configuration
   */
  useEffect(() => {
    if (!mapLoaded || mapInitialized.current || !window.simplemaps_worldmap_mapdata) return;

    const md = window.simplemaps_worldmap_mapdata;

    // Configure map settings
    md.main_settings = {
      width: 'responsive',
      background_color: 'transparent',
      background_transparent: 'yes',
      popups: 'on_hover',
      label_color: '#047857',
      label_size: 20,
      label_font: '"Playfair Display", serif',
      border_size: 2,
      border_color: '#FFFFFF',
      state_color: '#E5E7EB',
      state_hover_color: '#22C55E',
      all_states_inactive: 'no',
      all_states_zoomable: 'yes',
      div: 'simplemaps-container',
      auto_load: 'yes',
      
      // Zoom settings - Smooth zoom like in the example
      manual_zoom: 'yes',
      back_image: 'no',
      arrow_box: 'yes',
      navigation_size: '40',
      navigation_color: '#FFFFFF',
      navigation_border_color: '#10B981',
      initial_back: 'no',
      initial_zoom: -1,
      initial_zoom_solo: 'no',
      zoom_out_incrementally: 'yes',
      zoom_percentage: 0.65, // Tighter zoom to fit vertically
      zoom_time: 0.5,
      
      // Popup settings
      popup_color: 'white',
      popup_opacity: 0.98,
      popup_shadow: 3,
      popup_corners: 12,
      popup_font: '15px/1.6 "Playfair Display", serif',
      popup_nocss: 'no',
      
      fade_time: 0.2,
    };

    // Initialize state_specific if not exists
    if (!md.state_specific) {
      md.state_specific = {};
    }
    
    // Define a region for Schengen countries to zoom into
    if (!md.regions) md.regions = {};
    md.regions['schengen_area'] = {
        name: 'Schengen Area',
        states: [...SCHENGEN_CODES]
    };

    // Color Schengen countries with more vibrant colors
    SCHENGEN_CODES.forEach(code => {
      if (md.state_specific[code]) {
        md.state_specific[code].color = '#A7F3D0';
        md.state_specific[code].hover_color = '#34D399';
        md.state_specific[code].description = SCHENGEN_COUNTRIES[code];
      }
    });

    // Set initial zoom to the Schengen region
    md.main_settings.initial_zoom = 'schengen_area';
    md.main_settings.initial_zoom_solo = 'no';
    
    // Load the map
    if (window.simplemaps_worldmap) {
      window.simplemaps_worldmap.load();
      mapInitialized.current = true;
    }
  }, [mapLoaded]);

  /**
   * Setup global click handler for SimpleMaps
   */
  useEffect(() => {
    // Create global click handler function
    window.handleSchengenCountryClick = (countryCode) => {
      if (SCHENGEN_CODES.includes(countryCode)) {
        dispatch(setDestinationCountry(countryCode));
        console.log('Country selected from map:', countryCode, SCHENGEN_COUNTRIES[countryCode]);
      }
    };

    return () => {
      delete window.handleSchengenCountryClick;
    };
  }, [dispatch]);

  /**
   * Setup click handlers for countries
   */
  useEffect(() => {
    if (!mapLoaded || !window.simplemaps_worldmap_mapdata) return;

    const md = window.simplemaps_worldmap_mapdata;

    // Add click handlers to Schengen countries only
    SCHENGEN_CODES.forEach(code => {
      if (md.state_specific[code]) {
        md.state_specific[code].url = `javascript:window.handleSchengenCountryClick('${code}');`;
        md.state_specific[code].inactive = 'no';
      }
    });

    // Make non-Schengen countries inactive (no hover, no click)
    Object.keys(md.state_specific).forEach(code => {
      if (!SCHENGEN_CODES.includes(code)) {
        md.state_specific[code].inactive = 'yes';
      }
    });
  }, [mapLoaded]);

  /**
   * Update map colors when destination country changes
   */
  useEffect(() => {
    if (!mapLoaded || !window.simplemaps_worldmap || !window.simplemaps_worldmap_mapdata) return;

    const md = window.simplemaps_worldmap_mapdata;

    // Reset all Schengen countries to vibrant light green
    SCHENGEN_CODES.forEach(code => {
      if (md.state_specific[code]) {
        md.state_specific[code].color = '#A7F3D0';
        md.state_specific[code].hover_color = '#34D399';
      }
    });

    // Highlight selected country with darker green
    if (destinationCountry && md.state_specific[destinationCountry]) {
      md.state_specific[destinationCountry].color = '#10B981';
      md.state_specific[destinationCountry].hover_color = '#059669';
    }

    // Refresh the map
    if (window.simplemaps_worldmap && window.simplemaps_worldmap.refresh) {
      window.simplemaps_worldmap.refresh();
    }
  }, [destinationCountry, mapLoaded]);

  /**
   * Handle destination country change from dropdown
   */
  const handleDestinationChange = (countryCode) => {
    dispatch(setDestinationCountry(countryCode));
    console.log('Country selected from dropdown:', countryCode, SCHENGEN_COUNTRIES[countryCode]);
  };

  /**
   * Handle start application button click
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

  return (
    <div className="relative w-full">
      {/* Hide SimpleMaps watermark and enhance map */}
      <style>{`
        #simplemaps-container a[href*="simplemaps.com"],
        #simplemaps-container a[href*="simplemaps"],
        #simplemaps-container div[id*="credits"] {
          display: none !important;
          visibility: hidden !important;
          opacity: 0 !important;
          width: 0 !important;
          height: 0 !important;
          position: absolute !important;
          left: -9999px !important;
        }
        /* Make map more prominent and crisp */
        #simplemaps-container {
          position: relative;
        }
        #simplemaps-container svg {
          filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.1));
          border-radius: 12px;
        }
        #simplemaps-container svg path {
          stroke-width: 1.2;
        }

        /* Modern Zoom Buttons */
        #simplemaps_navigation {
          left: 24px !important;
          right: auto !important;
          top: 24px !important;
        }
        #simplemaps_navigation div {
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          background-color: rgba(255, 255, 255, 0.65) !important;
          border: 1px solid rgba(0, 0, 0, 0.05) !important;
          border-radius: 50% !important; /* Circular buttons */
          width: 42px !important;
          height: 42px !important;
          margin-bottom: 10px !important;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
        }
        #simplemaps_navigation div:hover {
          background-color: #FFFFFF !important;
          transform: scale(1.05) !important;
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12) !important;
        }
        #simplemaps_navigation div svg {
          fill: #059669 !important;
          width: 20px !important;
          height: 20px !important;
        }
      `}</style>

      {/* Map Container with Premium Styling */}
      <div className="rounded-3xl overflow-hidden shadow-2xl" style={{ backgroundColor: '#FFFFFF' }}>
        {/* Map with Gradient Background */}
        <div style={{
          padding: 0,
          margin: 0,
          background: 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
          position: 'relative',
          display: 'block'
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

          {/* SimpleMaps Container */}
          <div 
            id="simplemaps-container" 
            style={{ 
              position: 'relative', 
              zIndex: 10,
              width: '100%',
              height: '100%'
            }}
          >
            {!mapLoaded && (
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                color: '#059669',
                fontSize: '18px',
                fontFamily: '"Playfair Display", serif'
              }}>
                Harita yükleniyor...
              </div>
            )}
          </div>
        </div>

        {/* Country Selection and CTA Section */}
        <div style={{
          backgroundColor: '#FFFFFF',
          padding: '1.5rem 2.5rem',
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
              onChange={(e) => dispatch(setOriginCountry(e.target.value))}
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
            Hazırlamaya Başla
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InteractiveWorldMap;
