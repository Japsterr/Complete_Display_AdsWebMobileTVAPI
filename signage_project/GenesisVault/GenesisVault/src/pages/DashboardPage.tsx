import React, { useEffect, useState } from 'react';
import { Container } from 'react-bootstrap';

const DashboardPage = () => {
  const [userInfo, setUserInfo] = useState<any>(null);

  useEffect(() => {
    // Try to get token from localStorage
    const token = localStorage.getItem('keygen_token');
    if (!token) return;
    // Fetch user info from Keygen API
    fetch('https://keygen.genesiscloud.co.za/v1/accounts/mrjc-co-za/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.api+json',
      },
    })
      .then(res => res.json())
      .then(data => setUserInfo(data.data?.attributes || null));
  }, []);

  return (
    <Container className="pt-5">
      <h2 style={{ color: '#ff9900', fontWeight: 'bold' }}>Dashboard</h2>
      <div style={{ color: '#fff', background: '#2d323b', padding: 24, borderRadius: 12, marginTop: 24 }}>
        <p>Welcome to GenesisVault!</p>
        {userInfo ? (
          <div style={{ marginTop: 24, padding: 16, background: '#3a3f47', borderRadius: 8 }}>
            <h5 style={{ color: '#ff9900' }}>User Info</h5>
            <p>Email: {userInfo.email}</p>
            <p>Name: {userInfo.name || 'N/A'}</p>
            <p>Role: {userInfo.role || 'N/A'}</p>
            <p>ID: {userInfo.id}</p>
          </div>
        ) : (
          <p style={{ color: '#ff9900' }}>No user info available. Please log in.</p>
        )}
      </div>
      <div className="row mt-4">
        <div className="col-md-6">
          <div style={{ background: '#3a3f47', padding: 16, borderRadius: 8 }}>
            <h5 style={{ color: '#ff9900' }}>License Keys</h5>
            <p>(Placeholder for license key list)</p>
          </div>
        </div>
        <div className="col-md-6">
          <div style={{ background: '#3a3f47', padding: 16, borderRadius: 8 }}>
            <h5 style={{ color: '#ff9900' }}>License Status</h5>
            <p>(Placeholder for license status)</p>
          </div>
        </div>
        <div className="col-md-6">
          <div style={{ background: '#3a3f47', padding: 16, borderRadius: 8 }}>
            <h5 style={{ color: '#ff9900' }}>Machines</h5>
            <p>(Placeholder for machine/device list)</p>
          </div>
        </div>
        <div className="col-md-6">
          <div style={{ background: '#3a3f47', padding: 16, borderRadius: 8 }}>
            <h5 style={{ color: '#ff9900' }}>User Profile</h5>
            <p>(Placeholder for user profile/settings)</p>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default DashboardPage;
