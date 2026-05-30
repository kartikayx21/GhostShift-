import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import ProgressBar from '../components/ProgressBar'
import AgentCard from '../components/AgentCard'
import ActivityLog from '../components/ActivityLog'

const API_BASE = import.meta.env.VITE_API_URL || ''

// These match the backend agent names from database.py
const AGENT_KEYS = ['hunter', 'component_tracer', 'factory_spy', 'forensics', 'judge']
const AGENT_DISPLAY_NAMES = {
  'hunter': 'The Hunter',
  'component_tracer': 'The Component Tracer',
  'factory_spy': 'The Factory Spy',
  'forensics': 'The Forensics Agent',
  'judge': 'The Judge',
}

export default function Investigation() {
  const { id } = useParams()
  const navigate = useNavigate()
  const eventSourceRef = useRef(null)
  const pollRef = useRef(null)

  const [brand, setBrand] = useState('')
  const [product, setProduct] = useState('')
  const [progress, setProgress] = useState(0)
  const [agents, setAgents] = useState(() => {
    const initial = {}
    AGENT_KEYS.forEach((key) => {
      initial[key] = { name: AGENT_DISPLAY_NAMES[key], status: 'pending', findings_count: 0 }
    })
    return initial
  })
  const [logs, setLogs] = useState([])
  const [isComplete, setIsComplete] = useState(false)

  // Fetch initial status
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/investigate/${id}/status`)
      if (!res.ok) return

      const data = await res.json()
      if (data.brand) setBrand(data.brand)
      if (data.product) setProduct(data.product)
      if (data.overall_progress != null) setProgress(data.overall_progress)

      if (data.agents && Array.isArray(data.agents)) {
        setAgents((prev) => {
          const next = { ...prev }
          data.agents.forEach((agentInfo) => {
            // Find the matching key by name
            const matchKey = AGENT_KEYS.find(
              (k) => AGENT_DISPLAY_NAMES[k] === agentInfo.name
            )
            if (matchKey) {
              next[matchKey] = {
                name: agentInfo.name,
                status: agentInfo.status || 'pending',
                findings_count: agentInfo.findings_count || 0,
              }
            }
          })
          return next
        })
      }

      if (data.status === 'complete' || data.status === 'completed') {
        setIsComplete(true)
        setProgress(100)
        setTimeout(() => navigate(`/dossier/${id}`), 2500)
      }
    } catch {
      // silently fail
    }
  }, [id, navigate])

  // SSE connection
  useEffect(() => {
    fetchStatus()

    // Connect to SSE stream
    const eventSource = new EventSource(`${API_BASE}/api/investigate/${id}/stream`)
    eventSourceRef.current = eventSource

    eventSource.addEventListener('log', (event) => {
      try {
        const data = JSON.parse(event.data)
        setLogs((prev) => [...prev, data])
      } catch {}
    })

    eventSource.addEventListener('status', (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.agent) {
          setAgents((prev) => ({
            ...prev,
            [data.agent]: {
              name: data.name || AGENT_DISPLAY_NAMES[data.agent] || data.agent,
              status: data.status || prev[data.agent]?.status || 'pending',
              findings_count: data.findings_count ?? prev[data.agent]?.findings_count ?? 0,
            },
          }))
        }
        // Also refresh status to get updated progress
        fetchStatus()
      } catch {}
    })

    eventSource.addEventListener('error', (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.agent) {
          setAgents((prev) => ({
            ...prev,
            [data.agent]: {
              name: data.name || AGENT_DISPLAY_NAMES[data.agent] || data.agent,
              status: 'error',
              findings_count: 0,
            },
          }))
        }
      } catch {}
    })

    eventSource.addEventListener('complete', () => {
      setIsComplete(true)
      setProgress(100)
      setTimeout(() => navigate(`/dossier/${id}`), 2500)
    })

    eventSource.onerror = () => {
      // SSE disconnected — will rely on polling fallback
    }

    // Polling fallback every 3s
    pollRef.current = setInterval(fetchStatus, 3000)

    return () => {
      eventSource.close()
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [id, fetchStatus, navigate])

  return (
    <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-8 max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
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

        <div className="flex items-center gap-4 flex-wrap">
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            Investigation in Progress
          </h1>
          {isComplete && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="status-badge bg-risk-low/10 text-risk-low border border-risk-low/20"
            >
              <span className="w-2 h-2 rounded-full bg-risk-low" />
              Complete
            </motion.span>
          )}
        </div>

        {(brand || product) && (
          <p className="text-gray-500 text-sm mt-1 font-mono">
            {brand} {brand && product && '—'} {product}
          </p>
        )}
      </motion.div>

      {/* Progress */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <ProgressBar progress={progress} />
      </motion.div>

      {/* Two-column layout */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Agents */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="w-full lg:w-1/3 space-y-3"
        >
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            AI Agents
          </h2>
          {AGENT_KEYS.map((key, i) => (
            <AgentCard
              key={key}
              name={agents[key]?.name || AGENT_DISPLAY_NAMES[key]}
              status={agents[key]?.status || 'pending'}
              findingsCount={agents[key]?.findings_count || 0}
              index={i}
            />
          ))}
        </motion.div>

        {/* Right: Activity Log */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="w-full lg:w-2/3"
        >
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Activity Feed
          </h2>
          <ActivityLog logs={logs} />
        </motion.div>
      </div>

      {/* Redirecting overlay */}
      {isComplete && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm flex items-center justify-center z-40"
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="glass-card p-8 text-center"
          >
            <motion.div
              className="w-12 h-12 border-4 border-accent-primary/30 border-t-accent-primary rounded-full mx-auto mb-4"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
            <p className="text-lg font-semibold text-white">Investigation Complete</p>
            <p className="text-sm text-gray-400 mt-1">Preparing your evidence dossier...</p>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
