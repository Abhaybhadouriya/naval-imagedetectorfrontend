import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { auth } from '../firebase';
import { Header } from './Header';
import { Footer } from './Footer';
const ResultPage = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const { state } = useLocation(); // Get navigation state
  const [showLoginBT,setShowLoginBT] = useState(false)

  useEffect(() => {
    // Set result from navigation state
    if (state && state.resultImage) {
      setResult({
        resultImage1: state.resultImage, // Base64 image from Flask
        filename: state.filename || 'Predicted Mask',
      });
    }
    setLoading(false);
  }, [state]);

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
      <>
            <Header loginBT={showLoginBT} logout={auth} />
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Analysis Result</h1>
        {result ? (
          <div className="space-y-6">
            <p className="text-lg">Predicted Mask: {result.filename}</p>
            {result.resultImage1 && (
              <img style={{width:256,height:256}}
                src={result.resultImage1}
                alt="Predicted Mask"
                className="w-full rounded-lg max-w-md"
              />
            )}
          </div>
        ) : (
          <p>No results found. Please upload an image.</p>
        )}
      </div>
    </div>
         <Footer />
        </>
  );
};

export default ResultPage;