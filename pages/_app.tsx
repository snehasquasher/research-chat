// pages/_app.tsx
import React from 'react';
import RootLayout from '../components/RootLayout';
import '../globals.css';

function MyApp({ Component, pageProps }: { Component: React.ComponentType; pageProps: any }) {
  return (
    <RootLayout>
      <Component {...pageProps} />
    </RootLayout>
  );
}
export default MyApp;
