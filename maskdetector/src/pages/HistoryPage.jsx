import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../components/AuthProvider';
import { Header } from './Header';
import { Footer } from './Footer';

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = await user.getIdToken();
        // Fetch all records from /result endpoint
        const response = await fetch('http://image-processing-backend:5000/result', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success') {
            // Fetch images for each record
            const enrichedHistory = await Promise.all(
              data.records.map(async (record) => {
                try {
                  const imageResponse = await fetch(`http://image-processing-backend:5000/image/${record.id}`, {
                    headers: {
                      Authorization: `Bearer ${token}`,
                    },
                  });
                  if (imageResponse.ok) {
                    const imageData = await imageResponse.json();
                    return {
                      ...record,
                      originalImageUrl: imageData.original_image,
                      processedImageUrl: imageData.processed_image,
                    };
                  }
                  return record; // Fallback if image fetch fails
                } catch (error) {
                  console.error(`Error fetching images for record ${record.id}:`, error);
                  return record;
                }
              })
            );
            setHistory(enrichedHistory);
          } else {
            console.error('Fetch error:', data.message);
          }
        } else {
          console.error('Fetch error:', response.statusText);
        }
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchHistory();
    } else {
      setLoading(false); // Skip fetch if no user is logged in
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">Loading...</div>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gray-100 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold mb-6">Search History</h1>
          {history.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {history.map((item) => (

                <div key={item.id} className="bg-white p-4 rounded-lg shadow-md">
                  <hr/>
                  <div className="space-y-4">
                  <h3>Result - {item.id} </h3>
                  </div>
                  <div className="space-y-4">
                    {/* Original Image */}
                    {item.originalImageUrl ? (
                      <div>
                        <p className="text-sm font-semibold">Original Image</p>
                        <img style={{width:256,height:256}}
                          src={item.originalImageUrl}
                          alt="Original"
                          className="w-full h-48 object-cover rounded"
                        />
                      </div>
                    ) : (
                      <p className="text-sm text-gray-600">Original image unavailable</p>
                    )}
                    {/* Processed Image */}
                    {item.processedImageUrl ? (
                      <div>
                        <p className="text-sm font-semibold">Processed Image</p>
                        <img style={{width:256,height:256}}
                          src={item.processedImageUrl}
                          alt="Processed"
                          className="w-full h-48 object-cover rounded"
                        />
                      </div>
                    ) : (
                      <p className="text-sm text-gray-600">Processed image unavailable</p>
                    )}
                    {/* Metadata */}
                    <div className="text-sm text-gray-600">
                      <p>ID: {item.id}</p>
                      <p>Original: {item.original_filename}</p>
                      <p>Processed: {item.processed_filename}</p>
                      <p>Time: {new Date(item.time).toLocaleString()}</p>
                      <p>Status: {item.status}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No previous searches found</p>
          )}
        </div>
      </div>
      <Footer />
    </>
  );
};

export default HistoryPage;