import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState(null);

    useEffect(() => {
        // Check for stored token/user on mount
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');
        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
            // Set default authorization header
            api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            // Use URLSearchParams for OAuth2PasswordRequestForm
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);

            const response = await api.post('/auth/login', params, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': undefined
                },
            });

            const { access_token } = response.data;

            // Store token
            setToken(access_token);
            localStorage.setItem('token', access_token);

            // Set default authorization header
            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

            // Fetch user details from /auth/me
            const meResponse = await api.get('/auth/me');
            const userInfo = meResponse.data;

            setUser(userInfo);
            localStorage.setItem('user', JSON.stringify(userInfo));

            return userInfo;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const signup = async (name, email, password, role) => {
        try {
            const response = await api.post('/auth/register', {
                name,
                email,
                password,
                role
            });

            // After signup, automatically login
            return await login(email, password);
        } catch (error) {
            console.error('Signup failed:', error);
            throw error;
        }
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
    };

    const value = {
        user,
        token,
        login,
        signup,
        logout,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
