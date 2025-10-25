import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import { 
  TextField, 
  Button, 
  InputAdornment, 
  IconButton,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import { Visibility, VisibilityOff, Mail, Lock, Person, Phone, CalendarToday, Public } from '@mui/icons-material';
import { motion } from 'framer-motion';

/**
 * Register Page Component
 * Allows users to create a new account
 */
const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    surname: '',
    profile_type: 'STUDENT',
    passport_type: 'BORDO',
    phone: '',
    date_of_birth: '',
    nationality: 'Turkish'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  /**
   * Handle register form submission
   */
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Call backend register API (proxied through Vite dev server)
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 
          'accept': 'application/json',
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      // Check if registration was successful
      if (!response.ok) {
        setError(data.detail || 'Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.');
        setIsLoading(false);
        return;
      }

      // Registration successful - redirect to login page
      alert('Kayıt başarılı! Giriş yapabilirsiniz.');
      navigate('/login');
    } catch (err) {
      setError('Kayıt başarısız. Lütfen tekrar deneyin.');
      console.error('Register error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyles = {
    marginBottom: '1.25rem',
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
      '&.Mui-focused': {
        color: '#059669',
      },
    },
  };

  return (
    <PageTransition>
      <div 
        className="min-h-screen flex items-center justify-center px-4 py-8"
        style={{
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        {/* Register Card */}
        <div 
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            borderRadius: '24px',
            padding: '2.5rem',
            maxWidth: '600px',
            width: '100%',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
            border: '1px solid rgba(255, 255, 255, 0.8)'
          }}
        >
          {/* Logo & Brand */}
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <motion.div
              key="badge-animation"
              initial="hidden"
              animate="visible"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '1rem'
              }}
            >
              <span
                style={{
                  fontStyle: 'italic',
                  fontSize: '2rem',
                  color: '#064E3B',
                  fontWeight: '400'
                }}
              >
                visa flow
              </span>
              <FlightTakeoffIcon sx={{ fontSize: 32, color: '#064E3B', paddingTop: '0.5rem' }} />
            </motion.div>
            
            <h1
              style={{
                fontSize: '1.75rem',
                fontWeight: '800',
                color: '#1a1a1a',
                marginBottom: '0.5rem'
              }}
            >
              Hesap Oluştur
            </h1>
            <p style={{ color: '#666666', fontSize: '0.95rem' }}>
              Vize başvuru sürecinize başlamak için kaydolun
            </p>
          </div>

          {/* Register Form */}
          <form onSubmit={handleRegister}>
            {/* Name & Surname Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <TextField
                fullWidth
                name="name"
                label="Ad"
                value={formData.name}
                onChange={handleChange}
                required
                sx={inputStyles}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person sx={{ color: '#10B981' }} />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                name="surname"
                label="Soyad"
                value={formData.surname}
                onChange={handleChange}
                required
                sx={inputStyles}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person sx={{ color: '#10B981' }} />
                    </InputAdornment>
                  ),
                }}
              />
            </div>

            {/* Email Input */}
            <TextField
              fullWidth
              type="email"
              name="email"
              label="E-posta"
              value={formData.email}
              onChange={handleChange}
              required
              sx={inputStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Mail sx={{ color: '#10B981' }} />
                  </InputAdornment>
                ),
              }}
            />

            {/* Password Input */}
            <TextField
              fullWidth
              type={showPassword ? 'text' : 'password'}
              name="password"
              label="Şifre"
              value={formData.password}
              onChange={handleChange}
              required
              sx={inputStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock sx={{ color: '#10B981' }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            {/* Phone Input */}
            <TextField
              fullWidth
              name="phone"
              label="Telefon"
              placeholder="05001234567"
              value={formData.phone}
              onChange={handleChange}
              required
              sx={inputStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Phone sx={{ color: '#10B981' }} />
                  </InputAdornment>
                ),
              }}
            />

            {/* Date of Birth Input */}
            <TextField
              fullWidth
              name="date_of_birth"
              label="Doğum Tarihi"
              placeholder="16.07.2000"
              value={formData.date_of_birth}
              onChange={handleChange}
              required
              sx={inputStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <CalendarToday sx={{ color: '#10B981' }} />
                  </InputAdornment>
                ),
              }}
            />

            {/* Nationality Input */}
            <TextField
              fullWidth
              name="nationality"
              label="Uyruk"
              value={formData.nationality}
              onChange={handleChange}
              required
              sx={inputStyles}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Public sx={{ color: '#10B981' }} />
                  </InputAdornment>
                ),
              }}
            />

            {/* Profile Type & Passport Type Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <FormControl fullWidth sx={inputStyles}>
                <InputLabel id="profile-type-label" sx={{ 
                  color: '#064E3B',
                  fontFamily: '"Playfair Display", serif',
                  '&.Mui-focused': { color: '#059669' }
                }}>
                  Profil Tipi
                </InputLabel>
                <Select
                  labelId="profile-type-label"
                  name="profile_type"
                  value={formData.profile_type}
                  onChange={handleChange}
                  label="Profil Tipi"
                  sx={{
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
                    fontFamily: '"Playfair Display", serif',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#A7F3D0',
                      borderWidth: '2px',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#10B981',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#10B981',
                      borderWidth: '2px',
                    },
                  }}
                >
                  <MenuItem value="STUDENT">Öğrenci</MenuItem>
                  <MenuItem value="EMPLOYEE">Çalışan</MenuItem>
                  <MenuItem value="TOURIST">Turist</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={inputStyles}>
                <InputLabel id="passport-type-label" sx={{ 
                  color: '#064E3B',
                  fontFamily: '"Playfair Display", serif',
                  '&.Mui-focused': { color: '#059669' }
                }}>
                  Pasaport Tipi
                </InputLabel>
                <Select
                  labelId="passport-type-label"
                  name="passport_type"
                  value={formData.passport_type}
                  onChange={handleChange}
                  label="Pasaport Tipi"
                  sx={{
                    borderRadius: '12px',
                    backgroundColor: '#F0FDF4',
                    fontFamily: '"Playfair Display", serif',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#A7F3D0',
                      borderWidth: '2px',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#10B981',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#10B981',
                      borderWidth: '2px',
                    },
                  }}
                >
                  <MenuItem value="BORDO">Bordo (Kırmızı)</MenuItem>
                  <MenuItem value="YESIL">Yeşil</MenuItem>
                </Select>
              </FormControl>
            </div>

            {/* Error Message */}
            {error && (
              <p style={{ color: '#EF4444', fontSize: '0.875rem', marginBottom: '1rem', marginTop: '-0.5rem' }}>
                {error}
              </p>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              fullWidth
              disabled={isLoading}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: '#FFFFFF',
                padding: '0.875rem',
                borderRadius: '12px',
                fontSize: '1rem',
                fontWeight: '700',
                textTransform: 'none',
                fontFamily: '"Playfair Display", serif',
                boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
                marginTop: '0.5rem',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(16, 185, 129, 0.5)',
                },
                '&:disabled': {
                  background: '#CCCCCC',
                  color: '#FFFFFF',
                },
                transition: 'all 0.3s ease',
              }}
            >
              {isLoading ? 'Kayıt yapılıyor...' : 'Kayıt Ol'}
            </Button>

            {/* Login Link */}
            <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
              <p style={{ color: '#666666', fontSize: '0.95rem' }}>
                Zaten hesabınız var mı?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  style={{
                    color: '#10B981',
                    fontWeight: '600',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    textDecoration: 'underline',
                    fontFamily: '"Playfair Display", serif',
                  }}
                >
                  Giriş Yap
                </button>
              </p>
            </div>
          </form>
        </div>
      </div>
    </PageTransition>
  );
};

export default Register;

