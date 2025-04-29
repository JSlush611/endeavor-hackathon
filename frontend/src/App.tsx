import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { OrderDetails } from './pages/OrderDetails';
import { Orders } from './pages/Orders';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/orders/:orderId" element={<OrderDetails />} />
          <Route path="/orders" element={<Orders />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
