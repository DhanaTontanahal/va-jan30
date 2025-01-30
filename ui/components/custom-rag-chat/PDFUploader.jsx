import React, { useState } from "react";
import axios from "axios";
import "./PDFUploader.css";

const PDFUploader = ({ onClose }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [fileUrl, setFileUrl] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
    } else {
      alert("Only PDF files are allowed.");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploadStatus("Uploading...");
      const response = await axios.post(
        "http://localhost:8080/upload", // Change to your backend URL
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setUploadStatus("Upload successful!");
      setFileUrl(response.data.fileUrl);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("Upload failed.");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <span className="close-icon" onClick={onClose}>
          &times;
        </span>
        <h2>Upload a PDF</h2>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
        />
        <button onClick={handleUpload} disabled={!file}>
          Upload
        </button>
        <p>{uploadStatus}</p>

        {fileUrl && (
          <div>
            <h3>File Uploaded Successfully!</h3>
            <a href={fileUrl} target="_blank" rel="noopener noreferrer">
              View PDF
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default PDFUploader;
