import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing session token in URL (callback) or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const tokenFromUrl = urlParams.get('token');

        if (tokenFromUrl) {
            localStorage.setItem('auth_token', tokenFromUrl);
            window.history.replaceState({}, document.title, window.location.pathname); // Clean URL
        }

        const token = localStorage.getItem('auth_token');
        if (token) {
            fetchCurrentUser(token);
        } else {
            setLoading(false);
        }
    }, []);

    const fetchCurrentUser = async (token) => {
        try {
            const response = await fetch('http://localhost:8000/api/auth/me?token=' + token);
            if (response.ok) {
                const data = await response.json();
                setUser(data);
            } else {
                logout();
            }
        } catch (error) {
            console.error("Auth check failed:", error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = () => {
        // Redirect to backend login endpoint
        window.location.href = 'http://localhost:8000/api/auth/login';
    };

    const logout = () => {
        localStorage.removeItem('auth_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
