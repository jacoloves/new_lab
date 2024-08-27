import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { AdminFlagProvider } from './components/providers/AdminFlagProvider';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <AdminFlagProvider>
    <App />
  </AdminFlagProvider>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals