import { motion } from 'framer-motion'; // eslint-disable-line no-unused-vars

/**
 * PageTransition Component
 * Provides smooth fade-in/out animations for page transitions
 */
const PageTransition = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{
        duration: 0.7,
        ease: [0.22, 1, 0.36, 1], // Custom cubic-bezier for premium feel
      }}
      style={{
        width: '100%',
        minHeight: '100vh',
      }}
    >
      {children}
    </motion.div>
  );
};

export default PageTransition;

