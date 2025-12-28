import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="flex items-center p-4 pb-2 justify-between sticky top-0 z-50 bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-sm">
      <div className="w-12">
        {/* Placeholder for balance */}
      </div>
      <h2 className="text-lg font-bold leading-tight tracking-[-0.015em] text-center dark:text-white">Nostalgia</h2>
      <div className="flex w-12 items-center justify-end">
        <div className="flex items-center justify-center rounded-lg h-10 w-10 text-primary">
          <span className="material-symbols-outlined">wifi</span>
        </div>
      </div>
    </header>
  );
};
