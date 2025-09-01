import { Link, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav className="bg-blue-600 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">Notes App</Link>
        
        {token ? (
          <div className="flex items-center space-x-4">
            <Link to="/" className="hover:text-blue-200">My Notes</Link>
            <Link to="/notes/new" className="hover:text-blue-200">Add Note</Link>
            <button 
              onClick={handleLogout}
              className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-4">
            <Link to="/login" className="hover:text-blue-200">Login</Link>
            <Link to="/signup" className="hover:text-blue-200">Signup</Link>
          </div>
        )}
      </div>
    </nav>
  );
}