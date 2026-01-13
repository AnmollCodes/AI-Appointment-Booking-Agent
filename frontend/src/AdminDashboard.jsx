import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Trash2, RefreshCw, User, Clipboard, Clock } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export default function AdminDashboard({ onClose }) {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAppointments = async () => {
        setLoading(true);
        try {
            // We need a new endpoint for this, or use specific logic
            // For demo, let's assume we can fetch all or just use a mock if backend isn't ready
            // But I'll add the endpoint to backend/main.py next
            const res = await axios.get(`${API_URL}/admin/appointments`);
            setAppointments(res.data);
        } catch (e) {
            console.error("Failed to fetch", e);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchAppointments();
        const interval = setInterval(fetchAppointments, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleCancel = async (id) => {
        if (!confirm("Cancel this appointment?")) return;
        try {
            await axios.post(`${API_URL}/admin/cancel`, { id });
            fetchAppointments();
        } catch (e) {
            alert("Error cancelling");
        }
    }

    return (
        <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            style={{
                position: 'absolute',
                inset: 0,
                zIndex: 20,
                background: 'rgba(5, 5, 5, 0.95)',
                backdropFilter: 'blur(20px)',
                padding: '40px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
                color: 'white'
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, background: 'linear-gradient(to right, #6366f1, #ec4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Aura Dashboard
                </h2>
                <button
                    onClick={onClose}
                    style={{ background: 'transparent', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '10px 20px', borderRadius: '8px' }}
                >
                    Close
                </button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 10px' }}>
                    <thead>
                        <tr style={{ color: 'rgba(255,255,255,0.5)', textAlign: 'left' }}>
                            <th style={{ padding: '10px' }}>Client</th>
                            <th>Service</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && appointments.length === 0 && (
                            <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>Loading...</td></tr>
                        )}
                        {appointments.map(appt => (
                            <motion.tr
                                key={appt.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                style={{ background: 'rgba(255,255,255,0.05)' }}
                            >
                                <td style={{ padding: '15px', borderRadius: '10px 0 0 10px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <div style={{ background: '#6366f1', padding: '8px', borderRadius: '50%' }}><User size={16} /></div>
                                        <div>
                                            <div style={{ fontWeight: 'bold' }}>{appt.name}</div>
                                            <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>{appt.contact}</div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Clipboard size={14} opacity={0.7} />
                                        {appt.service}
                                    </div>
                                </td>
                                <td>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Clock size={14} opacity={0.7} />
                                        {new Date(appt.start_iso).toLocaleString()}
                                    </div>
                                </td>
                                <td>
                                    <span style={{
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        background: appt.status === 'booked' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                        color: appt.status === 'booked' ? '#34d399' : '#f87171',
                                        fontSize: '0.85rem'
                                    }}>
                                        {appt.status.toUpperCase()}
                                    </span>
                                </td>
                                <td style={{ borderRadius: '0 10px 10px 0' }}>
                                    {appt.status === 'booked' && (
                                        <button
                                            onClick={() => handleCancel(appt.id)}
                                            style={{ color: '#f87171', background: 'transparent', border: 'none', padding: '8px' }}
                                            title="Cancel Appointment"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    )}
                                </td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </motion.div>
    )
}
