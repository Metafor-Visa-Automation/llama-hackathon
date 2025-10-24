import { Edit, Description, CheckCircle } from '@mui/icons-material';

/**
 * ProcessSteps Component
 * Displays the 3-step process of how the Visa Flow application works
 */
const ProcessSteps = () => {
  const steps = [
    {
      id: 1,
      icon: Edit,
      title: 'Bilgilerinizi Girin',
      description: 'Kişisel ve seyahat bilgilerinizi girersiniz',
    },
    {
      id: 2,
      icon: Description,
      title: 'Belgeleri Oluşturun',
      description: 'Yapay zeka destekli belge listesi ve niyet mektubu alırsınız',
    },
    {
      id: 3,
      icon: CheckCircle,
      title: 'Başvuru belgeleriniz hazır!',
      description: 'Oluşturulan belgelerle kolayca başvurunuzu tamamlarsınız',
    },
  ];

  return (
    <section style={{
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      padding: '6rem 2rem',
      borderTop: '1px solid rgba(255, 255, 255, 0.3)'
    }}>
      <div className="container mx-auto">
        <h2
          style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            color: '#000000',
            textAlign: 'center',
            marginBottom: '4rem',
            letterSpacing: '-0.02em',
          }}
        >
          Nasıl Çalışır?
        </h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '3rem',
            maxWidth: '1200px',
            margin: '0 auto',
          }}
        >
          {steps.map((step) => {
            const IconComponent = step.icon;
            return (
              <div key={step.id} style={{ textAlign: 'center' }}>
                <div
                  style={{
                    width: '80px',
                    height: '80px',
                    margin: '0 auto 2rem',
                    backgroundColor: '#F0F0F0',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#000000',
                    fontSize: '2.5rem',
                  }}
                >
                  <IconComponent fontSize="inherit" style={{ fontSize: '2.5rem' }} />
                </div>
                <h3
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: '#000000',
                    marginBottom: '1rem',
                  }}
                >
                  {step.title}
                </h3>
                <p style={{ fontSize: '1rem', color: '#666666', lineHeight: '1.6' }}>
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default ProcessSteps;
