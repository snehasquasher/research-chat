// pages/_app.tsx
import React, { useState } from 'react';
import '../globals.css';

function MyApp({ Component, pageProps }: { Component: React.ComponentType; pageProps: any }) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFileText, setSelectedFileText] = useState('');

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      if (selectedFile?.type == 'text/plain') {
        const contents = await selectedFile.text();
        setSelectedFileText(contents);

        console.log(contents);
      }
    }
  };

  return (
    <div>
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
    </div>
  );
}

export default MyApp;
