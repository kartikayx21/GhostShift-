import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import ListingForensicsCard from './ListingForensicsCard'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function IPFingerprintDashboard({ brand, product }) {
  const [scanResult, setScanResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [fingerprint, setFingerprint] = useState(null)

  useEffect(() => {
    if (brand && product) {
      runScan()
    }
  }, [brand, product])

  const runScan = async () => {
    setLoading(true)
    try {
      const [fpRes, compareRes] = await Promise.all([
        fetch(`${API_BASE}/api/fingerprint/extract`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ brand, product }),
        }),
        fetch(`${API_BASE}/api/fingerprint/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ brand, product }),
        }),
      ])

      const fpData = await fpRes.json()
      const compareData = await compareRes.json()

      setFingerprint(fpData.fingerprint)
      setScanResult(compareData)
    } catch (err) {
      console.error('Fingerprint scan failed:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="glass-card p-6 text-center">
        <motion.div
          className="w-8 h-8 border-2 border-accent-primary/30 border-t-accent-primary rounded-full mx-auto mb-3"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <p className="text-gray-500 text-sm">Scanning product fingerprint...</p>
      </div>
    )
  }

  const threatLevel = scanResult?.threat_level || 0
  const highRisk = scanResult?.high_risk_listings || 0
  const compResults = scanResult?.comparison_results || []
  const chips = fingerprint?.componentSignature?.chipIds || []
  const serialPattern = fingerprint?.componentSignature?.serialPattern || {}

  return (
    <div className="space-y-4">
      {/* Header card */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <span>🔬</span> IP Fingerprint Analysis
          </h3>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.3 }}
          >
            <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold ${
              threatLevel > 70 ? 'bg-risk-high/10 text-risk-high' :
              threatLevel > 40 ? 'bg-risk-medium/10 text-risk-medium' :
              'bg-risk-low/10 text-risk-low'
            }`}>
              Threat: {threatLevel}%
            </span>
          </motion.div>
        </div>

        {/* Threat gauge */}
        <div className="mb-4">
          <div className="h-3 bg-dark-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{
                background: threatLevel > 70 ? 'linear-gradient(90deg, #f59e0b, #ef4444)' :
                            threatLevel > 40 ? 'linear-gradient(90deg, #22c55e, #f59e0b)' :
                            'linear-gradient(90deg, #22c55e, #16a34a)',
              }}
              initial={{ width: 0 }}
              animate={{ width: `${threatLevel}%` }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
            />
          </div>
          <div className="flex justify-between text-[9px] text-gray-600 mt-1">
            <span>Monitoring</span>
            <span>Suspicious</span>
            <span>High Risk</span>
          </div>
        </div>

        {/* Product DNA */}
        {fingerprint && (
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-dark-700/50 rounded-lg p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Component DNA</p>
              <div className="space-y-1">
                {chips.map((chip, i) => (
                  <span key={i} className="inline-block text-[10px] bg-accent-primary/10 text-accent-glow px-2 py-0.5 rounded-full mr-1 mb-1">
                    {chip}
                  </span>
                ))}
              </div>
            </div>
            <div className="bg-dark-700/50 rounded-lg p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Serial Pattern</p>
              <p className="text-[10px] font-mono text-gray-400">{serialPattern.format || 'N/A'}</p>
              <p className="text-[10px] text-gray-600 mt-1">Checksum: {serialPattern.checksum || 'N/A'}</p>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="bg-dark-700/50 rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-accent-glow">{scanResult?.listings_analyzed || 0}</p>
            <p className="text-[9px] text-gray-500 uppercase">Scanned</p>
          </div>
          <div className="bg-dark-700/50 rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-risk-high">{highRisk}</p>
            <p className="text-[9px] text-gray-500 uppercase">High Risk</p>
          </div>
          <div className="bg-dark-700/50 rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-risk-medium">{(scanResult?.listings_analyzed || 0) - highRisk}</p>
            <p className="text-[9px] text-gray-500 uppercase">Other</p>
          </div>
        </div>
      </div>

      {/* Listing forensics cards */}
      {compResults.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span>🛒</span> Analyzed Listings ({compResults.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {compResults.map((listing, i) => (
              <ListingForensicsCard key={i} listing={listing} index={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
