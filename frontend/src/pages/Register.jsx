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
  Language,
  Wc,
  Home,
  CheckCircle
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
    gender: 'MALE',
    phone: '',
    date_of_birth: '',
    nationality: 'Turkish',
    address: '',
    has_schengen_before: false
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
                  otovize
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
              borderRadius: '24px',
              padding: '2rem 2.5rem',
              width: '100%',
              maxWidth: '550px',
              boxShadow: '0 30px 80px rgba(0, 0, 0, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.9)'
            }}>
              {/* Form Header */}
              <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                <h2 style={{
                  fontSize: '1.75rem',
                  fontWeight: '800',
                  color: '#1a1a1a',
                  marginBottom: '0.25rem'
                }}>
                  Hesap Oluştur
                </h2>
                <p style={{ color: '#666666', fontSize: '0.9rem', margin: 0 }}>
                  Yolculuğunuz birkaç adım ötede
                </p>
              </div>

              {/* Registration Form */}
              <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                {/* Name & Surname */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <CustomInput name="name" placeholder="Ad" value={formData.name} onChange={handleChange} icon={<Person sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />
                  <CustomInput name="surname" placeholder="Soyad" value={formData.surname} onChange={handleChange} icon={<Person sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />
                </div>

                {/* Email & Password */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <CustomInput name="email" type="email" placeholder="E-posta" value={formData.email} onChange={handleChange} icon={<Email sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />
                  <CustomInput name="password" type={showPassword ? 'text' : 'password'} placeholder="Şifre" value={formData.password} onChange={handleChange} icon={<Lock sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required showPasswordToggle showPassword={showPassword} onTogglePassword={() => setShowPassword(!showPassword)} focusedField={focusedField} setFocusedField={setFocusedField} />
                </div>

                {/* Phone & Date of Birth */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <CustomInput name="phone" placeholder="Telefon" value={formData.phone} onChange={handleChange} icon={<Phone sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />
                  <CustomInput name="date_of_birth" placeholder="Doğum Tarihi" value={formData.date_of_birth} onChange={handleChange} icon={<CalendarToday sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />
                </div>

                {/* Nationality & Gender */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <CustomInput name="nationality" placeholder="Uyruk" value={formData.nationality} onChange={handleChange} icon={<Public sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />
                  <CustomSelect name="gender" value={formData.gender} onChange={handleChange} icon={<Wc sx={{ color: '#10B981', fontSize: '1.1rem' }} />} options={[{ value: 'MALE', label: 'Erkek' }, { value: 'FEMALE', label: 'Kadın' }, { value: 'OTHER', label: 'Diğer' }]} focusedField={focusedField} setFocusedField={setFocusedField} />
                </div>

                {/* Address */}
                <CustomInput name="address" placeholder="Adres" value={formData.address} onChange={handleChange} icon={<Home sx={{ color: '#10B981', fontSize: '1.1rem' }} />} required focusedField={focusedField} setFocusedField={setFocusedField} />

                {/* Profile Type & Passport Type */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <CustomSelect name="profile_type" value={formData.profile_type} onChange={handleChange} icon={<Work sx={{ color: '#10B981', fontSize: '1.1rem' }} />} options={[{ value: 'STUDENT', label: 'Öğrenci' }, { value: 'EMPLOYEE', label: 'Çalışan' }, { value: 'TOURIST', label: 'Turist' }]} focusedField={focusedField} setFocusedField={setFocusedField} />
                  <CustomSelect name="passport_type" value={formData.passport_type} onChange={handleChange} icon={<CardTravel sx={{ color: '#10B981', fontSize: '1.1rem' }} />} options={[{ value: 'BORDO', label: 'Bordo' }, { value: 'YESIL', label: 'Yeşil' }]} focusedField={focusedField} setFocusedField={setFocusedField} />
                </div>

                {/* Schengen Before */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.65rem',
                    padding: '0.75rem 1rem',
                    borderRadius: '12px',
                    border: formData.has_schengen_before ? '2px solid #10B981' : '2px solid #E5E7EB',
                    backgroundColor: formData.has_schengen_before ? '#F0FDF4' : '#F9FAFB',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: formData.has_schengen_before ? '0 0 0 3px rgba(16, 185, 129, 0.1)' : 'none'
                  }}
                  onClick={() => setFormData({ ...formData, has_schengen_before: !formData.has_schengen_before })}
                  onMouseEnter={(e) => {
                    if (!formData.has_schengen_before) {
                      e.currentTarget.style.borderColor = '#10B981';
                      e.currentTarget.style.backgroundColor = '#F0FDF4';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!formData.has_schengen_before) {
                      e.currentTarget.style.borderColor = '#E5E7EB';
                      e.currentTarget.style.backgroundColor = '#F9FAFB';
                    }
                  }}
                >
                  <CheckCircle sx={{
                    color: formData.has_schengen_before ? '#10B981' : '#9CA3AF',
                    fontSize: '1.3rem',
                    transition: 'color 0.3s ease'
                  }} />
                  <span style={{
                    fontSize: '0.95rem',
                    fontFamily: '"Playfair Display", serif',
                    color: '#1a1a1a',
                    fontWeight: formData.has_schengen_before ? '600' : '400',
                    transition: 'font-weight 0.3s ease'
                  }}>
                    Daha önce Schengen vizesi aldım
                  </span>
                </div>

                {/* Error Message */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                      padding: '0.75rem',
                      borderRadius: '10px',
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#EF4444',
                      fontSize: '0.85rem',
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
                    padding: '0.875rem',
                    borderRadius: '12px',
                    border: 'none',
                    background: isLoading ? '#CCCCCC' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: '#FFFFFF',
                    fontSize: '1rem',
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
                <div style={{ textAlign: 'center', marginTop: '0.25rem' }}>
                  <p style={{ color: '#666666', fontSize: '0.9rem', margin: 0 }}>
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
                        fontSize: '0.9rem',
                        padding: 0
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
        left: '0.85rem',
        top: '50%',
        transform: 'translateY(-50%)',
        fontSize: '1.1rem',
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
          padding: '0.75rem 0.75rem 0.75rem 2.75rem',
          borderRadius: '12px',
          border: isFocused ? '2px solid #10B981' : '2px solid #E5E7EB',
          backgroundColor: isFocused ? '#F0FDF4' : '#F9FAFB',
          fontSize: '0.95rem',
          fontFamily: '"Playfair Display", serif',
          color: '#1a1a1a',
          outline: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isFocused ? '0 0 0 3px rgba(16, 185, 129, 0.1)' : 'none'
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
        left: '0.85rem',
        top: '50%',
        transform: 'translateY(-50%)',
        fontSize: '1.1rem',
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
          padding: '0.75rem 0.75rem 0.75rem 2.75rem',
          borderRadius: '12px',
          border: isFocused ? '2px solid #10B981' : '2px solid #E5E7EB',
          backgroundColor: isFocused ? '#F0FDF4' : '#F9FAFB',
          fontSize: '0.95rem',
          fontFamily: '"Playfair Display", serif',
          color: '#1a1a1a',
          outline: 'none',
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isFocused ? '0 0 0 3px rgba(16, 185, 129, 0.1)' : 'none',
          appearance: 'none',
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23666666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 0.75rem center'
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

