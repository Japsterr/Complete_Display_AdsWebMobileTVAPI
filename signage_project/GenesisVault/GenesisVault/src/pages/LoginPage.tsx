import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Form, Button, Alert } from 'react-bootstrap';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleLogin = async () => {
  // TEMP: Bypass authentication for dashboard preview
  navigate('/dashboard');
  };

  return (
    <Container className="d-flex flex-column align-items-center justify-content-center" style={{ minHeight: '100vh', background: '#23272f' }}>
      <Form style={{ width: 350, background: '#2d323b', padding: 32, borderRadius: 16, boxShadow: '0 0 16px #ff9900', border: '2px solid #ff9900' }}>
        <h2 className="mb-4 text-center" style={{ color: '#ff9900', fontWeight: 'bold' }}>GenesisVault Login</h2>
        {error && <Alert variant="warning">{error}</Alert>}
        <Form.Group className="mb-3">
          <Form.Label style={{ color: '#ff9900', fontWeight: 'bold' }}>Email</Form.Label>
          <Form.Control type="email" value={email} onChange={e => setEmail(e.target.value)} style={{ background: '#3a3f4b', color: '#fff', borderColor: '#ff9900' }} />
        </Form.Group>
        <Form.Group className="mb-4">
          <Form.Label style={{ color: '#ff9900', fontWeight: 'bold' }}>Password</Form.Label>
          <Form.Control type="password" value={password} onChange={e => setPassword(e.target.value)} style={{ background: '#3a3f4b', color: '#fff', borderColor: '#ff9900' }} />
        </Form.Group>
        <Button variant="warning" className="w-100" style={{ fontWeight: 'bold', fontSize: '1.2rem', boxShadow: '0 0 8px #ff9900' }} onClick={handleLogin}>Login</Button>
      </Form>
    </Container>
  );
};

export default LoginPage;
