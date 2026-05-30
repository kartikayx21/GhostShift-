import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function GhostShiftReport({ brand, product }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchProbability() {
      try {
        const res = await fetch(`${API_BASE}/api/forensics/probability`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ brand, product }),
        })
        const result = await res.json()
        setData(result)
      } catch (err) {
        console.error('Failed to load probability:', err)
      } finally {
        setLoading(false)
      }
    }
    if (brand && product) fetchProbability()
  }, [brand, product])

  if (loading || !data) return null

  const { probability, alert } = data
  const prob = probability?.probability || 0
  const probPct = Math.round(prob * 100)
  const breakdown = probability?.breakdown || {}
  const weights = probability?.weights || {}
  const verdict = probability?.verdict || 'MONITORING'

  const signalLabels = {
    listingData: 'Marketplace Intel',
    factoryIntel: 'Factory Intel',
    componentTrace: 'Supply Chain',
    listingForensics: 'Forensics',
    pricingAnomaly: 'Pricing',
  }

  const verdictColors = {
    'HIGH RISK': { text: 'text-risk-high', bg: 'bg-risk-high', glow: 'shadow-risk-high/30' },
    'SUSPICIOUS': { text: 'text-risk-medium', bg: 'bg-risk-medium', glow: 'shadow-risk-medium/30' },
    'MONITORING': { text: 'text-risk-low', bg: 'bg-risk-low', glow: 'shadow-risk-low/30' },
  }

  const vc = verdictColors[verdict] || verdictColors['MONITORING']

  return (
    <div className="glass-card p-6">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
        <span>🎯</span> Ghost Shift Probability Model
      </h3>

      {/* Main probability display */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          {/* Circular gauge */}
          <svg width="160" height="160" viewBox="0 0 160 160">
            {/* Background track */}
            <circle cx="80" cy="80" r="65" fill="none" stroke="#1a1a1a" strokeWidth="12" />
            {/* Progress arc */}
            <circle
              cx="80" cy="80" r="65" fill="none"
              stroke={prob > 0.7 ? '#ef4444' : prob > 0.4 ? '#f59e0b' : '#22c55e'}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${prob * 408} 408`}
              transform="rotate(-90 80 80)"
              style={{ transition: 'stroke-dasharray 1.5s ease-out' }}
            />
          </svg>
          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.span
              className={`text-3xl font-black ${vc.text}`}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, type: 'spring' }}
            >
              {probPct}%
            </motion.span>
            <span className="text-[10px] text-gray-500 uppercase tracking-wider">Probability</span>
          </div>
        </div>

        <div className="ml-6">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${vc.text} bg-dark-700 border border-current/20`}>
              {verdict}
            </span>
            <p className="text-gray-400 text-sm mt-2 max-w-[200px]">
              {alert?.message?.substring(0, 120)}...
            </p>
          </motion.div>
        </div>
      </div>

      {/* Signal breakdown bars */}
      <div className="space-y-3">
        <p className="text-[10px] text-gray-500 uppercase tracking-wider">Signal Breakdown</p>
        {Object.entries(breakdown).map(([key, value], i) => {
          const weight = weights[key] || 0
          const pct = Math.round(value * 100)
          const weightPct = Math.round(weight * 100)

          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-400">{signalLabels[key] || key}</span>
                <span className="text-xs font-mono text-gray-500">
                  {pct}% <span className="text-gray-600">× {weightPct}%w</span>
                </span>
              </div>
              <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{
                    background: value > 0.7 ? 'linear-gradient(90deg, #ef4444, #dc2626)' :
                               value > 0.4 ? 'linear-gradient(90deg, #f59e0b, #d97706)' :
                               'linear-gradient(90deg, #22c55e, #16a34a)',
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ delay: 0.6 + i * 0.1, duration: 0.8, ease: 'easeOut' }}
                />
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Correlation bonus */}
      {probability?.correlation_bonus > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-4 bg-risk-high/5 border border-risk-high/10 rounded-lg p-3"
        >
          <p className="text-xs text-risk-high font-semibold flex items-center gap-1">
            ⚡ Correlation Bonus: +{Math.round(probability.correlation_bonus * 100)}%
          </p>
          <p className="text-[10px] text-gray-500 mt-1">
            Multiple independent signals are corroborating — increases confidence in ghost shift detection.
          </p>
        </motion.div>
      )}

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2 mt-5 pt-4 border-t border-white/5">
        {['File DMCA', 'Alert Customs', 'Platform Report'].map((action) => (
          <button
            key={action}
            onClick={() => alert(`${action} action initiated for ${brand} ${product}`)}
            className="px-3 py-1.5 rounded-lg bg-dark-700 border border-white/10 text-xs text-gray-400 hover:text-white hover:border-white/20 transition-all duration-200"
          >
            {action}
          </button>
        ))}
      </div>
    </div>
  )
}
