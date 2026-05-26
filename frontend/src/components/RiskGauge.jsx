import React, { useEffect, useState } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'

function getRiskColor(score) {
  if (score <= 40) return { color: '#22c55e', glow: 'rgba(34, 197, 94, 0.3)', label: 'LOW' }
  if (score <= 70) return { color: '#f59e0b', glow: 'rgba(245, 158, 11, 0.3)', label: 'MEDIUM' }
  return { color: '#ef4444', glow: 'rgba(239, 68, 68, 0.3)', label: 'HIGH' }
}

export default function RiskGauge({ score = 0, animated = true }) {
  const clampedScore = Math.min(100, Math.max(0, score))
  const risk = getRiskColor(clampedScore)

  const cx = 140
  const cy = 140
  const r = 110
  const strokeWidth = 14
  const startAngle = 135
  const endAngle = 405
  const totalAngle = endAngle - startAngle

  const toRad = (deg) => (deg * Math.PI) / 180

  const bgStartX = cx + r * Math.cos(toRad(startAngle))
  const bgStartY = cy + r * Math.sin(toRad(startAngle))
  const bgEndX = cx + r * Math.cos(toRad(endAngle))
  const bgEndY = cy + r * Math.sin(toRad(endAngle))

  const bgPath = `M ${bgStartX} ${bgStartY} A ${r} ${r} 0 1 1 ${bgEndX} ${bgEndY}`

  const arcLength = (totalAngle / 360) * 2 * Math.PI * r

  const motionProgress = useMotionValue(0)
  const dashOffset = useTransform(motionProgress, (v) => {
    const filled = (v / 100) * arcLength
    return arcLength - filled
  })

  const displayScore = useMotionValue(0)
  const [displayNum, setDisplayNum] = useState(0)

  useEffect(() => {
    if (animated) {
      animate(motionProgress, clampedScore, { duration: 1.8, ease: 'easeOut' })
      animate(displayScore, clampedScore, { duration: 1.8, ease: 'easeOut' })
    } else {
      motionProgress.set(clampedScore)
      displayScore.set(clampedScore)
      setDisplayNum(Math.round(clampedScore))
    }
  }, [clampedScore, animated])

  useEffect(() => {
    const unsubscribe = displayScore.on('change', (v) => {
      setDisplayNum(Math.round(v))
    })
    return () => unsubscribe()
  }, [])

  return (
    <div className="relative flex flex-col items-center">
      <svg width="280" height="280" viewBox="0 0 280 280" className="drop-shadow-2xl">
        <defs>
          <filter id="riskGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={risk.color} stopOpacity="0.6" />
            <stop offset="100%" stopColor={risk.color} stopOpacity="1" />
          </linearGradient>
        </defs>

        {/* Background arc */}
        <path
          d={bgPath}
          fill="none"
          stroke="#1a1a1a"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Subtle background ring glow */}
        <path
          d={bgPath}
          fill="none"
          stroke={risk.color}
          strokeWidth={strokeWidth + 8}
          strokeLinecap="round"
          strokeDasharray={arcLength}
          style={{ strokeDashoffset: arcLength - (clampedScore / 100) * arcLength }}
          opacity="0.08"
        />

        {/* Foreground arc */}
        <motion.path
          d={bgPath}
          fill="none"
          stroke={risk.color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={arcLength}
          style={{ strokeDashoffset: dashOffset }}
          filter="url(#riskGlow)"
        />

        {/* Center score */}
        <text
          x={cx}
          y={cy - 8}
          textAnchor="middle"
          dominantBaseline="central"
          fill="white"
          fontSize="56"
          fontWeight="800"
          fontFamily="Inter, system-ui, sans-serif"
        >
          {displayNum}
        </text>
        <text
          x={cx + 36}
          y={cy - 18}
          textAnchor="start"
          dominantBaseline="central"
          fill={risk.color}
          fontSize="20"
          fontWeight="600"
          fontFamily="Inter, system-ui, sans-serif"
        >
          %
        </text>
        <text
          x={cx}
          y={cy + 32}
          textAnchor="middle"
          dominantBaseline="central"
          fill="#6b7280"
          fontSize="11"
          fontWeight="600"
          letterSpacing="3"
          fontFamily="Inter, system-ui, sans-serif"
        >
          RISK SCORE
        </text>
      </svg>

      {/* Risk level badge */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.5, duration: 0.5 }}
        className="mt-2 status-badge"
        style={{
          backgroundColor: `${risk.color}15`,
          color: risk.color,
          border: `1px solid ${risk.color}30`,
        }}
      >
        <span
          className="w-2 h-2 rounded-full inline-block"
          style={{ backgroundColor: risk.color }}
        />
        {risk.label} RISK
      </motion.div>
    </div>
  )
}
