import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { logout } from '../store/authSlice';
import { Person, Login, Logout, PersonAdd } from '@mui/icons-material';

/**
 * UserGreeting Component - Modern Glassmorphism Style
 * Shows welcome message if logged in, or login/register buttons if not
 * Fades out on scroll down, fades in on scroll up
 */
const UserGreeting = () => {
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      // If scrolling down and past 50px, hide
      if (currentScrollY > lastScrollY && currentScrollY > 50) {
        setIsVisible(false);
      }
      // If scrolling up, show
      else if (currentScrollY < lastScrollY) {
        setIsVisible(true);
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [lastScrollY]);

  const handleLoginClick = () => {
    navigate('/login');
  };

  const handleRegisterClick = () => {
    navigate('/register');
  };

  const handleLogoutClick = () => {
    dispatch(logout());
    // Refresh the page after logout
    window.location.reload();
  };

  if (!isAuthenticated) {
    // Not logged in - Show login and register buttons with modern glassmorphism
    return (
      <div
        style={{
          position: 'fixed',
          top: '2rem',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 0.4s ease-in-out',
          pointerEvents: isVisible ? 'auto' : 'none',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.625rem',
            backgroundColor: '#EBF5CF',
            backgroundImage: `
              url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='2.5' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.15'/%3E%3C/svg%3E")
            `,
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            padding: '0.5rem',
            borderRadius: '50px',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            boxShadow: '0 4px 20px rgba(16, 185, 129, 0.15), 0 0 0 1px rgba(16, 185, 129, 0.1)',
          }}
        >
          {/* Register Button */}
          <button
            onClick={handleRegisterClick}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: 'transparent',
              color: '#2d5016',
              padding: '0.625rem 1.25rem',
              borderRadius: '50px',
              border: 'none',
              fontSize: '0.875rem',
              fontWeight: '600',
              fontFamily: '"Playfair Display", serif',
              cursor: 'pointer',
              transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
              overflow: 'hidden',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(16, 185, 129, 0.12)';
              e.currentTarget.style.color = '#059669';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#2d5016';
            }}
          >
            <PersonAdd sx={{ fontSize: 16 }} />
            <span>Kayıt Ol</span>
          </button>

          {/* Divider */}
          <div
            style={{
              width: '1px',
              height: '20px',
              backgroundColor: 'rgba(16, 185, 129, 0.25)',
            }}
          />

          {/* Login Button */}
          <button
            onClick={handleLoginClick}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#FFFFFF',
              padding: '0.625rem 1.25rem',
              borderRadius: '50px',
              border: 'none',
              fontSize: '0.875rem',
              fontWeight: '600',
              fontFamily: '"Playfair Display", serif',
              cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(16, 185, 129, 0.3)',
              transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
              position: 'relative',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(16, 185, 129, 0.3)';
            }}
          >
            <Login sx={{ fontSize: 16 }} />
            <span>Giriş Yap</span>
          </button>
        </div>
      </div>
    );
  }

  // Logged in - Show modern welcome message with logout button
  return (
    <div
      style={{
        position: 'fixed',
        top: '2rem',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.4s ease-in-out',
        pointerEvents: isVisible ? 'auto' : 'none',
      }}
    >
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.75rem',
          backgroundColor: '#EBF5CF',
          backgroundImage: `
            url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='2.5' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.15'/%3E%3C/svg%3E")
          `,
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          padding: '0.625rem 1rem 0.625rem 0.625rem',
          borderRadius: '50px',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          boxShadow: '0 4px 20px rgba(16, 185, 129, 0.15), 0 0 0 1px rgba(16, 185, 129, 0.1)',
        }}
      >
        {/* User Avatar with gradient ring */}
        <div
          style={{
            position: 'relative',
            padding: '2px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            borderRadius: '50%',
            boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '34px',
              height: '34px',
              borderRadius: '50%',
              backgroundColor: '#EBF5CF',
            }}
          >
            <Person sx={{ fontSize: 19, color: '#059669' }} />
          </div>
        </div>

        {/* Welcome Text with modern typography */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
          <span
            style={{
              color: '#6b8e4e',
              fontSize: '0.625rem',
              fontWeight: '500',
              fontFamily: '"Playfair Display", serif',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
            }}
          >
            Hoşgeldin
          </span>
          <span
            style={{
              color: '#2d5016',
              fontSize: '0.875rem',
              fontWeight: '600',
              fontFamily: '"Playfair Display", serif',
              lineHeight: '1.2',
            }}
          >
            {user?.name || 'Kullanıcı'}
          </span>
        </div>

        {/* Logout Button with modern hover effect */}
        <button
          onClick={handleLogoutClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            cursor: 'pointer',
            transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
            marginLeft: '0.5rem',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
            e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
          title="Çıkış Yap"
        >
          <Logout sx={{ fontSize: 16, color: '#dc2626' }} />
        </button>
      </div>
    </div>
  );
};

export default UserGreeting;

