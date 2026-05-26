import { motion } from 'framer-motion'

const AGENT_ICONS = ['🔍', '🔗', '🏭', '🔬', '⚖️']

const statusConfig = {
  pending: {
    color: 'border-gray-600',
    dotColor: 'bg-gray-500',
    label: 'Waiting...',
    labelColor: 'text-gray-500',
  },
  running: {
    color: 'border-accent-primary',
    dotColor: 'bg-accent-primary',
    label: 'Analyzing...',
    labelColor: 'text-accent-glow',
  },
  complete: {
    color: 'border-risk-low',
    dotColor: 'bg-risk-low',
    label: 'Complete',
    labelColor: 'text-risk-low',
  },
  error: {
    color: 'border-risk-high',
    dotColor: 'bg-risk-high',
    label: 'Error',
    labelColor: 'text-risk-high',
  },
}

export default function AgentCard({ name, status = 'pending', findingsCount = 0, index = 0 }) {
  const config = statusConfig[status] || statusConfig.pending
  const icon = AGENT_ICONS[index] || '🔍'

  return (
    <motion.div
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1, ease: 'easeOut' }}
      className={`glass-card p-4 border-l-4 ${config.color} transition-all duration-500`}
    >
      <div className="flex items-center gap-3">
        {/* Agent Icon */}
        <div className="text-2xl flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-xl bg-dark-700/60">
          {icon}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-white truncate">{name}</h3>
          <div className="flex items-center gap-2 mt-1">
            {/* Status indicator */}
            {status === 'pending' && (
              <motion.div
                className={`w-2 h-2 rounded-full ${config.dotColor}`}
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              />
            )}
            {status === 'running' && (
              <motion.div
                className="w-4 h-4 border-2 border-accent-primary border-t-transparent rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
            )}
            {status === 'complete' && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <svg className="w-4 h-4 text-risk-low" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </motion.div>
            )}
            {status === 'error' && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <svg className="w-4 h-4 text-risk-high" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.div>
            )}
            <span className={`text-xs font-medium ${config.labelColor}`}>{config.label}</span>
          </div>
        </div>

        {/* Findings badge */}
        {status === 'complete' && findingsCount > 0 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 400, delay: 0.2 }}
            className="flex-shrink-0 bg-accent-primary/15 text-accent-glow text-xs font-mono font-semibold px-2.5 py-1 rounded-lg"
          >
            {findingsCount} finding{findingsCount !== 1 ? 's' : ''}
          </motion.div>
        )}
      </div>

      {/* Running shimmer bar */}
      {status === 'running' && (
        <div className="mt-3 h-0.5 bg-dark-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full w-1/3 rounded-full"
            style={{ background: 'linear-gradient(90deg, transparent, #6366f1, transparent)' }}
            animate={{ x: ['-100%', '400%'] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>
      )}
    </motion.div>
  )
}
