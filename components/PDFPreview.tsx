// components/ImagePreview.tsx
import React, { useState } from "react";

type Props = {
	files: File[];
};

const PDFPreview = ({ files }: Props) => {
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
			<ul >
				{files.map((file) => {
					return (
						<li key={file.name}>
							{file.type === 'application/pdf' && (
								<div>
									<h2 className={`group rounded-lg mb-3 font-semibold`}>PDF Preview of {file.name}:</h2>
									<embed src={URL.createObjectURL(file)} type="application/pdf" width="100%" height="500px" />
								</div>
							)}
							{file.type === 'text/plain' && (
								<div>
									<h2 className={`group rounded-lg mb-3 font-semibold`}>Text File Preview of {file.name}:</h2>
									<embed src={URL.createObjectURL(file)} type="text/plain" width="100%" height="500px" />
								</div>
							)}
						</li>
					);
				})}
			</ul>
		</div>
	);
};

export default PDFPreview;
