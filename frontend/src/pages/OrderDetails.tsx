import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import { Button } from '../components/Button';
import { useOrders, OrderDetails as IOrderDetails } from '../hooks/useOrders';
import { EditMatchModal } from '../components/EditMatchModal';
import { StatusBadge } from '../components/StatusBadge';
import { Toast } from '../components/Toast';

function ConfidenceScore({ score }: { score: number }) {
  const getColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <span className={`${getColor(score / 100)} font-medium`}>
      {score.toFixed(1)}%
    </span>
  );
}

export function OrderDetails() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { getOrderDetails, updateLineItem, exportOrder, updateOrderStatus } = useOrders();
  const [orderDetails, setOrderDetails] = useState<IOrderDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLineItem, setSelectedLineItem] = useState<IOrderDetails['line_items'][0] | null>(null);
  const [exporting, setExporting] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const details = await getOrderDetails(Number(orderId));
        setOrderDetails(details);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    if (orderId) {
      fetchDetails();
    }
  }, [orderId, getOrderDetails]);

  const handleExport = async () => {
    if (!orderId) return;
    
    try {
      setExporting(true);
      await exportOrder(Number(orderId));
      setToastMessage('Order exported successfully!');
      setToastType('success');
      setShowToast(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export order');
      setToastMessage(err instanceof Error ? err.message : 'Failed to export order');
      setToastType('error');
      setShowToast(true);
    } finally {
      setExporting(false);
    }
  };

  const handleCompleteReview = async () => {
    if (!orderId || !orderDetails) return;
    
    try {
      setUpdating(true);
      const updated = await updateOrderStatus(Number(orderId), 'completed');
      setOrderDetails(prev => prev ? { ...prev, order: updated } : null);
      setToastMessage('Order review completed successfully!');
      setToastType('success');
      setShowToast(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status');
      setToastMessage(err instanceof Error ? err.message : 'Failed to update status');
      setToastType('error');
      setShowToast(true);
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdateLineItem = async (productId: number) => {
    if (!selectedLineItem || !orderId) return;
    
    try {
      await updateLineItem(Number(orderId), selectedLineItem.id, productId);
      // Refresh order details
      const details = await getOrderDetails(Number(orderId));
      setOrderDetails(details);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update line item');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error || !orderDetails) {
    return (
      <Card variant="error">
        <CardContent className="p-6">
          <p className="text-error-500">{error || 'Order not found'}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">
            Order: {orderDetails.order.filename}
          </h2>
          <div className="mt-1 flex items-center space-x-4">
            <p className="text-sm text-neutral-500">
              Uploaded on {new Date(orderDetails.order.created_at).toLocaleDateString()}
            </p>
            <StatusBadge status={orderDetails.order.status} />
          </div>
        </div>
        <div className="flex space-x-4">
          <Button 
            variant="outline"
            onClick={() => navigate('/orders')}
          >
            Back to Orders
          </Button>
          {orderDetails.order.status === 'needs_review' && (
            <Button 
              variant="outline"
              onClick={handleCompleteReview}
              isLoading={updating}
            >
              Complete Review
            </Button>
          )}
          <Button 
            onClick={handleExport} 
            isLoading={exporting}
            variant="outline"
          >
            Export to CSV
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Line Items</CardTitle>
          <CardDescription>Review and edit matched products</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-neutral-200">
            {orderDetails.line_items.map((item) => (
              <div key={item.id} className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-neutral-900">{item.extracted_text}</p>
                    {item.matched_product_id ? (
                      <p className="mt-1 text-sm text-neutral-500">
                        Matched to: Product {item.matched_product_id}
                      </p>
                    ) : (
                      <p className="mt-1 text-sm text-neutral-500">No match selected</p>
                    )}
                  </div>
                  <div className="ml-4 flex items-center space-x-4">
                    <ConfidenceScore score={item.confidence_score} />
                    <Button size="sm" variant="outline" onClick={() => setSelectedLineItem(item)}>
                      Edit Match
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {selectedLineItem && (
        <EditMatchModal
          isOpen={!!selectedLineItem}
          onClose={() => setSelectedLineItem(null)}
          lineItem={selectedLineItem}
          onUpdate={handleUpdateLineItem}
        />
      )}

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