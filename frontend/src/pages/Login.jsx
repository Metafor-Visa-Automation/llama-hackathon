import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { loginSuccess } from '../store/authSlice';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';
import FlightTakeoffIcon from '@mui/icons-material/FlightTakeoff';
import { TextField, Button, InputAdornment, IconButton } from '@mui/material';
import { Visibility, VisibilityOff, Mail, Lock } from '@mui/icons-material';
import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars

/**
 * Login Page Component
 * Allows users to login with email and password
 */
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const dispatch = useDispatch();
  const navigate = useNavigate();

  /**
   * Handle login form submission
   */
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // TODO: Backend login API entegrasyonu yapılacak
      // const response = await fetch('/api/auth/login', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password })
      // });
      // const data = await response.json();

      // Simulated login for now (backend hazır olunca kaldırılacak)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock credentials kontrolü
      const MOCK_EMAIL = 'test@mail.com';
      const MOCK_PASSWORD = 'test123';
      
      if (email !== MOCK_EMAIL || password !== MOCK_PASSWORD) {
        setError('E-posta veya şifre hatalı. Lütfen tekrar deneyin.');
        setIsLoading(false);
        return;
      }
      
      // Extract name from email (before @)
      const name = email.split('@')[0];
      const capitalizedName = name.charAt(0).toUpperCase() + name.slice(1);

      // Dispatch login success action
      dispatch(loginSuccess({
        user: { name: capitalizedName, email },
        token: 'mock-jwt-token' // TODO: Backend'den gelecek gerçek token
      }));

      // Navigate to landing page
      navigate('/');
    } catch (err) {
      setError('Giriş başarısız. Lütfen bilgilerinizi kontrol edin.');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageTransition>
      <div 
        className="min-h-screen flex items-center justify-center px-4"
        style={{
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        {/* Login Card */}
        <div 
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px',
          padding: '3rem',
          maxWidth: '450px',
          width: '100%',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
          border: '1px solid rgba(255, 255, 255, 0.8)'
        }}
      >
        {/* Logo & Brand */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          {/* Brand text */}
          <motion.div
                key="badge-animation"
                initial="hidden"
                animate="visible"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '1.5rem'
                }}
              >
                <span
                  style={{
                    fontStyle: 'italic',
                    fontSize: '2.5rem',
                    color: '#064E3B',
                    fontWeight: '400'
                  }}
                >
                  visa flow
                </span>
                <FlightTakeoffIcon sx={{ fontSize: 36, color: '#064E3B', paddingTop: '0.5rem' }} />
              </motion.div>
          
          <h1
            style={{
              fontSize: '2rem',
              fontWeight: '800',
              color: '#1a1a1a',
              marginBottom: '0.5rem'
            }}
          >
            Hoş Geldiniz
          </h1>
          <p style={{ color: '#666666', fontSize: '1rem' }}>
            Hesabınıza giriş yapın
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin}>
          {/* Email Input */}
          <TextField
            fullWidth
            type="email"
            label="E-posta"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            sx={{
              marginBottom: '1.5rem',
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
            }}
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
            label="Şifre"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            sx={{
              marginBottom: '1rem',
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
            }}
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

          {/* Error Message */}
          {error && (
            <p style={{ color: '#EF4444', fontSize: '0.875rem', marginBottom: '1rem' }}>
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
            {isLoading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
          </Button>
        </form>
      </div>
      </div>
    </PageTransition>
  );
};

export default Login;

