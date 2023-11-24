"use client"; // Make this component a client component
// components/FileUploadForm.tsx
import React, { FormEvent, useState } from "react";
import CustomFileSelector from "./CustomFileSelector";
import PDFPreview from "./PDFPreview";
import classNames from "classnames";

const FileUploadForm = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const handleFileSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      //convert `FileList` to `File[]`
      const _files = Array.from(e.target.files);
      setFiles(_files);
    }
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => { /* removed async */
    e.preventDefault();
    
    const formData = new FormData();
    files.forEach((file, i) => {
      formData.append(file.name, file);
    });
    var req = fetch('/api/uploadFiles', {
        method: 'post',
        body: formData /* or aFile[0]*/
    }); // returns a promise

    req.then(function(response) {
        // returns status + response headers
        // but not yet the body, 
        // for that call `response[text() || json() || arrayBuffer()]` <-- also promise
      
        if (response.ok) {
          // status code was 200-299
          location.href = "/chat"
        } else {
          // status was something else
        }
      }, function(error) {
        console.error('failed due to network error or cross domain')
      })
  };

  return (
    <form className="w-full position-fixed"  onSubmit={handleSubmit}>
    <div className="flex justify-between">
        <CustomFileSelector
            accept="application/pdf, text/plain"
            onChange={handleFileSelected}
        />
        <button
            type="submit"
            className={classNames({
                "bg-violet-50 text-violet-500 hover:bg-violet-100 px-4 py-2 rounded-md":
                  true,
                "disabled pointer-events-none opacity-40": uploading,
              })}
              disabled={uploading}
        >Upload</button>
        </div>
        <PDFPreview files={files} />
      
    </form>
  );
};

export default FileUploadForm;
