import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function FactoryIntelTimeline({ brand, product }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch(`${API_BASE}/api/forensics/full-analysis`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ brand, product }),
        })
        const result = await res.json()
        setData(result)
      } catch (err) {
        console.error('Failed to load factory intel:', err)
      } finally {
        setLoading(false)
      }
    }
    if (brand && product) fetchData()
  }, [brand, product])

  if (loading || !data) return null

  const employees = data.employee_intelligence?.results || []
  const jobs = data.job_intelligence?.results || []
  const kt = data.knowledge_transfer || {}
  const dossier = data.dossier || {}

  return (
    <div className="space-y-4">
      {/* Employee Movement Timeline */}
      {employees.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <span>👥</span> Employee Movement Timeline
          </h3>

          <div className="relative pl-6">
            {/* Timeline line */}
            <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-accent-primary/50 via-risk-medium/50 to-risk-high/50" />

            {employees.map((emp, i) => {
              const riskColor = emp.classification === 'CRITICAL' ? 'risk-high' :
                               emp.classification === 'HIGH' ? 'risk-medium' : 'risk-low'
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.15 }}
                  className="relative mb-6 last:mb-0"
                >
                  {/* Timeline dot */}
                  <div className={`absolute -left-4 top-1 w-3 h-3 rounded-full bg-${riskColor} ring-2 ring-dark-800`} />

                  <div className="bg-dark-700/50 rounded-xl p-4 border border-white/5">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-sm font-semibold text-white">{emp.name}</p>
                        <p className="text-xs text-gray-500">{emp.role}</p>
                      </div>
                      <span className={`status-badge bg-${riskColor}/10 text-${riskColor} border border-${riskColor}/20 text-[10px]`}>
                        {emp.classification}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs mt-2">
                      <span className="text-gray-500 bg-dark-600/50 px-2 py-0.5 rounded">{emp.previous_employer}</span>
                      <span className="text-risk-high">→</span>
                      <span className="text-gray-400 bg-dark-600/50 px-2 py-0.5 rounded">{emp.current_employer}</span>
                    </div>

                    <div className="flex items-center justify-between mt-3 text-[10px]">
                      <span className="text-gray-600">{emp.months_since_transfer}mo ago • {emp.transfer_date}</span>
                      <span className="text-gray-500">Risk: <span className={`text-${riskColor} font-bold`}>{Math.round(emp.adjusted_risk * 100)}%</span></span>
                    </div>

                    <p className="text-[10px] text-gray-600 mt-2 italic">⚠ {emp.risk_signal}</p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      )}

      {/* Job Posting Activity */}
      {jobs.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <span>📋</span> Suspicious Job Postings
          </h3>

          <div className="space-y-3">
            {jobs.map((job, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="bg-dark-700/50 rounded-xl p-4 border border-white/5"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="text-sm font-semibold text-white">{job.title}</p>
                    <p className="text-xs text-gray-500">{job.company} • {job.location}</p>
                  </div>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                    job.risk_score > 0.6 ? 'bg-risk-high/10 text-risk-high' :
                    job.risk_score > 0.3 ? 'bg-risk-medium/10 text-risk-medium' :
                    'bg-risk-low/10 text-risk-low'
                  }`}>
                    {Math.round(job.risk_score * 100)}%
                  </span>
                </div>

                {/* Red flags */}
                <div className="flex flex-wrap gap-1 mt-2">
                  {(job.red_flags || []).map((flag, j) => (
                    <span key={j} className="text-[10px] px-2 py-0.5 rounded-full bg-risk-high/10 text-risk-high border border-risk-high/10">
                      🚩 {flag}
                    </span>
                  ))}
                </div>

                <p className="text-[10px] text-gray-600 mt-2">Posted: {job.posted_date}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Knowledge Transfer */}
      {kt.correlations?.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span>🧠</span> Knowledge Transfer Signals
          </h3>

          <div className="flex items-center gap-3 mb-3">
            <div className="bg-dark-700/50 rounded-lg p-3 text-center flex-1">
              <p className={`text-lg font-bold ${kt.kt_probability > 0.6 ? 'text-risk-high' : kt.kt_probability > 0.3 ? 'text-risk-medium' : 'text-risk-low'}`}>
                {Math.round((kt.kt_probability || 0) * 100)}%
              </p>
              <p className="text-[10px] text-gray-500 uppercase">KT Probability</p>
            </div>
            <div className="bg-dark-700/50 rounded-lg p-3 text-center flex-1">
              <p className={`text-lg font-bold ${kt.capacity_anomaly ? 'text-risk-high' : 'text-risk-low'}`}>
                {kt.capacity_ratio ? `${Math.round(kt.capacity_ratio * 100)}%` : 'N/A'}
              </p>
              <p className="text-[10px] text-gray-500 uppercase">Capacity Ratio</p>
            </div>
          </div>

          {kt.correlations.map((c, i) => (
            <div key={i} className="text-xs text-gray-400 bg-dark-700/30 rounded-lg p-2 mb-1">
              <span className="text-risk-medium font-semibold">{c.employee}</span>: {c.from} → {c.to}
              <span className="text-gray-600 ml-1">— {c.correlation}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
