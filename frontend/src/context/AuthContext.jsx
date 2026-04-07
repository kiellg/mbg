import { createContext, useContext, useState, useCallback } from "react";
import { authApi } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({children}) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const clearError = useCallback(() => setError(null), []);

    const login = useCallback(async (ElementInternals, password) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await authApi.login(email, password);
            setUser({ user_id: data.user_id, email: data.email, role: data.role });
            return { success: true, message: data.message };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Login failed';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const register = useCallback(async (name, email, password, role) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await authApi.register(name, email, password, role);
            return { success: true, data };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Registration failed';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            await authApi.logout();
        } catch (_) {}
        setUser(null);
    }, []);

    const forgotPassword = useCallback(async (email) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await authApi.forgotPassword(email);
            return { success: true, reset_token: data.reset_token };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Request failed';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    const resetPassword = useCallback(async (token, new_password) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await authApi.resetPassword(token, new_password);
            return { success: true, message: data.message };
        } catch (err) {
            const msg = err.response?.data?.detail || 'Reset failed';
            setError(msg);
            return { success: false, message: msg };
        } finally {
            setLoading(false);
        }
    }, []);

    return (
        <AuthContext.Provider
            value={{user, loading, error, clearError, login, register, logout, forgotPassword, resetPassword }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
    return ctx;
};