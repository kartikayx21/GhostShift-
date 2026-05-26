import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

function getRiskBadge(score) {
  if (score == null) return { color: 'text-gray-500', bg: 'bg-gray-500/10', border: 'border-gray-500/20', label: '—' }
  if (score <= 40) return { color: 'text-risk-low', bg: 'bg-risk-low/10', border: 'border-risk-low/20', label: `${Math.round(score)}%` }
  if (score <= 70) return { color: 'text-risk-medium', bg: 'bg-risk-medium/10', border: 'border-risk-medium/20', label: `${Math.round(score)}%` }
  return { color: 'text-risk-high', bg: 'bg-risk-high/10', border: 'border-risk-high/20', label: `${Math.round(score)}%` }
}

export default function Home() {
  const navigate = useNavigate()
  const [brand, setBrand] = useState('')
  const [product, setProduct] = useState('')
  const [loading, setLoading] = useState(false)
  const [recentInvestigations, setRecentInvestigations] = useState([])
  const [error, setError] = useState(null)

  // Fetch recent investigations
  useEffect(() => {
    fetch('/api/investigations')
      .then((res) => res.ok ? res.json() : Promise.reject('Failed to fetch'))
      .then((data) => setRecentInvestigations(Array.isArray(data) ? data : []))
      .catch(() => setRecentInvestigations([]))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!brand.trim() || !product.trim()) return

    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand: brand.trim(), product: product.trim() }),
      })

      if (!res.ok) throw new Error('Failed to start investigation')

      const data = await res.json()
      navigate(`/investigate/${data.investigation_id}`)
    } catch (err) {
      setError(err.message || 'Something went wrong')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-start px-4 py-16 relative overflow-hidden">
      {/* Background grid effect */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(99, 102, 241, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* Floating orbs */}
      <div className="fixed top-1/4 left-1/4 w-96 h-96 bg-accent-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-1/4 right-1/4 w-80 h-80 bg-accent-secondary/5 rounded-full blur-3xl pointer-events-none" />

      {/* Logo */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        className="text-center mb-12 relative z-10"
      >
        <h1 className="text-7xl sm:text-8xl font-black tracking-tight animate-glow select-none">
          GHOST
        </h1>
        <div
          className="text-2xl sm:text-3xl font-bold tracking-[0.5em] uppercase mt-1"
          style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          SHIFT
        </div>
        <p className="text-gray-500 mt-4 text-sm font-medium tracking-wide">
          AI-Powered IP Theft Detection
        </p>
      </motion.div>

      {/* Form Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass-card p-8 w-full max-w-lg relative z-10"
      >
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="brand-name" className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Brand Name
            </label>
            <input
              id="brand-name"
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              placeholder="e.g. Nike, Apple, Dyson"
              className="glass-input w-full"
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="product-name" className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Product Name
            </label>
            <input
              id="product-name"
              type="text"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
              placeholder="e.g. Air Max 90, iPhone 15 Pro Case"
              className="glass-input w-full"
              disabled={loading}
            />
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-risk-high text-sm text-center"
            >
              {error}
            </motion.p>
          )}

          <button
            type="submit"
            disabled={loading || !brand.trim() || !product.trim()}
            className="btn-primary w-full flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <motion.div
                  className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                <span>Initializing agents...</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Start Investigation</span>
              </>
            )}
          </button>
        </form>
      </motion.div>

      {/* Recent Investigations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="w-full max-w-lg mt-10 relative z-10"
      >
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Recent Investigations
        </h2>

        {recentInvestigations.length === 0 ? (
          <div className="glass-card p-6 text-center">
            <p className="text-gray-600 text-sm">No investigations yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {recentInvestigations.map((inv, i) => {
              const badge = getRiskBadge(inv.risk_score)
              const isComplete = inv.status === 'complete' || inv.status === 'completed'
              const targetPath = isComplete ? `/dossier/${inv.id}` : `/investigate/${inv.id}`

              return (
                <motion.div
                  key={inv.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.05 }}
                  onClick={() => navigate(targetPath)}
                  className="glass-card p-4 flex items-center justify-between cursor-pointer hover:border-white/10 transition-all duration-300 group"
                >
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-white group-hover:text-accent-glow transition-colors truncate">
                      {inv.brand} — {inv.product}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5 capitalize">{inv.status || 'unknown'}</p>
                  </div>

                  {inv.risk_score != null && (
                    <span className={`status-badge ${badge.bg} ${badge.color} border ${badge.border}`}>
                      {badge.label}
                    </span>
                  )}

                  <svg className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors ml-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </motion.div>
              )
            })}
          </div>
        )}
      </motion.div>
    </div>
  )
}
