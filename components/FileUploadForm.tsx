import React, { FormEvent, useState } from "react";
import CustomFileSelector from "./CustomFileSelector";
import PDFPreview from "./PDFPreview";
import classNames from "classnames";

import Link from 'next/link'
const FileUploadForm = () => {
    const [files, setFiles] = useState<File[]>([]);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState("");

    const handleFileSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
        }
    };
    console.log('files',files)
    const handleSubmit = async (e) => {
      e.preventDefault();
      setUploading(true);
      setUploadStatus("Uploading...");
    
      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file, file.name);
      });
    
      try {
        const uploadResponse = await fetch("/api/uploadFiles", {
          method: "POST",
          body: formData,
        });
    
        if (!uploadResponse.ok) {
          throw new Error(`Upload failed with status: ${uploadResponse.status}`);
        }
    
        const uploadedFiles = await uploadResponse.json();
        console.log("uploadedFiles:", uploadedFiles);
    
        if (!Array.isArray(uploadedFiles) || uploadedFiles.length === 0) {
          throw new Error("No files were uploaded");
        }
    
        setUploadStatus("Upload successful! Generating embeddings...");
    
        // Prepare data for generate_embeddings
        const dataForEmbeddings = { files: uploadedFiles };
        console.log("Data for generate_embeddings:", dataForEmbeddings);
    
        // Call the generate_embeddings endpoint
        const embeddingsResponse = await fetch("/api/generate_embeddings", {
          method: "POST",
          body: JSON.stringify(dataForEmbeddings),
          headers: {
            "Content-Type": "application/json",
          },
        });
    
        if (!embeddingsResponse.ok) {
          console.log("Embeddings response:", embeddingsResponse);
          throw new Error(
            `Embeddings generation failed with status: ${embeddingsResponse.status}`
          );
        }
    
        const embeddingsData = await embeddingsResponse.json();
        console.log("Embeddings data:", embeddingsData);
    
        // Persist embeddings data in local storage
        const embeddingsJson = JSON.stringify(embeddingsData);
        localStorage.setItem("embeddings", embeddingsJson);
    
        setUploadStatus("Embeddings generated! Starting chat...");
    
        // Navigate to the chat page
        window.location.href = "/chat";
      } catch (error) {
        console.error("Error:", error);
        setUploadStatus(
          `Error: ${error instanceof Error ? error.message : "Unknown error"}`
        );
      } finally {
        setUploading(false);
      }
    };
    
  
    return (
        <form className="w-full position-fixed" onSubmit={handleSubmit}>
            <div className="flex justify-between">
                <CustomFileSelector
                    accept="application/pdf"
                    onChange={handleFileSelected}
                />
                <Link href="/chat">
                <button
                    type="submit"
                    className={classNames({
                        "bg-violet-50 text-violet-500 hover:bg-violet-100 px-4 py-2 rounded-md": true,
                        "disabled pointer-events-none opacity-40": uploading,
                    })}
                    disabled={uploading}
                >
                    Upload
                </button>
                </Link>
            </div>
            <PDFPreview files={files} />
            {uploadStatus && <p>{uploadStatus}</p>}
        </form>
    );
};

export default FileUploadForm;
