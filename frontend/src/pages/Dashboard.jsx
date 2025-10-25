import PageTransition from '../components/PageTransition';
import vibeBg from '../assets/vibe-bg1.webp';

/**
 * Dashboard Page Component
 * Shows user's visa applications
 */
const Dashboard = () => {
  return (
    <PageTransition>
      <div
        style={{
          minHeight: '100vh',
          width: '100%',
          background: `linear-gradient(135deg, rgba(235, 245, 207, 0.85) 0%, rgba(207, 245, 215, 0.9) 100%)`,
          backgroundImage: `url(${vibeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
        }}
      >
        <div
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(12px)',
            borderRadius: '24px',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            boxShadow: '0 8px 32px rgba(16, 185, 129, 0.15)',
            padding: '3rem',
            maxWidth: '1200px',
            width: '100%',
            textAlign: 'center',
          }}
        >
          <h1
            style={{
              fontFamily: '"Playfair Display", serif',
              fontSize: '2.5rem',
              fontWeight: '700',
              color: '#2d5016',
              marginBottom: '1rem',
            }}
          >
            Başvurularım
          </h1>
          <p
            style={{
              fontFamily: '"Playfair Display", serif',
              fontSize: '1.125rem',
              color: '#6b8e4e',
              marginBottom: '2rem',
            }}
          >
            Vize başvurularınızı buradan takip edebilirsiniz
          </p>

          {/* Empty state placeholder */}
          <div
            style={{
              padding: '4rem 2rem',
              borderRadius: '16px',
              backgroundColor: 'rgba(16, 185, 129, 0.05)',
              border: '2px dashed rgba(16, 185, 129, 0.2)',
            }}
          >
            <p
              style={{
                fontFamily: '"Playfair Display", serif',
                fontSize: '1rem',
                color: '#6b8e4e',
                fontStyle: 'italic',
              }}
            >
              Henüz başvuru bulunmamaktadır
            </p>
          </div>
        </div>
      </div>
    </PageTransition>
  );
};

export default Dashboard;
