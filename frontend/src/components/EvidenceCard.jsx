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

function formatSourceLabel(url) {
  if (!url) return null
  try {
    const u = new URL(url)
    const hostname = u.hostname.replace('www.', '')
    const path = u.pathname
    // Build a readable reference like "AliExpress Item #3140897"
    if (hostname.includes('aliexpress')) {
      const match = path.match(/item\/(\d+)/)
      return match ? `AliExpress Listing #${match[1]}` : `AliExpress Evidence`
    }
    if (hostname.includes('dhgate')) {
      const match = path.match(/product\/(\d+)/)
      return match ? `DHgate Listing #${match[1]}` : `DHgate Evidence`
    }
    if (hostname.includes('taobao')) {
      const match = path.match(/item\/(\d+)/)
      return match ? `Taobao Listing #${match[1]}` : `Taobao Evidence`
    }
    if (hostname.includes('1688')) {
      const slug = path.split('/').filter(Boolean).pop()
      return slug ? `1688.com — ${slug.replace(/-/g, ' ')}` : `1688.com Supplier Record`
    }
    if (hostname.includes('linkedin')) {
      const slug = path.split('/').filter(Boolean).pop()
      return slug ? `LinkedIn — ${slug.replace(/-/g, ' ')}` : `LinkedIn Profile`
    }
    if (hostname.includes('alibaba')) {
      const slug = path.split('/').filter(Boolean).pop()
      return slug ? `Alibaba — ${slug.replace(/-/g, ' ')}` : `Alibaba Supplier`
    }
    if (hostname.includes('zhaopin') || hostname.includes('51job') || hostname.includes('liepin')) {
      const match = path.match(/job\/(\d+)/)
      return match ? `${hostname} Job #${match[1]}` : `${hostname} Job Posting`
    }
    // Fallback: show hostname + truncated path
    const display = hostname + path
    return display.length > 45 ? display.slice(0, 45) + '…' : display
  } catch {
    return url.length > 45 ? url.slice(0, 45) + '…' : url
  }
}

export default function EvidenceCard({ evidence, index = 0 }) {
  const { type, description, source_url, confidence } = evidence
  const config = TYPE_CONFIG[type] || TYPE_CONFIG.listing
  const confColor = getConfidenceColor(confidence)
  const confPercent = Math.round((confidence || 0) * 100)
  const sourceLabel = formatSourceLabel(source_url)

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

      {/* Source Reference (non-clickable evidence tag) */}
      {sourceLabel && (
        <div className="flex items-center gap-2 flex-wrap">
          <div
            className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg truncate"
            style={{ backgroundColor: 'rgba(99, 102, 241, 0.08)', color: 'rgba(165, 180, 252, 0.8)', border: '1px solid rgba(99, 102, 241, 0.15)' }}
            title={source_url}
          >
            <svg className="w-3 h-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span className="truncate">{sourceLabel}</span>
          </div>
          <span
            className="text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-widest"
            style={{ backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.25)' }}
          >
            Simulated
          </span>
        </div>
      )}
    </motion.div>
  )
}

