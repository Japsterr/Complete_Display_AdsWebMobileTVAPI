import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './custom.css'
import App from './App'
import { ChakraProvider } from '@chakra-ui/react'
import { theme } from './theme'

// theme imported from ./theme

createRoot(document.getElementById('root')!).render(
  <StrictMode>
  <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </StrictMode>,
)
