import React from 'react'

const CATEGORY_STYLES = {
  billing: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-400', label: 'Billing' },
  technical: { bg: 'bg-purple-100', text: 'text-purple-700', dot: 'bg-purple-400', label: 'Technical' },
  refund: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-400', label: 'Refund' },
  other: { bg: 'bg-slate-100', text: 'text-slate-600', dot: 'bg-slate-400', label: 'Other' },
  unclassified: { bg: 'bg-white', text: 'text-slate-400', dot: 'bg-slate-200', label: 'Unclassified' },
}

const PRIORITY_STYLES = {
  high: 'bg-red-500',
  medium: 'bg-amber-400',
  low: 'bg-emerald-400',
}

const STATUS_STYLES = {
  new: { bg: 'bg-slate-100', text: 'text-slate-600', label: 'New' },
  draft_ready: { bg: 'bg-violet-100', text: 'text-violet-700', label: 'Draft Ready' },
  approved: { bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Approved' },
  edited_sent: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Edited' },
  rejected: { bg: 'bg-red-100', text: 'text-red-600', label: 'Rejected' },
}

function relativeTime(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function TicketCard({ ticket, selected, onClick }) {
  const category = ticket.classification?.category || 'unclassified'
  const catStyle = CATEGORY_STYLES[category] || CATEGORY_STYLES.unclassified
  const priStyle = PRIORITY_STYLES[ticket.priority] || PRIORITY_STYLES.medium
  const statusStyle = STATUS_STYLES[ticket.status] || STATUS_STYLES.new
  const isProcessing = ticket.status === 'new'

  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left px-4 py-3.5 border-b border-slate-100 transition-all duration-150 relative
        ${selected
          ? 'bg-violet-50 border-l-4 border-l-violet-500'
          : 'bg-white hover:bg-slate-50 border-l-4 border-l-transparent'
        }
      `}
    >
      {/* Top row: name + priority dot + time */}
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${priStyle}`} />
          <span className={`text-sm font-semibold leading-tight ${selected ? 'text-violet-900' : 'text-slate-800'}`}>
            {ticket.customer_name}
          </span>
        </div>
        <span className="text-xs text-slate-400 flex-shrink-0 ml-2">
          {relativeTime(ticket.created_at)}
        </span>
      </div>

      {/* Subject */}
      <p className="text-xs text-slate-600 mb-2.5 line-clamp-1 pl-4">
        {ticket.subject}
      </p>

      {/* Bottom row: category badge + status badge */}
      <div className="flex items-center gap-1.5 pl-4 flex-wrap">
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${catStyle.bg} ${catStyle.text}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${catStyle.dot}`} />
          {catStyle.label}
        </span>
        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusStyle.bg} ${statusStyle.text}`}>
          {isProcessing ? (
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
              Processing
            </span>
          ) : statusStyle.label}
        </span>
      </div>
    </button>
  )
}

export default function TicketQueue({ tickets, selectedId, onSelect, loading }) {
  const filterCounts = {
    all: tickets.length,
    new: tickets.filter(t => t.status === 'new').length,
    draft_ready: tickets.filter(t => t.status === 'draft_ready').length,
    decided: tickets.filter(t => ['approved', 'edited_sent', 'rejected'].includes(t.status)).length,
  }

  if (loading) {
    return (
      <div className="flex flex-col h-full bg-white">
        <div className="px-4 py-4 border-b border-slate-200">
          <div className="h-5 w-24 bg-slate-200 rounded animate-pulse mb-2" />
          <div className="h-3 w-32 bg-slate-100 rounded animate-pulse" />
        </div>
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="px-4 py-3.5 border-b border-slate-100 animate-pulse">
            <div className="flex justify-between mb-2">
              <div className="h-4 w-28 bg-slate-200 rounded" />
              <div className="h-3 w-10 bg-slate-100 rounded" />
            </div>
            <div className="h-3 w-40 bg-slate-100 rounded mb-2 ml-4" />
            <div className="flex gap-2 ml-4">
              <div className="h-5 w-16 bg-slate-100 rounded-full" />
              <div className="h-5 w-20 bg-slate-100 rounded-full" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="px-4 py-4 border-b border-slate-200 flex-shrink-0">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-slate-800 text-sm">Ticket Queue</h2>
          <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">
            {filterCounts.all}
          </span>
        </div>
        {/* Mini stats */}
        <div className="grid grid-cols-3 gap-1.5">
          <div className="bg-slate-50 rounded-lg px-2 py-1.5 text-center">
            <div className="text-sm font-bold text-amber-500">{filterCounts.new + filterCounts.draft_ready}</div>
            <div className="text-xs text-slate-500">Pending</div>
          </div>
          <div className="bg-slate-50 rounded-lg px-2 py-1.5 text-center">
            <div className="text-sm font-bold text-violet-600">{filterCounts.draft_ready}</div>
            <div className="text-xs text-slate-500">Ready</div>
          </div>
          <div className="bg-slate-50 rounded-lg px-2 py-1.5 text-center">
            <div className="text-sm font-bold text-emerald-600">{filterCounts.decided}</div>
            <div className="text-xs text-slate-500">Decided</div>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {tickets.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
            <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-3">
              <svg className="w-6 h-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-sm text-slate-500">No tickets yet</p>
          </div>
        ) : (
          tickets.map(ticket => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              selected={ticket.id === selectedId}
              onClick={() => onSelect(ticket.id)}
            />
          ))
        )}
      </div>
    </div>
  )
}
