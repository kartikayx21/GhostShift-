import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

const API_BASE = import.meta.env.VITE_API_URL || ''

const NODE_COLORS = {
  green: { bg: '#22c55e', glow: 'rgba(34,197,94,0.3)', border: '#16a34a' },
  yellow: { bg: '#f59e0b', glow: 'rgba(245,158,11,0.3)', border: '#d97706' },
  red: { bg: '#ef4444', glow: 'rgba(239,68,68,0.3)', border: '#dc2626' },
}

const NODE_ICONS = {
  brand: '🏢', supplier: '📦', factory: '🏭', product: '📱',
  listing: '🛒', employee: '👤', buyer: '💰',
}

export default function SupplyChainGraph({ brand, product }) {
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState(null)
  const [suspiciousPaths, setSuspiciousPaths] = useState([])

  useEffect(() => {
    async function fetchGraph() {
      try {
        const [graphRes, pathsRes] = await Promise.all([
          fetch(`${API_BASE}/api/supply-chain/graph`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, product }),
          }),
          fetch(`${API_BASE}/api/supply-chain/suspicious-paths`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, product }),
          }),
        ])

        const gData = await graphRes.json()
        const pData = await pathsRes.json()

        setGraphData(gData.graph)
        setSuspiciousPaths(pData.paths || [])
      } catch (err) {
        console.error('Failed to load supply chain graph:', err)
      } finally {
        setLoading(false)
      }
    }
    if (brand && product) fetchGraph()
  }, [brand, product])

  if (loading) {
    return (
      <div className="glass-card p-6 text-center">
        <motion.div
          className="w-8 h-8 border-2 border-accent-primary/30 border-t-accent-primary rounded-full mx-auto mb-3"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <p className="text-gray-500 text-sm">Building supply chain graph...</p>
      </div>
    )
  }

  if (!graphData) return null

  const { nodes, edges, stats } = graphData

  // Position nodes in a radial layout
  const centerX = 400
  const centerY = 250
  const radius = 180
  const nodePositions = {}
  nodes.forEach((node, i) => {
    const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2
    nodePositions[node.id] = {
      x: centerX + radius * Math.cos(angle) * (node.type === 'brand' ? 0.0 : 1.0),
      y: centerY + radius * Math.sin(angle) * (node.type === 'brand' ? 0.0 : 1.0),
    }
  })

  // Put brand node at center
  const brandNode = nodes.find(n => n.type === 'brand')
  if (brandNode) nodePositions[brandNode.id] = { x: centerX, y: centerY }

  const highlightedNodeIds = new Set()
  suspiciousPaths.forEach(p => p.path?.forEach(id => highlightedNodeIds.add(id)))

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
          <span>🔗</span> Supply Chain Intelligence
        </h3>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-risk-low" /> Verified
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-risk-medium" /> Suspicious
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-risk-high" /> Confirmed
          </span>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        {[
          { label: 'Nodes', value: stats.total_nodes, color: 'text-accent-glow' },
          { label: 'Connections', value: stats.total_edges, color: 'text-accent-glow' },
          { label: 'Suspicious', value: stats.suspicious_nodes, color: 'text-risk-medium' },
          { label: 'Alert Paths', value: suspiciousPaths.length, color: 'text-risk-high' },
        ].map((stat, i) => (
          <div key={i} className="bg-dark-700/50 rounded-xl p-3 text-center">
            <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
            <p className="text-[10px] text-gray-500 uppercase tracking-wider">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Graph SVG */}
      <div className="relative bg-dark-900/50 rounded-xl overflow-hidden border border-white/5" style={{ height: 500 }}>
        <svg width="100%" height="100%" viewBox="0 0 800 500">
          {/* Edges */}
          {edges.map((edge, i) => {
            const from = nodePositions[edge.from]
            const to = nodePositions[edge.to]
            if (!from || !to) return null
            return (
              <g key={`edge-${i}`}>
                <line
                  x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                  stroke={edge.suspicious ? '#ef4444' : '#333'}
                  strokeWidth={edge.suspicious ? 2 : 1}
                  strokeDasharray={edge.suspicious ? '6,3' : 'none'}
                  opacity={0.6}
                />
                {edge.label && (
                  <text
                    x={(from.x + to.x) / 2} y={(from.y + to.y) / 2 - 6}
                    fill="#666" fontSize="9" textAnchor="middle"
                  >
                    {edge.label}
                  </text>
                )}
                <text
                  x={(from.x + to.x) / 2} y={(from.y + to.y) / 2 + 6}
                  fill={edge.suspicious ? '#ef4444' : '#555'} fontSize="8" textAnchor="middle"
                  fontWeight={edge.suspicious ? 'bold' : 'normal'}
                >
                  {edge.relation}
                </text>
              </g>
            )
          })}

          {/* Nodes */}
          {nodes.map((node) => {
            const pos = nodePositions[node.id]
            if (!pos) return null
            const colors = NODE_COLORS[node.color] || NODE_COLORS.yellow
            const icon = NODE_ICONS[node.type] || '❓'
            const isHighlighted = highlightedNodeIds.has(node.id)
            const isSelected = selectedNode?.id === node.id

            return (
              <g key={node.id} onClick={() => setSelectedNode(node)} style={{ cursor: 'pointer' }}>
                {/* Glow effect */}
                {(isHighlighted || isSelected) && (
                  <circle cx={pos.x} cy={pos.y} r={32}
                    fill="none" stroke={colors.bg} strokeWidth={2} opacity={0.5}
                  >
                    <animate attributeName="r" values="28;34;28" dur="2s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0.5;0.2;0.5" dur="2s" repeatCount="indefinite" />
                  </circle>
                )}
                {/* Node circle */}
                <circle cx={pos.x} cy={pos.y} r={24}
                  fill="#111" stroke={colors.bg} strokeWidth={2}
                />
                {/* Icon */}
                <text x={pos.x} y={pos.y + 1} textAnchor="middle" dominantBaseline="central" fontSize="16">
                  {icon}
                </text>
                {/* Label */}
                <text x={pos.x} y={pos.y + 38} textAnchor="middle" fill="#ccc" fontSize="9" fontWeight="500">
                  {node.name.length > 20 ? node.name.substring(0, 18) + '…' : node.name}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {/* Selected node detail panel */}
      {selectedNode && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 bg-dark-700/70 rounded-xl p-4 border border-white/5"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-xl">{NODE_ICONS[selectedNode.type]}</span>
              <h4 className="font-semibold text-white text-sm">{selectedNode.name}</h4>
            </div>
            <button onClick={() => setSelectedNode(null)} className="text-gray-500 hover:text-gray-300 text-xs">✕</button>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div><span className="text-gray-500">Type:</span> <span className="text-gray-300 capitalize">{selectedNode.type}</span></div>
            <div><span className="text-gray-500">Status:</span> <span className="text-gray-300 capitalize">{selectedNode.status}</span></div>
            <div>
              <span className="text-gray-500">Risk:</span>{' '}
              <span className={
                selectedNode.color === 'red' ? 'text-risk-high' :
                selectedNode.color === 'yellow' ? 'text-risk-medium' : 'text-risk-low'
              }>
                {selectedNode.color === 'red' ? 'High' : selectedNode.color === 'yellow' ? 'Medium' : 'Low'}
              </span>
            </div>
          </div>
          {/* Connected edges */}
          <div className="mt-3 pt-3 border-t border-white/5">
            <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Connections</p>
            <div className="space-y-1">
              {edges.filter(e => e.from === selectedNode.id || e.to === selectedNode.id).map((e, i) => (
                <div key={i} className="text-xs text-gray-400">
                  <span className={e.suspicious ? 'text-risk-high' : ''}>{e.relation}</span>
                  {' → '}
                  <span className="text-gray-300">{e.from === selectedNode.id ? e.to : e.from}</span>
                  {e.label && <span className="text-gray-600 ml-1">({e.label})</span>}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
