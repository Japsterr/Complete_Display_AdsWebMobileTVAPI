import { useEffect, useState } from "react";
import { PlusIcon } from "@heroicons/react/24/outline";
import api from "../services/api.ts";
import UploadModal from "../components/UploadModal.tsx";

type Media = {
  media_id: number;
  file: string;
  name: string;
  description?: string;
  uploaded_at: string;
  // Legacy field support
  id?: string | number;
  thumbnail_url?: string;
  file_url?: string;
  url?: string;
  file_name?: string;
  [key: string]: any; // Allow other fields from API
};

export default function MediaLibraryPage() {
  const [media, setMedia] = useState<Media[]>([]);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [previewMedia, setPreviewMedia] = useState<Media | null>(null);

  const handlePreview = (mediaItem: Media) => {
    setPreviewMedia(mediaItem);
  };

  const handleEdit = (mediaItem: Media) => {
    const newName = prompt("Enter new name:", mediaItem.name);
    if (newName && newName.trim() !== "") {
      api.patch(`/media/${mediaItem.media_id}/`, { name: newName.trim() })
        .then(() => {
          // Refresh media list
          api.get("/media/").then(res => setMedia(res.data));
        })
        .catch(error => {
          console.error("Error updating media:", error);
          alert("Failed to update media name");
        });
    }
  };

  const handleDelete = (mediaItem: Media) => {
    if (confirm(`Are you sure you want to delete "${mediaItem.name}"?`)) {
      api.delete(`/media/${mediaItem.media_id}/`)
        .then(() => {
          // Remove from local state
          setMedia(media.filter(m => m.media_id !== mediaItem.media_id));
        })
        .catch(error => {
          console.error("Error deleting media:", error);
          alert("Failed to delete media");
        });
    }
  };

  useEffect(() => {
    api.get("/media/").then(res => {
      console.log("Media API response:", res.data);
      if (res.data.length > 0) {
        console.log("First media item:", res.data[0]);
        console.log("Available fields:", Object.keys(res.data[0]));
      }
      setMedia(res.data);
    });
  }, []);

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1 className="h2 mb-1">Media Library</h1>
          <p className="text-muted">
            Upload and manage your media files for digital signage campaigns.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setUploadOpen(true)}
        >
          <PlusIcon style={{ width: '16px', height: '16px' }} className="me-2" />
          Upload Media
        </button>
      </div>

      {media.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-5">
            <PlusIcon style={{ width: '64px', height: '64px' }} className="text-muted mb-3" />
            <h4 className="card-title">No Media Files Yet</h4>
            <p className="card-text text-muted mb-4">
              Start by uploading your first image or video file to create engaging campaigns.
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setUploadOpen(true)}
            >
              <PlusIcon style={{ width: '16px', height: '16px' }} className="me-2" />
              Upload Your First Media
            </button>
          </div>
        </div>
      ) : (
        <div className="row g-4">
          {media.map(item => (
            <div key={item.media_id} className="col-sm-6 col-md-4 col-lg-3">
              <div className="card h-100">
                <div className="position-relative" style={{ paddingBottom: "56.25%" }}>
                  <img 
                    src={item.file_url || item.file || item.thumbnail_url || item.url || '/placeholder-image.png'} 
                    alt={item.name || item.file_name} 
                    className="card-img-top position-absolute w-100 h-100"
                    style={{ objectFit: 'cover' }}
                    onError={(e) => {
                      console.log("Image failed to load:", item);
                      // Show a placeholder or gray background on error
                      const img = e.target as HTMLImageElement;
                      img.style.display = 'none';
                      const parent = img.parentElement;
                      if (parent) {
                        parent.style.backgroundColor = '#f8f9fa';
                        parent.innerHTML = `
                          <div class="d-flex align-items-center justify-content-center h-100">
                            <div class="text-center text-muted">
                              <div style="font-size: 2rem;">📁</div>
                              <small>No Preview</small>
                            </div>
                          </div>
                        `;
                      }
                    }}
                  />
                </div>
                <div className="card-body">
                  <h6 className="card-title text-truncate" title={item.name || item.file_name}>
                    {item.name || item.file_name}
                  </h6>
                  <div className="btn-group w-100" role="group">
                    <button 
                      type="button" 
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => handlePreview(item)}
                    >
                      Preview
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary btn-sm"
                      onClick={() => handleEdit(item)}
                    >
                      Edit
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-outline-danger btn-sm"
                      onClick={() => handleDelete(item)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {uploadOpen && (
        <UploadModal 
          onClose={() => {
            setUploadOpen(false);
            // Refresh media list
            api.get("/media/").then(res => setMedia(res.data));
          }}
        />
      )}

      {/* Preview Modal */}
      {previewMedia && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Preview: {previewMedia.name}</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setPreviewMedia(null)}
                ></button>
              </div>
              <div className="modal-body text-center">
                <img 
                  src={previewMedia.file_url || previewMedia.file || previewMedia.thumbnail_url || previewMedia.url || '/placeholder-image.png'} 
                  alt={previewMedia.name}
                  className="img-fluid"
                  style={{ maxHeight: '70vh' }}
                />
                <div className="mt-3">
                  <p className="text-muted mb-1">
                    <strong>File:</strong> {previewMedia.name}
                  </p>
                  <p className="text-muted mb-1">
                    <strong>Uploaded:</strong> {new Date(previewMedia.uploaded_at).toLocaleDateString()}
                  </p>
                  {previewMedia.description && (
                    <p className="text-muted mb-1">
                      <strong>Description:</strong> {previewMedia.description}
                    </p>
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setPreviewMedia(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
