import { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../utils/constants';

export interface LineItem {
  id: number;
  order_id: number;
  extracted_text: string;
  matched_product_id: number | null;
  confidence_score: number;
}

export interface Order {
  id: number;
  filename: string;
  status: 'processing' | 'needs_review' | 'completed' | 'error';
  created_at: string;
  updated_at: string;
}

export interface OrderDetails {
  order: Order;
  line_items: LineItem[];
}

export function useOrders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/orders`);
      if (!response.ok) throw new Error('Failed to fetch orders');
      const data = await response.json();
      setOrders(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const getOrderDetails = useCallback(async (orderId: number): Promise<OrderDetails> => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`);
    if (!response.ok) throw new Error('Failed to fetch order details');
    return response.json();
  }, []);

  const updateLineItem = useCallback(async (orderId: number, itemId: number, productId: number) => {
    const response = await fetch(
      `${API_BASE_URL}/orders/${orderId}/line-items/${itemId}?product_id=${productId}`,
      {
        method: 'POST',
      }
    );
    if (!response.ok) throw new Error('Failed to update line item');
    return response.json();
  }, []);

  const exportOrder = useCallback(async (orderId: number) => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/export`);
    if (!response.ok) throw new Error('Failed to export order');
    
    // Get the filename from the Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    const filenameMatch = contentDisposition?.match(/filename=(.+)/);
    const filename = filenameMatch ? filenameMatch[1] : 'order.csv';
    
    // Create a blob from the response and download it
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }, []);

  const updateOrderStatus = useCallback(async (orderId: number, status: Order['status']) => {
    const response = await fetch(
      `${API_BASE_URL}/orders/${orderId}/status`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      }
    );
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Status update error:', errorData);
      throw new Error(errorData.detail || 'Failed to update order status');
    }
    const updatedOrder = await response.json();
    // Update orders list
    setOrders(orders => orders.map(order => 
      order.id === orderId ? updatedOrder : order
    ));
    return updatedOrder;
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return {
    orders,
    loading,
    error,
    fetchOrders,
    getOrderDetails,
    updateLineItem,
    exportOrder,
    updateOrderStatus,
  };
} 