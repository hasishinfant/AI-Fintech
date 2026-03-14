import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../services/api';

interface UploadPanelProps {
  applicationId: string;
  onUploadComplete?: () => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ 
  applicationId, 
  onUploadComplete 
}) => {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });
      return await apiClient.post(`/applications/${applicationId}/documents`, formData);
    },
    onSuccess: () => {
      setSelectedFiles(null);
      onUploadComplete?.();
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(e.target.files);
  };

  const handleUpload = () => {
    if (selectedFiles) {
      uploadMutation.mutate(selectedFiles);
    }
  };

  return (
    <div className="bg-white p-6 rounded shadow">
      <h3 className="font-bold text-lg mb-4">Upload Documents</h3>
      <div className="space-y-4">
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
        {selectedFiles && (
          <div className="text-sm text-gray-600">
            {selectedFiles.length} file(s) selected
          </div>
        )}
        <button
          onClick={handleUpload}
          disabled={!selectedFiles || uploadMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
        </button>
      </div>
    </div>
  );
};
