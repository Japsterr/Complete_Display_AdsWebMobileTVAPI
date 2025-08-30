import { useState } from "react";
import { uploadMedia } from "../services/api";

export default function UploadModal({ onClose }: { onClose: () => void }) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(selectedFiles);
      console.log("Files selected:", selectedFiles.map(f => f.name));
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setError("");
    
    try {
      for (const file of files) {
        await uploadMedia(file);
      }
      onClose(); // Close modal on success
    } catch (err: any) {
      setError("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="modal show d-block" style={{ zIndex: 1050 }}>
      {/* Backdrop - only this should close the modal when clicked */}
      <div 
        className="modal-backdrop show" 
        onClick={onClose}
        style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          width: '100%', 
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.4)' // Less dark backdrop
        }}
      ></div>
      {/* Modal Dialog - clicking inside should NOT close the modal */}
      <div className="modal-dialog modal-dialog-centered" style={{ position: 'relative', zIndex: 1051 }}>
        <div 
          className="modal-content"
          onClick={(e) => e.stopPropagation()} // Prevent clicks inside modal from bubbling up
        >
          <div className="modal-header">
            <h5 className="modal-title">Upload Media Files</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}
            
            <div className="mb-3">
              <label className="form-label">Select files to upload:</label>
              <input
                type="file"
                multiple
                className="form-control"
                accept="image/*,video/*"
                onChange={handleFileSelect}
              />
              <div className="form-text">Choose images or videos (max 10MB each)</div>
            </div>

            {files.length > 0 && (
              <div className="mb-3">
                <h6>Selected Files ({files.length}):</h6>
                <ul className="list-group">
                  {files.map((file, index) => (
                    <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                      <span>{file.name}</span>
                      <span className="badge bg-secondary">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={uploading}>
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={files.length === 0 || uploading}
            >
              {uploading ? "Uploading..." : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}