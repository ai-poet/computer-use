import React from 'react';
import { createRoot } from 'react-dom/client';
import { ConsolePage } from './pages/ConsolePage';
import './styles.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConsolePage />
  </React.StrictMode>
);
