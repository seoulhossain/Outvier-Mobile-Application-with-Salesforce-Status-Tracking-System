import React, { useState } from 'react';
import {
  HiOutlineEnvelope,
  HiOutlineIdentification,
  HiOutlineLockClosed,
  HiOutlineUser,
  HiOutlineUserCircle,
} from 'react-icons/hi2';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api';
import './Register.css';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    student_id: '',
    password: '',
    confirm: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function change(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
    setErrors(ev => ({ ...ev, [e.target.name]: undefined, general: undefined }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    if (!form.username.trim()) errs.username = 'Username is required.';
    if (!form.email.trim()) errs.email = 'Email is required.';
    if (!form.first_name.trim()) errs.first_name = 'First name is required.';
    if (!form.last_name.trim()) errs.last_name = 'Last name is required.';
    if (form.password.length < 8) errs.password = 'Password must be at least 8 characters.';
    if (form.password !== form.confirm) errs.confirm = 'Passwords do not match.';
    if (Object.keys(errs).length) { setErrors(errs); return; }

    setLoading(true);
    try {
      const payload = {
        username: form.username.trim(),
        email: form.email.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        password: form.password,
      };
      if (form.student_id.trim()) payload.student_id = form.student_id.trim();
      await register(payload);
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      if (err && typeof err === 'object') {
        const mapped = {};
        Object.entries(err).forEach(([k, v]) => {
          mapped[k] = Array.isArray(v) ? v[0] : v;
        });
        setErrors(mapped);
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="reg-wrapper">
      <div className="reg-card">
        <div className="reg-avatar">
          <HiOutlineUserCircle />
        </div>
        <h1 className="reg-brand">Create Account</h1>
        <p className="reg-sub">Register as a new student</p>

        {errors.general && <div className="reg-error-box">{errors.general}</div>}

        <form onSubmit={handleSubmit} className="reg-form" noValidate>
          {/* Row: First + Last name */}
          <div className="reg-row">
            <div className="reg-group">
              <label>First Name</label>
              <div className={`reg-field${errors.first_name ? ' reg-field--err' : ''}`}>
                <HiOutlineUser />
                <input name="first_name" value={form.first_name} onChange={change} placeholder="First name" />
              </div>
              {errors.first_name && <span className="reg-err">{errors.first_name}</span>}
            </div>
            <div className="reg-group">
              <label>Last Name</label>
              <div className={`reg-field${errors.last_name ? ' reg-field--err' : ''}`}>
                <HiOutlineUser />
                <input name="last_name" value={form.last_name} onChange={change} placeholder="Last name" />
              </div>
              {errors.last_name && <span className="reg-err">{errors.last_name}</span>}
            </div>
          </div>

          {/* Username */}
          <div className="reg-group">
            <label>Username</label>
            <div className={`reg-field${errors.username ? ' reg-field--err' : ''}`}>
              <HiOutlineUser />
              <input name="username" value={form.username} onChange={change} placeholder="Choose a username" autoFocus />
            </div>
            {errors.username && <span className="reg-err">{errors.username}</span>}
          </div>

          {/* Email */}
          <div className="reg-group">
            <label>Email Address</label>
            <div className={`reg-field${errors.email ? ' reg-field--err' : ''}`}>
              <HiOutlineEnvelope />
              <input name="email" type="email" value={form.email} onChange={change} placeholder="your@email.com" />
            </div>
            {errors.email && <span className="reg-err">{errors.email}</span>}
          </div>

          {/* Student ID (optional) */}
          <div className="reg-group">
            <label>Student ID <span className="reg-optional">(optional)</span></label>
            <div className={`reg-field${errors.student_id ? ' reg-field--err' : ''}`}>
              <HiOutlineIdentification />
              <input name="student_id" value={form.student_id} onChange={change} placeholder="e.g. S12345678" />
            </div>
            {errors.student_id && <span className="reg-err">{errors.student_id}</span>}
          </div>

          {/* Password */}
          <div className="reg-group">
            <label>Password</label>
            <div className={`reg-field${errors.password ? ' reg-field--err' : ''}`}>
              <HiOutlineLockClosed />
              <input name="password" type="password" value={form.password} onChange={change} placeholder="Min. 8 characters" />
            </div>
            {errors.password && <span className="reg-err">{errors.password}</span>}
          </div>

          {/* Confirm Password */}
          <div className="reg-group">
            <label>Confirm Password</label>
            <div className={`reg-field${errors.confirm ? ' reg-field--err' : ''}`}>
              <HiOutlineLockClosed />
              <input name="confirm" type="password" value={form.confirm} onChange={change} placeholder="Repeat password" />
            </div>
            {errors.confirm && <span className="reg-err">{errors.confirm}</span>}
          </div>

          <button type="submit" className="btn-register" disabled={loading}>
            {loading ? 'Creating account…' : 'CREATE ACCOUNT'}
          </button>
        </form>

        <p className="reg-signin">
          Already have an account?{' '}
          <Link to="/login" className="reg-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
