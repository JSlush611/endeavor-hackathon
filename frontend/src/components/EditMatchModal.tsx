import { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import { Button } from './Button';
import { Card } from './Card';
import { Toast } from './Toast';
import { API_BASE_URL } from '../utils/constants';

interface Product {
  id: number;
  description: string;
  category: string;
  unit_price: number;
  material: string;
  size: string;
  length: string;
  coating: string;
  thread_type: string;
}

interface EditMatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  lineItem: {
    id: number;
    order_id: number;
    extracted_text: string;
    matched_product_id: number | null;
  };
  onUpdate: (productId: number) => Promise<void>;
}

export function EditMatchModal({ isOpen, onClose, lineItem, onUpdate }: EditMatchModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');

  useEffect(() => {
    const searchTimeout = setTimeout(async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`${API_BASE_URL}/products/search?q=${encodeURIComponent(searchQuery)}`);
        if (!response.ok) throw new Error('Failed to search products');
        const data = await response.json();
        setSearchResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    }, 300); // Debounce search by 300ms

    return () => clearTimeout(searchTimeout);
  }, [searchQuery]);

  const handleSelect = async (productId: number) => {
    try {
      await onUpdate(productId);
      setToastMessage('Product match updated successfully!');
      setToastType('success');
      setShowToast(true);
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update match');
      setToastMessage(err instanceof Error ? err.message : 'Failed to update match');
      setToastType('error');
      setShowToast(true);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-2xl w-full bg-white rounded-lg shadow-xl">
          <div className="p-6">
            <Dialog.Title className="text-lg font-medium text-neutral-900">
              Edit Product Match
            </Dialog.Title>
            
            <div className="mt-4">
              <p className="text-sm text-neutral-500">
                Current item: <span className="font-medium text-neutral-900">{lineItem.extracted_text}</span>
              </p>
            </div>

            <div className="mt-6">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search products..."
                  className="flex-1 min-w-0 block w-full px-3 py-2 text-base border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                {loading && (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
                  </div>
                )}
              </div>

              {error && (
                <p className="mt-2 text-sm text-error-500">{error}</p>
              )}

              <div className="mt-6 space-y-4 max-h-96 overflow-y-auto">
                {searchResults.map((product) => (
                  <Card 
                    key={product.id} 
                    className="group hover:bg-neutral-50 transition-colors"
                  >
                    <div className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-neutral-900">{product.description}</p>
                          <div className="mt-1 text-sm text-neutral-500 space-y-1">
                            <p>Category: {product.category}</p>
                            <p>Material: {product.material} • Size: {product.size} • Length: {product.length}</p>
                            <p>Coating: {product.coating} • Thread: {product.thread_type}</p>
                            <p>Price: ${product.unit_price.toFixed(2)}</p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => handleSelect(product.id)}
                        >
                          Select Match
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-4">
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </div>
        </Dialog.Panel>
      </div>

      {showToast && (
        <Toast
          message={toastMessage}
          type={toastType}
          onClose={() => setShowToast(false)}
        />
      )}
    </Dialog>
  );
} 