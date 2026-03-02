/**
 * App.jsx — routing with auth protection.
 */
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';
import ChatPage from './pages/ChatPage';
import AuthPage from './pages/AuthPage';

function ProtectedRoute({ children }) {
    const { token } = useAuthStore();
    if (!token) return <Navigate to="/auth" replace />;
    return children;
}

export default function App() {
    const { token, fetchUser } = useAuthStore();

    useEffect(() => {
        if (token) fetchUser();
    }, [token, fetchUser]);

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/auth" element={token ? <Navigate to="/" replace /> : <AuthPage />} />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <ChatPage />
                        </ProtectedRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}
