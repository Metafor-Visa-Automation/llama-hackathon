import { useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';
import { TextField, Button, Radio, RadioGroup, FormControlLabel, FormControl, FormLabel } from '@mui/material';
import { ArrowBack, Send } from '@mui/icons-material';

/**
 * FillForm Page Component
 * Visa application form with mock questions
 * Questions will eventually come from AI
 */
const FillForm = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  // Country selection data (will be used in future updates)
  // eslint-disable-next-line no-unused-vars
  const { originCountry, destinationCountry } = useSelector((state) => state.country);

  // Mock questions (will be replaced with AI-generated questions)
  const [formData, setFormData] = useState({
    fullName: '',
    passportNumber: '',
    travelPurpose: '',
    travelDuration: '',
    accommodationInfo: '',
    previousVisas: '',
    financialStatus: ''
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // TODO: Send to backend/AI for processing
  };

  return (
    <PageTransition>
      <div 
        className="min-h-screen py-20 px-4"
        style={{
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          style={{
            position: 'fixed',
            top: '2rem',
            left: '2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            padding: '0.75rem 1.5rem',
            borderRadius: '50px',
            border: '1px solid rgba(255, 255, 255, 0.8)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            fontFamily: '"Playfair Display", serif',
            fontWeight: '600',
            color: '#1a1a1a',
            zIndex: 100
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateX(-4px)';
            e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateX(0)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.15)';
          }}
        >
          <ArrowBack sx={{ fontSize: 20 }} />
          <span>Geri Dön</span>
        </button>

        {/* Form Container */}
        <div 
          style={{
            maxWidth: '800px',
            margin: '0 auto',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '24px',
            padding: '3rem',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
            border: '1px solid rgba(255, 255, 255, 0.8)'
          }}
        >
          {/* Header */}
          <div style={{ marginBottom: '2.5rem', textAlign: 'center' }}>
            <h1
              style={{
                fontSize: '2.5rem',
                fontWeight: '800',
                color: '#1a1a1a',
                marginBottom: '0.75rem',
                fontFamily: '"Playfair Display", serif',
              }}
            >
              Vize Başvuru Formu
            </h1>
            <p style={{ 
              color: '#666666', 
              fontSize: '1.1rem',
              fontFamily: '"Playfair Display", serif',
            }}>
              Hoşgeldin {user?.name}, lütfen bilgilerini doldur
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {/* Full Name */}
            <div style={{ marginBottom: '1.5rem' }}>
              <TextField
                fullWidth
                label="Tam Adınız"
                value={formData.fullName}
                onChange={(e) => handleInputChange('fullName', e.target.value)}
                required
                placeholder="Örn: Ahmet Yılmaz"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
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
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  },
                }}
              />
            </div>

            {/* Passport Number */}
            <div style={{ marginBottom: '1.5rem' }}>
              <TextField
                fullWidth
                label="Pasaport Numarası"
                value={formData.passportNumber}
                onChange={(e) => handleInputChange('passportNumber', e.target.value)}
                required
                placeholder="Örn: U12345678"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
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
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  },
                }}
              />
            </div>

            {/* Travel Purpose */}
            <div style={{ marginBottom: '2rem' }}>
              <FormControl component="fieldset">
                <FormLabel 
                  component="legend"
                  sx={{
                    color: '#064E3B',
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    fontSize: '0.95rem',
                    marginBottom: '0.75rem',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  }}
                >
                  Seyahat Amacınız Nedir?
                </FormLabel>
                <RadioGroup
                  value={formData.travelPurpose}
                  onChange={(e) => handleInputChange('travelPurpose', e.target.value)}
                >
                  <FormControlLabel 
                    value="tourism" 
                    control={
                      <Radio 
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    } 
                    label="Turizm"
                    sx={{
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        color: '#1a1a1a',
                      },
                    }}
                  />
                  <FormControlLabel 
                    value="business" 
                    control={
                      <Radio 
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    } 
                    label="İş"
                    sx={{
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        color: '#1a1a1a',
                      },
                    }}
                  />
                  <FormControlLabel 
                    value="education" 
                    control={
                      <Radio 
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    } 
                    label="Eğitim"
                    sx={{
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        color: '#1a1a1a',
                      },
                    }}
                  />
                  <FormControlLabel 
                    value="family" 
                    control={
                      <Radio 
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    } 
                    label="Aile Ziyareti"
                    sx={{
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        color: '#1a1a1a',
                      },
                    }}
                  />
                </RadioGroup>
              </FormControl>
            </div>

            {/* Travel Duration */}
            <div style={{ marginBottom: '1.5rem' }}>
              <TextField
                fullWidth
                label="Seyahat Süresi"
                value={formData.travelDuration}
                onChange={(e) => handleInputChange('travelDuration', e.target.value)}
                required
                placeholder="Örn: 15 gün"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
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
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  },
                }}
              />
            </div>

            {/* Accommodation Info */}
            <div style={{ marginBottom: '1.5rem' }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Konaklama Bilgileri"
                value={formData.accommodationInfo}
                onChange={(e) => handleInputChange('accommodationInfo', e.target.value)}
                required
                placeholder="Nerede kalacaksınız? (Otel adı veya adres)"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
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
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  },
                }}
              />
            </div>

            {/* Previous Visas */}
            <div style={{ marginBottom: '2rem' }}>
              <FormControl component="fieldset">
                <FormLabel 
                  component="legend"
                  sx={{
                    color: '#064E3B',
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    fontSize: '0.95rem',
                    marginBottom: '0.75rem',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  }}
                >
                  Daha Önce Schengen Vizesi Aldınız mı?
                </FormLabel>
                <RadioGroup
                  value={formData.previousVisas}
                  onChange={(e) => handleInputChange('previousVisas', e.target.value)}
                >
                  <FormControlLabel 
                    value="yes" 
                    control={
                      <Radio 
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    } 
                    label="Evet"
                    sx={{
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        color: '#1a1a1a',
                      },
                    }}
                  />
                  <FormControlLabel 
                    value="no" 
                    control={
                      <Radio 
                        sx={{
                          color: '#10B981',
                          '&.Mui-checked': {
                            color: '#059669',
                          },
                        }}
                      />
                    } 
                    label="Hayır"
                    sx={{
                      '& .MuiFormControlLabel-label': {
                        fontFamily: '"Playfair Display", serif',
                        color: '#1a1a1a',
                      },
                    }}
                  />
                </RadioGroup>
              </FormControl>
            </div>

            {/* Financial Status */}
            <div style={{ marginBottom: '2.5rem' }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Mali Durum"
                value={formData.financialStatus}
                onChange={(e) => handleInputChange('financialStatus', e.target.value)}
                required
                placeholder="Seyahatinizi nasıl finanse edeceksiniz?"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
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
                    fontFamily: '"Playfair Display", serif',
                    fontWeight: '600',
                    '&.Mui-focused': {
                      color: '#059669',
                    },
                  },
                }}
              />
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              fullWidth
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#FFFFFF',
                padding: '1rem',
                borderRadius: '50px',
                fontSize: '1.1rem',
                fontWeight: '700',
                textTransform: 'none',
                fontFamily: '"Playfair Display", serif',
                boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(16, 185, 129, 0.5)',
                },
                transition: 'all 0.3s ease',
              }}
              endIcon={<Send />}
            >
              Başvuruyu Gönder
            </Button>
          </form>
        </div>
      </div>
    </PageTransition>
  );
};

export default FillForm;

