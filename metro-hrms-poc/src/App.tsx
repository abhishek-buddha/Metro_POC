// Main App component with routing
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import EmployeeList from './pages/EmployeeList';
import EmployeeForm from './pages/EmployeeForm';
import './App.css';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<EmployeeList />} />
          <Route path="/employee/:id/form" element={<EmployeeForm />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
