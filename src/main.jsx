import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BasicProvider } from '@basictech/react'
import { schema } from '../basic.config'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BasicProvider project_id={schema.project_id} schema={schema}></BasicProvider>
    <App />
  </StrictMode>,
)
