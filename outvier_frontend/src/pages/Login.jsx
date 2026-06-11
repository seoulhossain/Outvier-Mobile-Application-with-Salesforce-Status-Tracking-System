import React, { useState } from 'react';
import { HiOutlineEnvelope, HiOutlineLockClosed, HiOutlineUserCircle } from 'react-icons/hi2';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { login } from '../api';
import './Login.css';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const justRegistered = location.state?.registered;

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch {
      setError('Invalid username or password. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        {/* Avatar circle like wireframe */}
        <div className="login-avatar">
          <HiOutlineUserCircle />
        </div>
        <h1 className="login-brand">Outvier Portal</h1>
        <p className="login-sub">Sign in to your account</p>

        {justRegistered && (
          <div className="login-success">
            Account created successfully! Sign in below.
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <span className="field-icon"><HiOutlineEnvelope /></span>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Email Address"
              required
              autoFocus
            />
          </div>
          <div className="login-field">
            <span className="field-icon"><HiOutlineLockClosed /></span>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? 'Signing in…' : 'LOGIN'}
          </button>
        </form>
        <p className="login-hint">Demo: alex / alex1234  ·  admin / arka</p>
        <p className="login-register">
          New student?{' '}
          <Link to="/register" className="login-reg-link">Create an account</Link>
        </p>
      </div>
    </div>
  );
}

