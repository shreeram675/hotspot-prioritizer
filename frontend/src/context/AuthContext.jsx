import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        const token = localStorage.getItem('token');
        console.log("AuthContext: Checking auth, token:", token);
        if (token) {
            try {
                const response = await axios.get('http://localhost:8000/auth/me', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                console.log("AuthContext: User fetched:", response.data);
                setUser(response.data);
            } catch (error) {
                console.error("AuthContext: Auth check failed:", error);
                localStorage.removeItem('token');
                localStorage.removeItem('role');
                setUser(null);
            }
        } else {
            console.log("AuthContext: No token found");
            setUser(null);
        }
        setLoading(false);
    };

    const login = async (email, password) => {
        try {
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);

            const response = await axios.post('http://localhost:8000/auth/login', params);
            const { access_token, role } = response.data;

            localStorage.setItem('token', access_token);
            localStorage.setItem('role', role);

            // We await checkAuth to ensure the user state is fully updated from the server
            // before we consider the login "complete".
            await checkAuth();
            return true;
        } catch (error) {
            console.error("Login failed:", error);
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        setUser(null);
        window.location.href = '/auth/login';
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
