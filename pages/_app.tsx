// pages/_app.tsx
import React, { useState } from 'react';
import '../globals.css';

function MyApp({ Component, pageProps }: { Component: React.ComponentType; pageProps: any }) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFileText, setSelectedFileText] = useState('');

  const handleUpload = async () => {
    if (selectedFile) {
      const formData = new FormData();
      formData.append('pdf', selectedFile);

      try {
        const response = await fetch('http://127.0.0.1:5328/api/processDocs', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        console.log(data);
        // Handle the response data here

      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  };

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
