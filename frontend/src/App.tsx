import React, { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { SettingsPage } from './components/Settings';
import { Header } from './components/Header';
import Trading from './components/Trading';
import { Strategies } from './components/Strategies';

type Page = 'dashboard' | 'settings' | 'trading' | 'strategies';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [isStreaming, setIsStreaming] = useState(false);
  const [balance, setBalance] = useState<number | null>(null);
  const [ticksCount, setTicksCount] = useState(0);

  const handleTicksCountChange = (count: number) => {
    setTicksCount(count);
  };

  const handlePageChange = (page: Page) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-vh-100 bg-dark">
      <Header 
        isStreaming={isStreaming}
        balance={balance}
        ticksCount={ticksCount}
        onPageChange={handlePageChange}
        currentPage={currentPage}
      />
      
      {currentPage === 'dashboard' && (
        <Dashboard 
          onStreamingChange={setIsStreaming}
          onBalanceChange={setBalance}
          onTicksCountChange={handleTicksCountChange}
        />
      )}
      
      {currentPage === 'settings' && <SettingsPage />}
      
      {currentPage === 'trading' && <Trading />}
      
      {currentPage === 'strategies' && <Strategies />}
    </div>
  );
}

export default App;
