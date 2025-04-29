import { useEffect, useState } from 'react';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface ToastProps {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
}

export function Toast({ message, type, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, [onClose]);

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`flex items-center p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-success-50 text-success-700' : 'bg-error-50 text-error-700'
      }`}>
        {type === 'success' ? (
          <CheckCircleIcon className="h-6 w-6 mr-2" />
        ) : (
          <XCircleIcon className="h-6 w-6 mr-2" />
        )}
        <p className="font-medium">{message}</p>
      </div>
    </div>
  );
} 