import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import { Box, Button, Container, Heading, Input, Text, VStack, HStack } from "@chakra-ui/react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  // no toast in this minimal setup

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      // Try the SimpleJWT endpoint first for testing
      const res = await api.post("/login-simple/", { email, password });
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      navigate("/dashboard");
    } catch (err: any) {
      console.error("Login error:", err);
  const msg = err.response?.data?.detail || "Invalid credentials. Please try again.";
      setError(msg);
  // could add toast here if needed
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box minH="100vh" bg="#1a1b1e" display="flex" alignItems="center" py={16}>
      <Container maxW="lg">
        <VStack spacing={8} align="stretch">
          <VStack spacing={2} textAlign="center">
            <Box fontSize="5xl">📱</Box>
            <Heading size="lg" color="brand.500">Welcome back</Heading>
            <Text color="gray.400">Sign in to manage your digital signage campaigns</Text>
          </VStack>

          <Box
            bg="#222325"
            p={8}
            borderRadius="2xl"
            boxShadow="0 0 0 1px rgba(255,107,53,0.25), 0 10px 40px rgba(0,0,0,0.4)"
          >
            {error && (
              <Box bg="red.900" color="red.200" borderRadius="md" p={3} mb={4}>
                <strong>Sign In Failed:</strong> {error}
              </Box>
            )}

      <VStack as="form" onSubmit={handleSubmit} spacing={5} align="stretch">
        <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  value={email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                  borderColor="rgba(255,107,53,0.35)"
                  _hover={{ borderColor: 'brand.500' }}
                  _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 3px rgba(255,107,53,0.15)' }}
                  bg="#1c1d20"
                />
              
        <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                  borderColor="rgba(255,107,53,0.35)"
                  _hover={{ borderColor: 'brand.500' }}
                  _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 3px rgba(255,107,53,0.15)' }}
                  bg="#1c1d20"
                />

              <Button type="submit" isLoading={loading} size="lg" colorScheme="orange">
                🚀 Sign In
              </Button>
            </VStack>

      <Box h="1px" bg="rgba(255,107,53,0.2)" my={6} />
            <HStack justify="space-between" color="gray.400" fontSize="sm">
              <HStack spacing={6}>
                <Text>🔒 Secure login</Text>
                <Text>🌍 Access anywhere</Text>
                <Text>📱 Mobile ready</Text>
              </HStack>
              <Text>
                Don't have an account?{' '}
                <Box as={Link} to="/register" color="brand.400" _hover={{ color: 'brand.300', textDecoration: 'underline' }}>
                  Create one
                </Box>
              </Text>
            </HStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
}