import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import RiskGauge from '../components/RiskGauge'
import EvidenceCard from '../components/EvidenceCard'

const ACTION_COLORS = {
  'Report': { color: '#ef4444', bg: 'bg-risk-high/10', border: 'border-risk-high/20', text: 'text-risk-high' },
  'Investigate Further': { color: '#f59e0b', bg: 'bg-risk-medium/10', border: 'border-risk-medium/20', text: 'text-risk-medium' },
  'Low Risk': { color: '#22c55e', bg: 'bg-risk-low/10', border: 'border-risk-low/20', text: 'text-risk-low' },
}

export default function Dossier() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchResults() {
      try {
        const [resultsRes, statusRes] = await Promise.all([
          fetch(`/api/investigate/${id}/results`),
          fetch(`/api/investigate/${id}/status`),
        ])

        if (!resultsRes.ok) throw new Error('Investigation not found or not yet complete')

        const results = await resultsRes.json()
        const status = statusRes.ok ? await statusRes.json() : {}

        setData({
          ...results,
          brand: results.brand || status.brand || 'Unknown',
          product: results.product || status.product || 'Unknown',
        })
      } catch (err) {
        setError(err.message || 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="w-16 h-16 border-4 border-accent-primary/20 border-t-accent-primary rounded-full mx-auto mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          <p className="text-gray-400 font-medium">Loading evidence dossier...</p>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-8 text-center max-w-md"
        >
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-white mb-2">Investigation Not Found</h2>
          <p className="text-gray-400 text-sm mb-6">{error}</p>
          <Link to="/" className="btn-primary inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </motion.div>
      </div>
    )
  }

  const riskScore = data?.risk_score ?? 0
  const verdict = data?.verdict || 'No verdict available'
  const recommendedAction = data?.recommended_action || 'Low Risk'
  const evidence = data?.evidence || []
  const actionConfig = ACTION_COLORS[recommendedAction] || ACTION_COLORS['Low Risk']

  return (
    <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </Link>

        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="text-3xl sm:text-4xl font-bold text-white">Evidence Dossier</h1>
          <span className="status-badge bg-accent-primary/10 text-accent-glow border border-accent-primary/20">
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Verified
          </span>
        </div>
        <p className="text-gray-500 text-sm mt-1 font-mono">
          {data.brand} — {data.product}
        </p>
      </motion.div>

      {/* Risk Gauge Section */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="flex flex-col items-center mb-10"
      >
        <RiskGauge score={riskScore} />
      </motion.div>

      {/* Verdict */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-6 mb-8 text-center max-w-3xl mx-auto"
      >
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Verdict</h2>
        <p className="text-lg sm:text-xl font-medium text-gray-200 leading-relaxed">{verdict}</p>

        <div className="mt-4">
          <span
            className={`status-badge ${actionConfig.bg} ${actionConfig.text} border ${actionConfig.border} text-sm`}
          >
            {recommendedAction}
          </span>
        </div>
      </motion.div>

      {/* Evidence Grid */}
      {evidence.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="mb-10"
        >
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Evidence ({evidence.length} items)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {evidence.map((item, i) => (
              <EvidenceCard key={i} evidence={item} index={i} />
            ))}
          </div>
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="flex flex-col sm:flex-row items-center justify-center gap-4 pb-12"
      >
        <button
          onClick={() => alert('PDF report generation is a premium feature. Coming soon!')}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-dark-700 border border-white/10 text-gray-300 hover:text-white hover:border-white/20 transition-all duration-300 font-medium text-sm"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download PDF Report
        </button>

        <Link
          to="/"
          className="btn-primary inline-flex items-center gap-2 text-sm"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New Investigation
        </Link>
      </motion.div>
    </div>
  )
}
