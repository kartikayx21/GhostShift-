import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const AGENT_COLORS = {
  'Hunter': 'text-blue-400',
  'Listing Hunter': 'text-blue-400',
  'Tracer': 'text-purple-400',
  'Supply Chain Tracer': 'text-purple-400',
  'Factory Spy': 'text-amber-400',
  'Factory Intelligence': 'text-amber-400',
  'Forensics': 'text-cyan-400',
  'Digital Forensics': 'text-cyan-400',
  'Judge': 'text-red-400',
  'Risk Judge': 'text-red-400',
}

function getAgentColor(name) {
  for (const [key, value] of Object.entries(AGENT_COLORS)) {
    if (name.toLowerCase().includes(key.toLowerCase())) return value
  }
  return 'text-gray-400'
}

function formatTimestamp(ts) {
  if (!ts) return '--:--:--'
  try {
    const date = new Date(ts)
    return date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ts
  }
}

export default function ActivityLog({ logs = [] }) {
  const containerRef = useRef(null)
  const displayLogs = logs.slice(-100)

  // Auto-scroll to bottom
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [logs.length])

  return (
    <div className="glass-card overflow-hidden flex flex-col" style={{ maxHeight: '520px' }}>
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
        <div className="w-2 h-2 rounded-full bg-risk-low animate-pulse" />
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Live Activity</span>
        <span className="text-xs text-gray-600 font-mono ml-auto">{displayLogs.length} entries</span>
      </div>

      {/* Log entries */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto p-3 space-y-0.5 font-mono text-xs bg-dark-700/40"
      >
        {displayLogs.length === 0 ? (
          <div className="flex items-center justify-center h-full min-h-[200px]">
            <p className="text-gray-600 italic text-sm font-sans">Waiting for agent activity...</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {displayLogs.map((log, i) => (
              <motion.div
                key={`${log.timestamp}-${i}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="py-1 px-2 rounded hover:bg-white/[0.02] leading-relaxed"
              >
                <span className="text-gray-600">[{formatTimestamp(log.timestamp)}]</span>
                {' '}
                <span className={`font-semibold ${getAgentColor(log.agent_name)}`}>
                  {log.agent_name}:
                </span>
                {' '}
                <span className="text-gray-300">{log.message}</span>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  )
}
