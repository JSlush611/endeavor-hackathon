import { Order } from '../hooks/useOrders';

interface StatusBadgeProps {
  status: Order['status'];
}

export function StatusBadge({ status }: StatusBadgeProps) {
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