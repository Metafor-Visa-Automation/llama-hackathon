import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../store/authSlice';
import { Person, Login, Logout } from '@mui/icons-material';

/**
 * UserGreeting Component - Dynamic Island Style
 * Shows welcome message if logged in, or login button if not
 */
const UserGreeting = () => {
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  };

  const handleLogoutClick = () => {
    dispatch(logout());
  };

  if (!isAuthenticated) {
    // Not logged in - Show login button in dynamic island style
    return (
      <div
        style={{
          position: 'fixed',
          top: '2rem',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
        }}
      >
        <button
          onClick={handleLoginClick}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.75rem',
            backgroundColor: 'rgba(16, 185, 129, 0.95)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            color: '#FFFFFF',
            padding: '0.875rem 2rem',
            borderRadius: '50px',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            fontSize: '1rem',
            fontWeight: '600',
            fontFamily: '"Playfair Display", serif',
            cursor: 'pointer',
            boxShadow: '0 8px 32px rgba(16, 185, 129, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.05)';
            e.currentTarget.style.boxShadow = '0 12px 40px rgba(16, 185, 129, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = '0 8px 32px rgba(16, 185, 129, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)';
          }}
        >
          <Login sx={{ fontSize: 20 }} />
          <span>Giriş Yap</span>
        </button>
      </div>
    );
  }

  // Logged in - Show welcome message with logout button
  return (
    <div
      style={{
        position: 'fixed',
        top: '2rem',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
      }}
    >
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '1rem',
          backgroundColor: 'rgba(26, 26, 26, 0.95)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          padding: '0.875rem 1.5rem',
          borderRadius: '50px',
          border: '2px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
          animation: 'slideDown 0.5s ease-out',
        }}
      >
        {/* User Avatar Circle */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)',
          }}
        >
          <Person sx={{ fontSize: 20, color: '#FFFFFF' }} />
        </div>

        {/* Welcome Text */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
          <span
            style={{
              color: '#FFFFFF',
              fontSize: '1rem',
              fontWeight: '700',
              fontFamily: '"Playfair Display", serif',
              lineHeight: '1.2',
            }}
          >
            Hoşgeldin, {user?.name || 'Kullanıcı'}
          </span>
          <span
            style={{
              color: 'rgba(255, 255, 255, 0.6)',
              fontSize: '0.75rem',
              fontWeight: '400',
              fontFamily: '"Playfair Display", serif',
            }}
          >
            Vize başvuruna devam et
          </span>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogoutClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            marginLeft: '0.5rem',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
            e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
          }}
          title="Çıkış Yap"
        >
          <Logout sx={{ fontSize: 18, color: '#FFFFFF' }} />
        </button>
      </div>

      {/* Animation Keyframes */}
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translate(-50%, -20px);
          }
          to {
            opacity: 1;
            transform: translate(-50%, 0);
          }
        }
      `}</style>
    </div>
  );
};

export default UserGreeting;

