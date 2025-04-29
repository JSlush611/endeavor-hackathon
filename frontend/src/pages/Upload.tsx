import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import { Button } from '../components/Button';
import { Toast } from '../components/Toast';
import { API_BASE_URL } from '../utils/constants';

export function Upload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    try {
      setUploading(true);
      setProgress(0);
      
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setProgress(percentComplete);
        }
      });

      xhr.open('POST', `${API_BASE_URL}/upload`);
      xhr.send(formData);

      xhr.onload = () => {
        if (xhr.status === 200) {
          setToastMessage('File uploaded successfully!');
          setToastType('success');
          setShowToast(true);
        } else {
          throw new Error('Upload failed');
        }
      };

      xhr.onerror = () => {
        throw new Error('Upload failed');
      };
    } catch (error) {
      setToastMessage(error instanceof Error ? error.message : 'Upload failed');
      setToastType('error');
      setShowToast(true);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-neutral-900">Upload Order</h2>
        <p className="mt-1 text-sm text-neutral-500">
          Upload a PDF file to process a new sales order
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
          <CardDescription>Drag and drop your PDF file here or click to browse</CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-primary-500 bg-primary-50' : 'border-neutral-300 hover:border-primary-500'
            }`}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <div className="space-y-4">
                <div className="w-full bg-neutral-200 rounded-full h-2.5">
                  <div
                    className="bg-primary-500 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-neutral-500">Uploading... {Math.round(progress)}%</p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-neutral-500">
                  {isDragActive ? 'Drop the file here' : 'Drag and drop your PDF file here'}
                </p>
                <p className="text-xs text-neutral-400">or click to browse</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {showToast && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setShowToast(false)}
        />
      )}
    </div>
  );
} 