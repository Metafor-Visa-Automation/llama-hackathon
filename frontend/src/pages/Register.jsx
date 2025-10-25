import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';
import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars
import {
  Person,
  Email,
  Lock,
  Phone,
  CalendarToday,
  Public,
  Work,
  CardTravel,
  Visibility,
  VisibilityOff,
  Speed,
  VerifiedUser,
  Language
} from '@mui/icons-material';

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
  const [focusedField, setFocusedField] = useState('');

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

  return (
    <PageTransition>
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
          fontFamily: '"Playfair Display", serif'
        }}
      >
        {/* Split Layout Container */}
        <div style={{
          display: 'flex',
          width: '100%',
          maxWidth: '1400px',
          margin: 'auto',
          gap: '3rem',
          padding: '2rem'
        }}>

          {/* LEFT SIDE - Motivational Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            style={{
              flex: '1',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              padding: '3rem',
              color: '#1a1a1a'
            }}
          >
            {/* Logo */}
            <div style={{ marginBottom: '3rem' }}>
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}
              >
                <span style={{
                  fontStyle: 'italic',
                  fontSize: '2.5rem',
                  fontWeight: '400',
                  textShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                }}>
                  visa flow
                </span>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" style={{ marginTop: '0.5rem' }}>
                  <path d="M2.5 19L10 12L2.5 5M12.5 19L20 12L12.5 5" stroke="#1a1a1a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </motion.div>
            </div>

            {/* Motivational Text */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              <h1 style={{
                fontSize: '3.5rem',
                fontWeight: '800',
                lineHeight: '1.1',
                marginBottom: '1.5rem'
              }}>
                Dünya Seni <br/>
                <span style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  Bekliyor
                </span>
              </h1>

              <p style={{
                fontSize: '1.25rem',
                lineHeight: '1.7',
                opacity: '0.8',
                marginBottom: '2rem'
              }}>
                Vize başvuru sürecinizi kolaylaştırıyoruz.
                Hayalinizdeki destinasyona ulaşmak için gereken her adımda yanınızdayız.
              </p>

              {/* Features List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {[
                  { Icon: Speed, text: 'Hızlı ve güvenli başvuru süreci' },
                  { Icon: VerifiedUser, text: 'Uzman rehberlik desteği' },
                  { Icon: Language, text: '27 Schengen ülkesine erişim' }
                ].map((feature, index) => {
                  const IconComponent = feature.Icon;
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1, duration: 0.5 }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        fontSize: '1.1rem'
                      }}
                    >
                      <IconComponent style={{
                        fontSize: '28px',
                        color: '#10B981'
                      }} />
                      <span>
                        {feature.text}
                      </span>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          </motion.div>

          {/* RIGHT SIDE - Registration Form */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            style={{
              flex: '1',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(30px)',
              borderRadius: '32px',
              padding: '3rem',
              width: '100%',
              maxWidth: '550px',
              boxShadow: '0 30px 80px rgba(0, 0, 0, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.9)'
            }}>
              {/* Form Header */}
              <div style={{ marginBottom: '2.5rem', textAlign: 'center' }}>
                <h2 style={{
                  fontSize: '2rem',
                  fontWeight: '800',
                  color: '#1a1a1a',
                  marginBottom: '0.5rem'
                }}>
                  Hesap Oluştur
                </h2>
                <p style={{ color: '#666666', fontSize: '1rem' }}>
                  Yolculuğunuz birkaç adım ötede
                </p>
              </div>

              {/* Registration Form */}
              <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* Name & Surname Row */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <CustomInput
                    name="name"
                    placeholder="Ad"
                    value={formData.name}
                    onChange={handleChange}
                    icon={<Person sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                    required
                    focusedField={focusedField}
                    setFocusedField={setFocusedField}
                  />
                  <CustomInput
                    name="surname"
                    placeholder="Soyad"
                    value={formData.surname}
                    onChange={handleChange}
                    icon={<Person sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                    required
                    focusedField={focusedField}
                    setFocusedField={setFocusedField}
                  />
                </div>

                {/* Email */}
                <CustomInput
                  name="email"
                  type="email"
                  placeholder="E-posta"
                  value={formData.email}
                  onChange={handleChange}
                  icon={<Email sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                  required
                  focusedField={focusedField}
                  setFocusedField={setFocusedField}
                />

                {/* Password */}
                <CustomInput
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Şifre"
                  value={formData.password}
                  onChange={handleChange}
                  icon={<Lock sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                  required
                  showPasswordToggle
                  showPassword={showPassword}
                  onTogglePassword={() => setShowPassword(!showPassword)}
                  focusedField={focusedField}
                  setFocusedField={setFocusedField}
                />

                {/* Phone */}
                <CustomInput
                  name="phone"
                  placeholder="Telefon (05001234567)"
                  value={formData.phone}
                  onChange={handleChange}
                  icon={<Phone sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                  required
                  focusedField={focusedField}
                  setFocusedField={setFocusedField}
                />

                {/* Date of Birth */}
                <CustomInput
                  name="date_of_birth"
                  placeholder="Doğum Tarihi (16.07.2000)"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  icon={<CalendarToday sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                  required
                  focusedField={focusedField}
                  setFocusedField={setFocusedField}
                />

                {/* Nationality */}
                <CustomInput
                  name="nationality"
                  placeholder="Uyruk"
                  value={formData.nationality}
                  onChange={handleChange}
                  icon={<Public sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                  required
                  focusedField={focusedField}
                  setFocusedField={setFocusedField}
                />

                {/* Profile Type & Passport Type */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <CustomSelect
                    name="profile_type"
                    value={formData.profile_type}
                    onChange={handleChange}
                    icon={<Work sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                    options={[
                      { value: 'STUDENT', label: 'Öğrenci' },
                      { value: 'EMPLOYEE', label: 'Çalışan' },
                      { value: 'TOURIST', label: 'Turist' }
                    ]}
                    focusedField={focusedField}
                    setFocusedField={setFocusedField}
                  />
                  <CustomSelect
                    name="passport_type"
                    value={formData.passport_type}
                    onChange={handleChange}
                    icon={<CardTravel sx={{ color: '#10B981', fontSize: '1.25rem' }} />}
                    options={[
                      { value: 'BORDO', label: 'Bordo' },
                      { value: 'YESIL', label: 'Yeşil' }
                    ]}
                    focusedField={focusedField}
                    setFocusedField={setFocusedField}
                  />
                </div>

                {/* Error Message */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                      padding: '0.875rem',
                      borderRadius: '12px',
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#EF4444',
                      fontSize: '0.875rem',
                      textAlign: 'center'
                    }}
                  >
                    {error}
                  </motion.div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  style={{
                    marginTop: '0.5rem',
                    padding: '1rem',
                    borderRadius: '16px',
                    border: 'none',
                    background: isLoading ? '#CCCCCC' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: '#FFFFFF',
                    fontSize: '1.1rem',
                    fontWeight: '700',
                    fontFamily: '"Playfair Display", serif',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    boxShadow: isLoading ? 'none' : '0 8px 24px rgba(16, 185, 129, 0.4)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    transform: 'translateY(0)'
                  }}
                  onMouseEnter={(e) => {
                    if (!isLoading) {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 12px 32px rgba(16, 185, 129, 0.5)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = isLoading ? 'none' : '0 8px 24px rgba(16, 185, 129, 0.4)';
                  }}
                >
                  {isLoading ? 'Kayıt Yapılıyor...' : 'Hesap Oluştur'}
                </button>

                {/* Login Link */}
                <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
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
                        fontSize: '0.95rem'
                      }}
                    >
                      Giriş Yap
                    </button>
                  </p>
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
};

// Custom Input Component
const CustomInput = ({
  name,
  type = 'text',
  placeholder,
  value,
  onChange,
  icon,
  required,
  showPasswordToggle,
  showPassword,
  onTogglePassword,
  focusedField,
  setFocusedField
}) => {
  const isFocused = focusedField === name;

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      {/* Icon */}
      <span style={{
        position: 'absolute',
        left: '1rem',
        top: '50%',
        transform: 'translateY(-50%)',
        fontSize: '1.25rem',
        opacity: isFocused ? '1' : '0.6',
        transition: 'all 0.3s ease',
        pointerEvents: 'none',
        zIndex: 1
      }}>
        {icon}
      </span>

      {/* Input */}
      <input
        name={name}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        onFocus={() => setFocusedField(name)}
        onBlur={() => setFocusedField('')}
        style={{
          width: '100%',
          padding: '1rem 1rem 1rem 3.25rem',
          borderRadius: '14px',
          border: isFocused ? '2.5px solid #10B981' : '2.5px solid #E5E7EB',
          backgroundColor: isFocused ? '#F0FDF4' : '#F9FAFB',
          fontSize: '1rem',
          fontFamily: '"Playfair Display", serif',
          color: '#1a1a1a',
          outline: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isFocused ? '0 0 0 4px rgba(16, 185, 129, 0.1)' : 'none'
        }}
      />

      {/* Password Toggle */}
      {showPasswordToggle && (
        <button
          type="button"
          onClick={onTogglePassword}
          style={{
            position: 'absolute',
            right: '1rem',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: '0.6',
            transition: 'opacity 0.2s',
            padding: '0.25rem'
          }}
          onMouseEnter={(e) => e.target.style.opacity = '1'}
          onMouseLeave={(e) => e.target.style.opacity = '0.6'}
        >
          {showPassword ? (
            <VisibilityOff sx={{ fontSize: '1.25rem', color: '#666666' }} />
          ) : (
            <Visibility sx={{ fontSize: '1.25rem', color: '#666666' }} />
          )}
        </button>
      )}
    </div>
  );
};

// Custom Select Component
const CustomSelect = ({ name, value, onChange, icon, options, focusedField, setFocusedField }) => {
  const isFocused = focusedField === name;

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      {/* Icon */}
      <span style={{
        position: 'absolute',
        left: '1rem',
        top: '50%',
        transform: 'translateY(-50%)',
        fontSize: '1.25rem',
        opacity: isFocused ? '1' : '0.6',
        transition: 'all 0.3s ease',
        pointerEvents: 'none',
        zIndex: 1
      }}>
        {icon}
      </span>

      {/* Select */}
      <select
        name={name}
        value={value}
        onChange={onChange}
        onFocus={() => setFocusedField(name)}
        onBlur={() => setFocusedField('')}
        style={{
          width: '100%',
          padding: '1rem 1rem 1rem 3.25rem',
          borderRadius: '14px',
          border: isFocused ? '2.5px solid #10B981' : '2.5px solid #E5E7EB',
          backgroundColor: isFocused ? '#F0FDF4' : '#F9FAFB',
          fontSize: '1rem',
          fontFamily: '"Playfair Display", serif',
          color: '#1a1a1a',
          outline: 'none',
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isFocused ? '0 0 0 4px rgba(16, 185, 129, 0.1)' : 'none',
          appearance: 'none',
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23666666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 1rem center'
        }}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Register;

