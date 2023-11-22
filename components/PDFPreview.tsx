// components/ImagePreview.tsx
import React from "react";
import Image from "next/image";

type Props = {
   files: File[];
};

const PDFPreview = ({ files }: Props) => {
  return (
    <div>
      <ul >
        {files.map((file) => {
          return (
            <li key={file.name}>
                <p>{file.name}</p>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default PDFPreview;
