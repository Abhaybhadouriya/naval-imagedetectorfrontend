import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth } from '../firebase';
import { signOut } from 'firebase/auth';
import { Header } from './Header';
import { Footer } from './Footer';
const DashboardPage = () => {
  const navigate = useNavigate();
  const [showLoginBT,setShowLoginBT] = useState(false)

return (
    <>
        <Header loginBT={showLoginBT} logout={auth} />
        <div className="min-h-screen bg-gray-100 p-6">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold text-center">Dashboard</h1>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 " style={{ marginTop: "20px" ,marginBottom: "20px",padding: "20px",flexDirection: "row",alignItems: "center",display: "flex",flexWrap: "wrap",justifyContent: "center"}}>
                    <div className="bg-white p-6 rounded-lg shadow-md"  style={{width: "300px", height: "100%"}}>
                        <div className="flex flex-col gap-4 items-center text-center" >
                            <div className=" items-center" style={{ justifyContent: "space-between",display: "flex",flexDirection: "column",alignItems: "center" }}>
                                <img
                                    src="https://easy-peasy.ai/cdn-cgi/image/quality=80,format=auto,width=700/https://media.easy-peasy.ai/887a3fd0-a925-447c-b03f-029e874eaefe/fa5818c3-0f08-4737-b250-d85b67f6fb86.png"
                                    alt="Upload Icon"
                                    style={{ width: "200px", height: "200px" }}
                                    className="mr-4"                                    
                                />
                                <button
                                    onClick={() => navigate("/upload")}
                                  
                                    style={{ width: "200px", height: "50px" }}
                                >
                                    Upload Image
                                </button>
                            </div>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-md"  style={{width: "300px", height: "100%"}}>
                        <div className="flex flex-col gap-4 items-center text-center">
                        <div className=" items-center" style={{ justifyContent: "space-between",display: "flex",flexDirection: "column",alignItems: "center" }}>
                        <img
                                    src="http://datasciencecentral.com/wp-content/uploads/2021/10/9652435486.jpeg"
                                    alt="History Icon"
                                    style={{ width: "200px", height: "200px" }}
                                    className="mr-4"    
                                />
                                <button
                                    onClick={() => navigate("/history")}
                                    style={{ width: "200px", height: "50px" }}
                                >
                                    View Past Results
                                </button>
                            </div>
                        </div>
                    </div>
                   
                </div>
                {/* <div className="bg-white p-6 rounded-lg shadow-md">
                        <h2 className="text-xl font-semibold mb-4">Analytics Views</h2>
                        <div className="h-64 bg-gray-200 flex items-center justify-center">
                            <p className="text-gray-500">ELK Analytics Placeholder</p>
                        </div>
                    </div> */}
            </div>
        </div>
        <Footer />
    </>
);
};

export default DashboardPage;