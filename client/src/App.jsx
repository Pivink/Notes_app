import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Signup from './components/Signup';
import NotesList from './components/NotesList';
import NoteForm from './components/NoteForm';
import SharedNote from './components/SharedNote';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
}

function PublicRoute({ children }) {
  const token = localStorage.getItem('token');
  return !token ? children : <Navigate to="/" />;
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/signup" element={
            <PublicRoute>
              <Signup />
            </PublicRoute>
          } />
          <Route path="/" element={
            <ProtectedRoute>
              <NotesList />
            </ProtectedRoute>
          } />
          <Route path="/notes/new" element={
            <ProtectedRoute>
              <NoteForm />
            </ProtectedRoute>
          } />
          <Route path="/notes/:id/edit" element={
            <ProtectedRoute>
              <NoteForm />
            </ProtectedRoute>
          } />
          <Route path="/shared/:token" element={<SharedNote />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;