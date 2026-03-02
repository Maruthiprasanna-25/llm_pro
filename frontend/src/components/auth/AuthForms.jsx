/**
 * Auth forms — Login and Register with glassmorphism styling.
 */
import { useState } from 'react';
import useAuthStore from '../../store/authStore';

export function LoginForm({ onSwitch }) {
    const { login, isLoading, error, clearError } = useAuthStore();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(email, password);
        } catch {
            // error is set in the store
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-5">
            <div>
                <label className="block text-sm font-medium text-white/60 mb-1.5">Email</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); clearError(); }}
                    className="input-field"
                    placeholder="you@campus.edu"
                    required
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-white/60 mb-1.5">Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); clearError(); }}
                    className="input-field"
                    placeholder="••••••••"
                    required
                />
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-red-400 text-sm">
                    {error}
                </div>
            )}

            <button type="submit" disabled={isLoading} className="w-full btn-primary">
                {isLoading ? 'Signing in...' : 'Sign In'}
            </button>

            <p className="text-center text-sm text-white/40">
                Don&apos;t have an account?{' '}
                <button type="button" onClick={onSwitch} className="text-primary-400 hover:text-primary-300 transition-colors">
                    Sign up
                </button>
            </p>
        </form>
    );
}

export function RegisterForm({ onSwitch }) {
    const { register, isLoading, error, clearError } = useAuthStore();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [localError, setLocalError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirm) {
            setLocalError('Passwords do not match');
            return;
        }
        if (password.length < 8) {
            setLocalError('Password must be at least 8 characters');
            return;
        }
        setLocalError('');
        try {
            await register(email, password);
        } catch {
            // error is set in the store
        }
    };

    const displayError = localError || error;

    return (
        <form onSubmit={handleSubmit} className="space-y-5">
            <div>
                <label className="block text-sm font-medium text-white/60 mb-1.5">Email</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); clearError(); setLocalError(''); }}
                    className="input-field"
                    placeholder="you@campus.edu"
                    required
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-white/60 mb-1.5">Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); clearError(); setLocalError(''); }}
                    className="input-field"
                    placeholder="Min 8 characters"
                    required
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-white/60 mb-1.5">Confirm Password</label>
                <input
                    type="password"
                    value={confirm}
                    onChange={(e) => { setConfirm(e.target.value); setLocalError(''); }}
                    className="input-field"
                    placeholder="••••••••"
                    required
                />
            </div>

            {displayError && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-red-400 text-sm">
                    {displayError}
                </div>
            )}

            <button type="submit" disabled={isLoading} className="w-full btn-primary">
                {isLoading ? 'Creating account...' : 'Create Account'}
            </button>

            <p className="text-center text-sm text-white/40">
                Already have an account?{' '}
                <button type="button" onClick={onSwitch} className="text-primary-400 hover:text-primary-300 transition-colors">
                    Sign in
                </button>
            </p>
        </form>
    );
}
