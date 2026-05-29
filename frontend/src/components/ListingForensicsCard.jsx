import { motion } from 'framer-motion'

const THRESHOLD_COLORS = {
  red: { text: 'text-risk-high', bg: 'bg-risk-high', bar: '#ef4444' },
  yellow: { text: 'text-risk-medium', bg: 'bg-risk-medium', bar: '#f59e0b' },
  green: { text: 'text-risk-low', bg: 'bg-risk-low', bar: '#22c55e' },
}

const FINDING_ICONS = {
  logo_inconsistency: '🔍',
  material_quality: '🔬',
  packaging_anomaly: '📦',
  background_match: '🏭',
  serial_mismatch: '🔢',
  color_deviation: '🎨',
  build_quality: '🔩',
  font_mismatch: '✏️',
}

const SEVERITY_BADGE = {
  critical: 'bg-risk-high/10 text-risk-high border-risk-high/20',
  high: 'bg-risk-high/10 text-risk-high border-risk-high/20',
  medium: 'bg-risk-medium/10 text-risk-medium border-risk-medium/20',
  low: 'bg-risk-low/10 text-risk-low border-risk-low/20',
}

export default function ListingForensicsCard({ listing, index = 0 }) {
  if (!listing) return null

  const comparison = listing.comparison || {}
  const overallSuspicion = comparison.overallSuspicion || 0
  const suspicionPct = Math.round(overallSuspicion * 100)
  const verdict = comparison.verdict || 'LOW_RISK'

  const verdictConfig = {
    HIGH_RISK: { label: 'High Risk', color: 'text-risk-high', bg: 'bg-risk-high/10' },
    SUSPICIOUS: { label: 'Suspicious', color: 'text-risk-medium', bg: 'bg-risk-medium/10' },
    LOW_RISK: { label: 'Low Risk', color: 'text-risk-low', bg: 'bg-risk-low/10' },
  }

  const vc = verdictConfig[verdict] || verdictConfig.LOW_RISK

  // Price analysis
  const price = listing.price || 0
  const genuinePrice = listing.genuine_price || 0
  const priceRatio = genuinePrice > 0 ? (price / genuinePrice) : 0
  const pricePct = Math.round(priceRatio * 100)
  const priceThreshold = priceRatio > 0.85 ? 'green' : priceRatio > 0.6 ? 'yellow' : 'red'
  const tc = THRESHOLD_COLORS[priceThreshold]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="glass-card overflow-hidden"
    >
      {/* Header with verdict */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-lg">{listing.platform === 'AliExpress' ? '🛍️' : listing.platform === 'DHgate' ? '🏪' : '📱'}</span>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-white truncate">{listing.title}</p>
            <p className="text-[10px] text-gray-500">{listing.platform} • {listing.seller || 'Unknown seller'}</p>
          </div>
        </div>
        <span className={`status-badge ${vc.bg} ${vc.color} border border-current/20 text-[10px] flex-shrink-0`}>
          {vc.label}
        </span>
      </div>

      {/* Price comparison */}
      <div className="px-4 py-3 border-b border-white/5">
        <div className="flex items-center justify-between mb-2">
          <div>
            <p className="text-xs text-gray-500">Listing Price</p>
            <p className={`text-lg font-bold ${tc.text}`}>${price.toFixed(2)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500">vs Genuine</p>
            <p className={`text-sm font-bold ${tc.text}`}>{pricePct}%</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Genuine Price</p>
            <p className="text-lg font-bold text-gray-300">${genuinePrice.toFixed(2)}</p>
          </div>
        </div>

        {/* Price bar */}
        <div className="relative h-2 bg-dark-700 rounded-full overflow-hidden">
          <div className="absolute inset-0 flex">
            <div className="bg-risk-high/20 flex-1" style={{ maxWidth: '40%' }} />
            <div className="bg-risk-medium/20 flex-1" style={{ maxWidth: '25%' }} />
            <div className="bg-risk-low/20 flex-1" />
          </div>
          <motion.div
            className="absolute top-0 h-full w-1 rounded-full"
            style={{ backgroundColor: tc.bar }}
            initial={{ left: 0 }}
            animate={{ left: `${Math.min(pricePct, 100)}%` }}
            transition={{ delay: 0.3 + index * 0.1, duration: 0.8 }}
          />
        </div>
        <div className="flex justify-between text-[8px] text-gray-600 mt-1">
          <span>Impossible</span>
          <span>Suspicious</span>
          <span>Normal</span>
        </div>
      </div>

      {/* Suspicion scores */}
      <div className="px-4 py-3 border-b border-white/5">
        <div className="grid grid-cols-3 gap-2 text-center">
          {[
            { label: 'Component', value: comparison.componentOverlap },
            { label: 'Visual', value: comparison.visualMatch },
            { label: 'Pricing', value: comparison.pricingDeviation },
          ].map((item) => (
            <div key={item.label}>
              <p className={`text-sm font-bold ${
                (item.value || 0) > 0.7 ? 'text-risk-high' :
                (item.value || 0) > 0.4 ? 'text-risk-medium' : 'text-risk-low'
              }`}>
                {Math.round((item.value || 0) * 100)}%
              </p>
              <p className="text-[9px] text-gray-600 uppercase">{item.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Flags */}
      {listing.flags?.length > 0 && (
        <div className="px-4 py-3">
          <div className="flex flex-wrap gap-1">
            {listing.flags.map((flag, i) => (
              <span key={i} className="text-[9px] px-2 py-0.5 rounded-full bg-risk-high/10 text-risk-high/80 border border-risk-high/10">
                {flag.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
