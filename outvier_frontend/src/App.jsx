import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import StatusDetail from './pages/StatusDetail'
import Documents from './pages/Documents'
import Notifications from './pages/Notifications'
import SyncLogs from './pages/SyncLogs'

function PrivateRoute({ children }) {
  return localStorage.getItem('access_token') ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/applications/:id" element={<PrivateRoute><StatusDetail /></PrivateRoute>} />
        <Route path="/applications/:id/documents" element={<PrivateRoute><Documents /></PrivateRoute>} />
        <Route path="/notifications" element={<PrivateRoute><Notifications /></PrivateRoute>} />
        <Route path="/admin/sync-logs" element={<PrivateRoute><SyncLogs /></PrivateRoute>} />
        <Route path="*" element={<Navigate to={localStorage.getItem('access_token') ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
