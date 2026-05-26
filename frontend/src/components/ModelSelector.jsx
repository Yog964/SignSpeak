import { useRef, useState } from 'react';
import './ModelSelector.css';

function ModelSelector({ models, selectedModel, onModelChange, onModelUploaded }) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !file.name.endsWith('.pkl')) {
      alert('Please select a valid .pkl model file.');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/models/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      console.log('Upload successful:', result);
      
      // Clear the input
      if (fileInputRef.current) fileInputRef.current.value = '';
      
      // Refresh models
      if (onModelUploaded) onModelUploaded();
      
    } catch (error) {
      console.error('Error uploading model:', error);
      alert('Failed to upload model.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (e, modelId) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this model?')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/models/${modelId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        if (onModelUploaded) onModelUploaded();
      } else {
        alert('Failed to delete model');
      }
    } catch (error) {
      console.error(error);
      alert('Error deleting model');
    }
  };

  const handleEdit = async (e, modelId) => {
    e.stopPropagation();
    const newName = window.prompt('Enter new filename for this model (without .pkl):');
    if (!newName) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/models/${modelId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_name: newName }),
      });
      if (response.ok) {
        if (onModelUploaded) onModelUploaded();
      } else {
        const errorData = await response.json();
        alert(`Failed to rename model: ${errorData.detail}`);
      }
    } catch (error) {
      console.error(error);
      alert('Error renaming model');
    }
  };

  return (
    <div className="model-card" id="model-selector">
      <div className="model-header">
        <div className="card-label" style={{ marginBottom: 0 }}>Select Model</div>
        <button 
          className="btn-upload" 
          onClick={handleUploadClick}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : '+ Upload .pkl'}
        </button>
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept=".pkl"
          onChange={handleFileChange}
        />
      </div>
      <div className="model-buttons">
        {models.map((model) => {
          const isActive = selectedModel === model.id;
          return (
            <div
              key={model.id}
              className={`model-btn-container ${isActive ? 'active' : ''}`}
            >
              <button
                className={`model-btn ${isActive ? 'active' : ''}`}
                onClick={() => onModelChange(model.id)}
                id={`model-btn-${model.id}`}
                title={`Select ${model.name}`}
              >
                <span className="model-name">{model.name}</span>
                {isActive && (
                  <span className="model-actions">
                    <span 
                      className="model-action-icon edit-icon" 
                      onClick={(e) => handleEdit(e, model.id)}
                      title="Rename Model"
                    >
                      ✏️
                    </span>
                    <span 
                      className="model-action-icon delete-icon" 
                      onClick={(e) => handleDelete(e, model.id)}
                      title="Delete Model"
                    >
                      🗑️
                    </span>
                  </span>
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ModelSelector;
