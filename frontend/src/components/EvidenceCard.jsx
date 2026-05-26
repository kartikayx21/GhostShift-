import { motion } from 'framer-motion'

const TYPE_CONFIG = {
  listing: { icon: '🛒', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)', label: 'Listing' },
  supplier: { icon: '🏭', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', label: 'Supplier' },
  employment: { icon: '👤', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)', label: 'Employment' },
  forensic: { icon: '🔬', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.1)', label: 'Forensic' },
  synthesis: { icon: '⚖️', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', label: 'Synthesis' },
}

function getConfidenceColor(confidence) {
  if (confidence > 0.7) return '#22c55e'
  if (confidence > 0.4) return '#f59e0b'
  return '#ef4444'
}

function truncateUrl(url, maxLength = 40) {
  if (!url) return null
  try {
    const u = new URL(url)
    const display = u.hostname + u.pathname
    return display.length > maxLength ? display.slice(0, maxLength) + '...' : display
  } catch {
    return url.length > maxLength ? url.slice(0, maxLength) + '...' : url
  }
}

export default function EvidenceCard({ evidence, index = 0 }) {
  const { type, description, source_url, confidence } = evidence
  const config = TYPE_CONFIG[type] || TYPE_CONFIG.listing
  const confColor = getConfidenceColor(confidence)
  const confPercent = Math.round((confidence || 0) * 100)

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: 'easeOut' }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="glass-card p-5 flex flex-col gap-3 group cursor-default"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{config.icon}</span>
          <span
            className="text-xs font-semibold px-2.5 py-0.5 rounded-md uppercase tracking-wide"
            style={{ backgroundColor: config.bg, color: config.color }}
          >
            {config.label}
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-300 leading-relaxed flex-1">{description}</p>

      {/* Confidence */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500 font-medium">Confidence</span>
          <span className="text-xs font-mono font-semibold" style={{ color: confColor }}>
            {confPercent}%
          </span>
        </div>
        <div className="w-full h-1 bg-dark-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: confColor }}
            initial={{ width: 0 }}
            animate={{ width: `${confPercent}%` }}
            transition={{ duration: 0.8, delay: index * 0.08 + 0.3, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Source Link */}
      {source_url && (
        <a
          href={source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-xs text-accent-glow/70 hover:text-accent-glow transition-colors truncate"
        >
          <svg className="w-3 h-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <span className="truncate">{truncateUrl(source_url)}</span>
        </a>
      )}
    </motion.div>
  )
}
