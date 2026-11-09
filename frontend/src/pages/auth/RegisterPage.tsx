import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Layers, User as UserIcon, Mail, Lock, ArrowRight, Loader2, AlertCircle, Briefcase, Building2, CheckCircle2 } from 'lucide-react';
import { AuthFormField } from '../../components/auth/AuthFormField';
import { useAuth } from '../../context/AuthContext';
import { loginUser, registerUser } from '../../lib/api';
import { AccountType } from '../../types/auth';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [accountType, setAccountType] = useState<AccountType>('freelancer');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Front-end validations
    if (fullName.trim().length < 2) {
      setErrorMessage('Full name must be at least 2 characters long.');
      return;
    }

    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
      setErrorMessage('Password must contain at least one letter and one number.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Password and confirmation password do not match.');
      return;
    }

    setIsLoading(true);
    try {
      // 1. Register account
      await registerUser({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        confirm_password: confirmPassword,
        account_type: accountType,
      });

      // 2. Automatically log in user
      const loginResp = await loginUser({
        email: email.trim(),
        password,
      });
      login(loginResp.access_token, loginResp.user);

      // 3. Navigate to dashboard
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Registration failed. Please check your information.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative selection:bg-blue-600 selection:text-white bg-grid-pattern">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[400px] bg-gradient-to-tr from-blue-600/10 via-indigo-500/10 to-violet-600/10 blur-[120px] pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4">
        {/* Brand Header */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-violet-600 p-0.5 shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Layers className="w-5 h-5 text-blue-400" />
              </div>
            </div>
            <span className="text-2xl font-bold tracking-tight text-white">
              MilestonePay <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">AI</span>
            </span>
          </Link>
          <h2 className="mt-6 text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-blue-400 hover:text-blue-300 transition-colors">
              Sign in
            </Link>
          </p>
        </div>

        {/* Card */}
        <div className="mt-8 bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-2xl space-y-6">
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-900/60 flex items-start gap-3 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Account Type Selector */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                I want to join as a:
              </label>
              <div className="grid grid-cols-2 gap-3 pt-1">
                <button
                  type="button"
                  onClick={() => setAccountType('freelancer')}
                  className={`p-3.5 rounded-2xl border text-left flex flex-col justify-between transition-all ${
                    accountType === 'freelancer'
                      ? 'bg-blue-600/15 border-blue-500 text-white shadow-md shadow-blue-500/10'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <Briefcase className={`w-5 h-5 ${accountType === 'freelancer' ? 'text-blue-400' : 'text-slate-500'}`} />
                    {accountType === 'freelancer' && <CheckCircle2 className="w-4 h-4 text-blue-400" />}
                  </div>
                  <span className="text-sm font-semibold text-white">Freelancer</span>
                  <span className="text-[11px] text-slate-400 mt-0.5">Deliver work & receive milestone payments</span>
                </button>

                <button
                  type="button"
                  onClick={() => setAccountType('client')}
                  className={`p-3.5 rounded-2xl border text-left flex flex-col justify-between transition-all ${
                    accountType === 'client'
                      ? 'bg-indigo-600/15 border-indigo-500 text-white shadow-md shadow-indigo-500/10'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <Building2 className={`w-5 h-5 ${accountType === 'client' ? 'text-indigo-400' : 'text-slate-500'}`} />
                    {accountType === 'client' && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
                  </div>
                  <span className="text-sm font-semibold text-white">Client</span>
                  <span className="text-[11px] text-slate-400 mt-0.5">Post projects, review milestones & release funds</span>
                </button>
              </div>
            </div>

            <AuthFormField
              id="fullName"
              type="text"
              label="Full Name"
              icon={UserIcon}
              placeholder="e.g. Alex Mercer"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />

            <AuthFormField
              id="email"
              type="email"
              label="Email Address"
              icon={Mail}
              placeholder="you@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <AuthFormField
              id="password"
              type="password"
              label="Password"
              icon={Lock}
              placeholder="At least 8 characters (letters + numbers)"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <AuthFormField
              id="confirmPassword"
              type="password"
              label="Confirm Password"
              icon={Lock}
              placeholder="Re-type your password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-3 px-4 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 shadow-lg shadow-blue-600/25 transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
            <Link to="/" className="hover:text-slate-300 transition-colors">
              ← Return to Home
            </Link>
            <span className="capitalize">{accountType} Account</span>
          </div>
        </div>
      </div>
    </div>
  );
};

