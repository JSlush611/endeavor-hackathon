import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import { useOrders, Order } from '../hooks/useOrders';

function StatusBadge({ status }: { status: Order['status'] }) {
  const colors = {
    processing: 'bg-blue-100 text-blue-800',
    needs_review: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status]}`}>
      {status.replace('_', ' ')}
    </span>
  );
}

export function Orders() {
  const { orders, loading, error } = useOrders();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-500 border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-error-500">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-neutral-900">Orders</h2>
        <p className="mt-1 text-sm text-neutral-500">
          View and manage all sales orders
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Orders</CardTitle>
          <CardDescription>List of all processed orders</CardDescription>
        </CardHeader>
        <CardContent>
          {orders.length === 0 ? (
            <div className="text-sm text-neutral-500">
              No orders processed yet
            </div>
          ) : (
            <div className="divide-y divide-neutral-200">
              {orders.map((order) => (
                <Link
                  key={order.id}
                  to={`/orders/${order.id}`}
                  className="block py-4 hover:bg-neutral-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-neutral-900">{order.filename}</p>
                      <p className="text-sm text-neutral-500">
                        {new Date(order.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <StatusBadge status={order.status} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 