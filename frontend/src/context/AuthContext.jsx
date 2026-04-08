import { createContext, useContext, useState, useCallback } from "react";
import { authApi } from "../api/auth";

const AuthContext = createContext(null);
const AUTH_STORAGE_KEY = "mbg.auth.user";

function readStoredUser() {
    if (typeof window === "undefined") {
        return null;
    }

    try {
        const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
        if (!raw) {
            return null;
        }

        const parsed = JSON.parse(raw);
        if (parsed?.user_id && parsed?.email && parsed?.role) {
            return parsed;
        }
    } catch (_) {}

    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
}

function persistUser(user) {
    if (typeof window === "undefined") {
        return;
    }

    try {
        if (user) {
            window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
            return;
        }

        window.localStorage.removeItem(AUTH_STORAGE_KEY);
    } catch (_) {}
}

export function AuthProvider({children}) {
    const [user, setUser] = useState(() => readStoredUser());
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const clearError = useCallback(() => setError(null), []);

    const login = useCallback(async (email, password) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await authApi.login(email, password);
            const nextUser = { user_id: data.user_id, email: data.email, role: data.role };
            setUser(nextUser);
            persistUser(nextUser);
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
        persistUser(null);
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
