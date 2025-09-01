import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import API from '../api';

export default function SharedNote() {
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useParams();

  useEffect(() => {
    fetchSharedNote();
  }, [token]);

  const fetchSharedNote = async () => {
    try {
      const response = await API.get(`/shared/${token}`);
      setNote(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load shared note');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="container mx-auto p-6">Loading...</div>;
  if (error) return <div className="container mx-auto p-6 text-red-600">{error}</div>;
  if (!note) return <div className="container mx-auto p-6">Note not found</div>;

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">{note.title}</h1>
        
        {note.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            {note.tags.map(tag => (
              <span key={tag} className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
                #{tag}
              </span>
            ))}
          </div>
        )}
        
        <div className="prose max-w-none mb-6">
          <pre className="whitespace-pre-wrap font-sans">{note.content}</pre>
        </div>
        
        <div className="text-sm text-gray-500 border-t pt-4">
          Last updated: {new Date(note.updatedAt).toLocaleString()}
        </div>
      </div>
    </div>
  );
}