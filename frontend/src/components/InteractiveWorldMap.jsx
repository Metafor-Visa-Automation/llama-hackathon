import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Calendar } from 'lucide-react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { 
  setOriginCountry, 
  setDestinationCountry,
  setStartDate,
  setEndDate,
  setApplicationType
} from '../store/countrySlice';

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

const APPLICATION_TYPES = {
  'tourist': 'Turistik',
  'business': 'İş',
  'student': 'Öğrenci',
  'work': 'Çalışma'
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
 */
const InteractiveWorldMap = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const {
    originCountry,
    destinationCountry,
    startDate,
    endDate,
    applicationType
  } = useSelector((state) => state.country);
  const { isAuthenticated } = useSelector((state) => state.auth);
  
  const [mapLoaded, setMapLoaded] = useState(false);
  const mapInitialized = useRef(false);
  const scriptsLoaded = useRef(false);
  const startDateInputRef = useRef(null);
  const endDateInputRef = useRef(null);

  /**
   * Handle origin country change from dropdown
   */
  const handleOriginChange = (countryCode) => {
    dispatch(setOriginCountry({
      code: countryCode,
      name: ORIGIN_COUNTRIES[countryCode]
    }));
  };

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
        dispatch(setDestinationCountry({
          code: countryCode,
          name: SCHENGEN_COUNTRIES[countryCode]
        }));
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
    if (destinationCountry?.code && md.state_specific[destinationCountry.code]) {
      md.state_specific[destinationCountry.code].color = '#10B981';
      md.state_specific[destinationCountry.code].hover_color = '#059669';
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
    dispatch(setDestinationCountry({
      code: countryCode,
      name: SCHENGEN_COUNTRIES[countryCode]
    }));
    console.log('Country selected from dropdown:', countryCode, SCHENGEN_COUNTRIES[countryCode]);
  };

  /**
   * Handle start application button click
   */
  const handleStartApplication = () => {
    if (!originCountry?.code || !destinationCountry?.code || !startDate || !endDate || !applicationType) {
      return;
    }

    // Check if user is logged in
    if (!isAuthenticated) {
      // Redirect to login page if not authenticated
      navigate('/login');
      return;
    }

    // User is authenticated, redirect to loading screen
    console.log('Starting application:', {
      from: originCountry.name,
      to: destinationCountry.name
    });
    navigate('/loading-screen');
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

        .custom-input-root {
          flex: 1 1 200px;
          min-width: 200px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .custom-label-wrapper {
            display: flex;
            align-items: center;
            gap: 8px;
            padding-left: 12px;
            margin-bottom: 4px;
        }
        .custom-label-wrapper label {
            font-family: "Playfair Display", serif;
            color: #064E3B;
            font-weight: 600;
            font-size: 0.875rem;
            white-space: nowrap;
        }
        .custom-label-wrapper .line {
            width: 100%;
            height: 1px;
            background-color: #A7F3D0;
        }
        .custom-input-wrapper {
            display: flex;
            align-items: center;
            border: 2px solid #34D399;
            border-radius: 12px;
            padding: 0.6rem 1rem;
            background-color: #FFFFFF;
            transition: border-color 0.2s ease-in-out;
        }

        .custom-input-wrapper:hover {
          border-color: #10B981;
        }

        .custom-input-wrapper:focus-within {
          border-color: #10B981;
          box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }

        .custom-input-wrapper input, .custom-input-wrapper select {
          border: none;
          outline: none;
          background-color: transparent;
          width: 100%;
          font-family: "Playfair Display", serif;
          font-size: 1rem;
          color: #064E3B;
          -webkit-appearance: none;
          -moz-appearance: none;
          appearance: none;
        }

        .custom-input-wrapper input[type="date"]::-webkit-calendar-picker-indicator {
          display: none;
        }
        
        .custom-input-wrapper select {
          background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23064E3B%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E');
          background-repeat: no-repeat;
          background-position: right 0.7em top 50%;
          background-size: 0.65em auto;
        }

        .custom-input-wrapper .icon {
          color: #064E3B;
        }

      `}</style>

      {/* Map Container with Premium Styling */}
      <div className="rounded-3xl overflow-hidden shadow-2xl" style={{ backgroundColor: '#FFFFFF' }}>
        {/* Application Details Section */}
        <div style={{
          backgroundColor: '#FFFFFF',
          padding: '1.5rem 2.5rem',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          alignItems: 'flex-end',
          gap: '1.5rem',
          flexWrap: 'wrap'
        }}>
          {/* Application Type Dropdown */}
          <div className="custom-input-root">
            <div className="custom-label-wrapper">
              <label htmlFor="application-type">Başvuru Türü</label>
              <div className="line" />
            </div>
            <div className="custom-input-wrapper">
              <select 
                id="application-type"
                value={applicationType} 
                onChange={(e) => dispatch(setApplicationType(e.target.value))}
              >
                <option value="" disabled>Seçiniz</option>
                {Object.entries(APPLICATION_TYPES).map(([key, name]) => (
                  <option key={key} value={key}>{name}</option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Start Date */}
          <div className="custom-input-root">
            <div className="custom-label-wrapper">
              <label htmlFor="start-date">Başlangıç Tarihi</label>
              <div className="line" />
            </div>
            <div className="custom-input-wrapper" onClick={() => startDateInputRef.current.focus()}>
              <input 
                ref={startDateInputRef}
                type="text"
                onFocus={(e) => {
                  e.target.type='date';
                  // This is to make sure the date picker opens on Chrome
                  if (e.target.showPicker) {
                    e.target.showPicker();
                  }
                }}
                onBlur={(e) => {
                  if (!e.target.value) {
                    e.target.type='text';
                  }
                }}
                placeholder="gg.aa.yyyy"
                id="start-date"
                value={startDate || ''}
                onChange={(e) => dispatch(setStartDate(e.target.value))}
              />
              <Calendar size={20} className="icon" />
            </div>
          </div>

          {/* End Date */}
          <div className="custom-input-root">
            <div className="custom-label-wrapper">
              <label htmlFor="end-date">Bitiş Tarihi</label>
              <div className="line" />
            </div>
            <div className="custom-input-wrapper" onClick={() => endDateInputRef.current.focus()}>
              <input 
                ref={endDateInputRef}
                type="text"
                onFocus={(e) => {
                  e.target.type='date';
                  if (e.target.showPicker) {
                    e.target.showPicker();
                  }
                }}
                onBlur={(e) => {
                  if (!e.target.value) {
                    e.target.type='text';
                  }
                }}
                placeholder="gg.aa.yyyy"
                id="end-date"
                value={endDate || ''}
                onChange={(e) => dispatch(setEndDate(e.target.value))}
              />
              <Calendar size={20} className="icon" />
            </div>
          </div>
        </div>

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
              value={originCountry?.code || ''}
              label="Nereden"
              onChange={(e) => handleOriginChange(e.target.value)}
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
                backgroundColor: destinationCountry?.code ? '#F0FDF4' : '#F9FAFB',
                fontWeight: 500,
                fontFamily: '"Playfair Display", serif',
                '& fieldset': {
                  borderColor: destinationCountry?.code ? '#A7F3D0' : '#E5E7EB',
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
                color: destinationCountry?.code ? '#064E3B' : '#9CA3AF',
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
              value={destinationCountry?.code || ''}
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
            disabled={!originCountry?.code || !destinationCountry?.code || !startDate || !endDate || !applicationType}
            className={`
              inline-flex items-center gap-2 px-6 py-3 text-base font-semibold rounded-full
              transition-all duration-300 transform
              ${originCountry?.code && destinationCountry?.code && startDate && endDate && applicationType
                ? 'hover:scale-105 cursor-pointer'
                : 'cursor-not-allowed opacity-50'
              }
            `}
            style={{
              background: originCountry?.code && destinationCountry?.code && startDate && endDate && applicationType
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : '#CCCCCC',
              color: '#FFFFFF',
              boxShadow: originCountry?.code && destinationCountry?.code && startDate && endDate && applicationType
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
