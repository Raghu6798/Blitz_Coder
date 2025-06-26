import React, { useState } from 'react';
import Navigation from './components/Navigation';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import Testimonials from './components/Testimonials';
import Pricing from './components/Pricing';
import AuthModal from './components/AuthModal';
import Footer from './components/Footer';

function App() {
  const [authModal, setAuthModal] = useState<{
    isOpen: boolean;
    mode: 'signin' | 'signup';
  }>({
    isOpen: false,
    mode: 'signin'
  });

  const openAuthModal = (mode: 'signin' | 'signup') => {
    setAuthModal({ isOpen: true, mode });
  };

  const closeAuthModal = () => {
    setAuthModal({ isOpen: false, mode: 'signin' });
  };

  const toggleAuthMode = () => {
    setAuthModal(prev => ({
      ...prev,
      mode: prev.mode === 'signin' ? 'signup' : 'signin'
    }));
  };

  const handleGetStarted = () => {
    openAuthModal('signup');
  };

  const handleWatchDemo = () => {
    // TODO: Implement demo modal or redirect
    console.log('Watch demo clicked');
  };

  const handleSelectPlan = (plan: string) => {
    if (plan === 'Enterprise') {
      // TODO: Redirect to contact sales
      console.log('Contact sales for enterprise plan');
    } else {
      openAuthModal('signup');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navigation 
        onSignIn={() => openAuthModal('signin')}
        onSignUp={() => openAuthModal('signup')}
      />
      
      <Hero 
        onGetStarted={handleGetStarted}
        onWatchDemo={handleWatchDemo}
      />
      
      <Features />
      
      <HowItWorks />
      
      <Testimonials />
      
      <Pricing onSelectPlan={handleSelectPlan} />
      
      <Footer />
      
      <AuthModal
        isOpen={authModal.isOpen}
        onClose={closeAuthModal}
        mode={authModal.mode}
        onToggleMode={toggleAuthMode}
      />
    </div>
  );
}

export default App;