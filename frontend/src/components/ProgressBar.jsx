import { motion } from 'framer-motion'

export default function ProgressBar({ progress = 0 }) {
  const clampedProgress = Math.min(100, Math.max(0, progress))

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-400 tracking-wide uppercase">
          Investigation Progress
        </span>
        <span className="text-sm font-mono font-semibold text-accent-glow">
          {Math.round(clampedProgress)}%
        </span>
      </div>
      <div className="w-full h-2 bg-dark-700 rounded-full overflow-hidden relative">
        <motion.div
          className="h-full rounded-full relative"
          style={{
            background: 'linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa)',
          }}
          initial={{ width: 0 }}
          animate={{ width: `${clampedProgress}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          {/* Shimmer effect */}
          <div
            className="absolute inset-0 rounded-full overflow-hidden"
            style={{
              background:
                'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 2s ease-in-out infinite',
            }}
          />
          {/* Glow pulse */}
          <div className="absolute inset-0 rounded-full animate-pulse-slow opacity-40"
            style={{
              boxShadow: '0 0 12px rgba(99, 102, 241, 0.6), 0 0 24px rgba(139, 92, 246, 0.3)',
            }}
          />
        </motion.div>
      </div>
      <style>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>
    </div>
  )
}
