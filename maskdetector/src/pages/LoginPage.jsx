import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { auth } from '../firebase';
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { Header } from './Header';
import { Footer } from './Footer';
const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";
  const [showLoginBT,setShowLoginBT] = useState(true)

  const handleGoogleLogin = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
      navigate(from, { replace: true });
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  return (
    <>
    <Header   loginBT={showLoginBT}  />
    <div className="min-h-screen flex items-center justify-center bg-gray-100 " style={{minHeight:'35vw',maxHeight:'1000px'}}>
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>
        <button
          onClick={handleGoogleLogin}
         
        >
          <img
          alt='google_signin'
           src="data:image/png;base64,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"
          />
          Sign in with Google
        </button>
      </div>
    </div>
    <Footer />
    </>
  );
};

export default LoginPage;