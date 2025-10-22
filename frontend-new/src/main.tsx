import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/index.css'
import './styles/mobile.css'
import { ThemeProvider } from './contexts/ThemeContext'
import ToastContainer from './components/ToastContainer'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
      <ToastContainer />
    </ThemeProvider>
  </React.StrictMode>,
)

