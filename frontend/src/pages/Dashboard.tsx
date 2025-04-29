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

export function Dashboard() {
  const { orders, loading, error } = useOrders();

  const stats = {
    total: orders.length,
    pending: orders.filter(o => o.status === 'needs_review').length,
    processing: orders.filter(o => o.status === 'processing').length,
    completed: orders.filter(o => o.status === 'completed').length,
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <Card variant="error">
        <CardContent className="p-6">
          <p className="text-error-500">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-neutral-900">Dashboard</h2>
        <p className="mt-1 text-sm text-neutral-500">
          Overview of your sales order processing
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Orders</CardTitle>
            <CardDescription>All time</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.total}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending Review</CardTitle>
            <CardDescription>Orders needing attention</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.pending}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processing</CardTitle>
            <CardDescription>Currently processing</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.processing}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Completed</CardTitle>
            <CardDescription>Successfully processed</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.completed}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Orders</CardTitle>
          <CardDescription>Your latest processed orders</CardDescription>
        </CardHeader>
        <CardContent>
          {orders.length === 0 ? (
            <div className="text-sm text-neutral-500">
              No orders processed yet
            </div>
          ) : (
            <div className="divide-y divide-neutral-200">
              {orders.slice(0, 5).map((order) => (
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