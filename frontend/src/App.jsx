import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Investigation from './pages/Investigation'
import Dossier from './pages/Dossier'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen scanline-effect">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/investigate/:id" element={<Investigation />} />
          <Route path="/dossier/:id" element={<Dossier />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}
