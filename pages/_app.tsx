// pages/_app.tsx
import React, { useState } from 'react';
import '../globals.css';
import RootLayout from '../components/RootLayout';

function MyApp({ Component, pageProps }: { Component: React.ComponentType; pageProps: any }) {
  


  return (
    <RootLayout>
      <Component {...pageProps} />
    </RootLayout>
    /* <div>
      <input type="file" onChange={handleFileChange} />
      {selectedFile && selectedFile.type === 'application/pdf' && (
        <div>
          <h2>PDF Preview:</h2>
          <embed src={URL.createObjectURL(selectedFile)} type="application/pdf" width="100%" height="500px" />
        </div>
      )}
      {selectedFile && selectedFile.type === 'text/plain' && (
        <div>
          <h2>Text File Preview:</h2>
          <p>{selectedFileText}</p>
        </div>
      )}
    </div>  */
  );
}

export default MyApp;
