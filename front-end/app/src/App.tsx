import { useState, useEffect } from 'react';
import { Route, Switch } from 'wouter';
import Layout from './components/Layout';
import NewspaperComposer from './components/NewspaperComposer';
import DeliveryAnimation from './components/DeliveryAnimation';

function AppContent() {
  const [showDelivery, setShowDelivery] = useState(false);

  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    const lastSeen = localStorage.getItem('muse_delivery_seen');
    if (lastSeen !== today) {
      setShowDelivery(true);
    }
  }, []);

  const handleAnimationComplete = () => {
    localStorage.setItem('muse_delivery_seen', new Date().toISOString().split('T')[0]);
    setShowDelivery(false);
  };

  const handleSkip = () => {
    localStorage.setItem('muse_delivery_seen', new Date().toISOString().split('T')[0]);
    setShowDelivery(false);
  };

  return (
    <>
      {showDelivery && (
        <DeliveryAnimation onComplete={handleAnimationComplete} onSkip={handleSkip} />
      )}
      <NewspaperComposer />
    </>
  );
}

export default function App() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={AppContent} />
        <Route path="/newspaper" component={NewspaperComposer} />
      </Switch>
    </Layout>
  );
}
