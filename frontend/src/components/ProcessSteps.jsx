import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars
import { Edit, Description, CheckCircle } from '@mui/icons-material';

/**
 * ProcessSteps Component
 * Displays the 3-step process with modern design and scroll animations
 */
const ProcessSteps = () => {
  const steps = [
    {
      id: 1,
      icon: Edit,
      title: 'Bilgilerinizi Girin',
      description: 'Kişisel ve seyahat bilgilerinizi kolayca girersiniz',
      gradient: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
    },
    {
      id: 2,
      icon: Description,
      title: 'Belgeleri Oluşturun',
      description: 'Yapay zeka destekli belge listesi ve niyet mektubu alırsınız',
      gradient: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
    },
    {
      id: 3,
      icon: CheckCircle,
      title: 'Başvurunuz Hazır!',
      description: 'Oluşturulan belgelerle kolayca başvurunuzu tamamlarsınız',
      gradient: 'linear-gradient(135deg, #047857 0%, #064E3B 100%)',
    },
  ];

  // Container animation for title - Slower, more elegant
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.3,
        delayChildren: 0.2,
      },
    },
  };

  // Individual card animation
  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: 60,
      scale: 0.9,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.8,
        ease: [0.22, 1, 0.36, 1],
      },
    },
  };

  // Title animation
  const titleVariants = {
    hidden: { opacity: 0, y: 40 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.9,
        ease: [0.22, 1, 0.36, 1],
      },
    },
  };

  return (
    <section style={{
      background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 253, 244, 0.98) 100%)',
      backdropFilter: 'blur(20px)',
      padding: '6rem 2rem',
      borderTop: '1px solid rgba(16, 185, 129, 0.1)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Decorative background elements */}
      <div style={{
        position: 'absolute',
        top: '10%',
        right: '-5%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        pointerEvents: 'none',
      }}></div>
      <div style={{
        position: 'absolute',
        bottom: '10%',
        left: '-5%',
        width: '350px',
        height: '350px',
        background: 'radial-gradient(circle, rgba(5, 150, 105, 0.06) 0%, transparent 70%)',
        borderRadius: '50%',
        pointerEvents: 'none',
      }}></div>

      <div className="container mx-auto" style={{ position: 'relative', zIndex: 10 }}>
        <motion.h2
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={titleVariants}
          style={{
            fontSize: '3rem',
            fontWeight: '800',
            color: '#1A1A1A',
            textAlign: 'center',
            marginBottom: '1rem',
            letterSpacing: '-0.03em',
            fontFamily: '"Playfair Display", serif',
          }}
        >
          Nasıl Çalışır?
        </motion.h2>
        
        <motion.p
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={titleVariants}
          style={{
            fontSize: '1.15rem',
            color: '#666666',
            textAlign: 'center',
            marginBottom: '5rem',
            maxWidth: '600px',
            margin: '0 auto 5rem',
            fontFamily: '"Playfair Display", serif',
          }}
        >
          Vize başvurunuzu 3 basit adımda tamamlayın
        </motion.p>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={containerVariants}
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '2.5rem',
            maxWidth: '1200px',
            margin: '0 auto',
          }}
        >
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            return (
              <motion.div
                key={step.id}
                variants={cardVariants}
                whileHover={{ 
                  y: -8,
                  transition: { duration: 0.3 },
                }}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '24px',
                  padding: '2.5rem 2rem',
                  textAlign: 'center',
                  border: '2px solid rgba(16, 185, 129, 0.1)',
                  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.08)',
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 20px 60px rgba(16, 185, 129, 0.15)';
                  e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.08)';
                  e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.1)';
                }}
              >
                {/* Step number badge */}
                <div style={{
                  position: 'absolute',
                  top: '1.5rem',
                  right: '1.5rem',
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: step.gradient,
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.875rem',
                  fontWeight: '700',
                  fontFamily: '"Playfair Display", serif',
                  boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                }}>
                  {step.id}
                </div>

                {/* Icon container with gradient */}
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  whileInView={{ scale: 1, rotate: 0 }}
                  viewport={{ once: true }}
                  transition={{
                    delay: index * 0.3 + 0.4,
                    duration: 0.9,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                  style={{
                    width: '96px',
                    height: '96px',
                    margin: '0 auto 2rem',
                    background: step.gradient,
                    borderRadius: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#FFFFFF',
                    boxShadow: '0 8px 24px rgba(16, 185, 129, 0.3)',
                    transform: 'rotate(-5deg)',
                  }}
                >
                  <IconComponent style={{ fontSize: '3rem' }} />
                </motion.div>

                {/* Title */}
                <h3
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: '#1A1A1A',
                    marginBottom: '1rem',
                    fontFamily: '"Playfair Display", serif',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {step.title}
                </h3>

                {/* Description */}
                <p style={{
                  fontSize: '1rem',
                  color: '#666666',
                  lineHeight: '1.7',
                  fontFamily: '"Playfair Display", serif',
                }}>
                  {step.description}
                </p>

                {/* Bottom accent line */}
                <div style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: step.gradient,
                  opacity: 0.6,
                }}></div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
};

export default ProcessSteps;
