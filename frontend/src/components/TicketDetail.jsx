import React from 'react'

const PRIORITY_BADGE = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-emerald-100 text-emerald-700',
}

const STATUS_BADGE = {
  new: 'bg-slate-100 text-slate-600',
  draft_ready: 'bg-violet-100 text-violet-700',
  approved: 'bg-emerald-100 text-emerald-700',
  edited_sent: 'bg-blue-100 text-blue-700',
  rejected: 'bg-red-100 text-red-600',
}

function formatDate(dateStr) {
  if (!dateStr) return 'Unknown'
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function Avatar({ name }) {
  const initials = name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
  const colors = ['bg-violet-500', 'bg-blue-500', 'bg-indigo-500', 'bg-emerald-500', 'bg-orange-500', 'bg-pink-500']
  const idx = name.charCodeAt(0) % colors.length
  return (
    <div className={`w-10 h-10 rounded-full ${colors[idx]} flex items-center justify-center text-white font-semibold text-sm flex-shrink-0`}>
      {initials}
    </div>
  )
}

export default function TicketDetail({ ticket, loading }) {
  if (loading) {
    return (
      <div className="flex flex-col h-full p-5 animate-pulse">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-slate-200 rounded-full" />
          <div className="space-y-1.5">
            <div className="h-4 w-32 bg-slate-200 rounded" />
            <div className="h-3 w-40 bg-slate-100 rounded" />
          </div>
        </div>
        <div className="h-6 w-3/4 bg-slate-200 rounded mb-4" />
        <div className="flex gap-2 mb-5">
          <div className="h-5 w-16 bg-slate-100 rounded-full" />
          <div className="h-5 w-20 bg-slate-100 rounded-full" />
          <div className="h-5 w-24 bg-slate-100 rounded-full" />
        </div>
        <div className="space-y-2 flex-1">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className={`h-3 bg-slate-100 rounded ${i === 5 ? 'w-2/3' : 'w-full'}`} />
          ))}
        </div>
      </div>
    )
  }

  if (!ticket) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-8">
        <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5" />
          </svg>
        </div>
        <p className="text-slate-500 font-medium mb-1">Select a ticket</p>
        <p className="text-slate-400 text-sm">Click any ticket in the queue to view details and the AI-drafted response.</p>
      </div>
    )
  }

  const statusLabel = {
    new: 'New', draft_ready: 'Draft Ready', approved: 'Approved',
    edited_sent: 'Edited & Sent', rejected: 'Rejected',
  }[ticket.status] || ticket.status

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-200 flex-shrink-0">
        <div className="flex items-start gap-3 mb-3">
          <Avatar name={ticket.customer_name} />
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-slate-800">{ticket.customer_name}</div>
            <a
              href={`mailto:${ticket.customer_email}`}
              className="text-sm text-violet-600 hover:text-violet-700 hover:underline truncate block"
            >
              {ticket.customer_email}
            </a>
          </div>
          <span className="text-xs text-slate-400 flex-shrink-0">{ticket.id}</span>
        </div>

        {/* Subject */}
        <h2 className="text-base font-semibold text-slate-900 leading-snug mb-3">
          {ticket.subject}
        </h2>

        {/* Meta badges */}
        <div className="flex flex-wrap gap-2">
          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${PRIORITY_BADGE[ticket.priority]}`}>
            {ticket.priority} priority
          </span>
          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_BADGE[ticket.status]}`}>
            {statusLabel}
          </span>
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
            {formatDate(ticket.created_at)}
          </span>
        </div>
      </div>

      {/* Message body */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        <div className="flex items-center gap-2 mb-3">
          <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Customer Message</span>
        </div>
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
          <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
            {ticket.message}
          </p>
        </div>

        {/* Ticket ID footer */}
        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-400">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
          </svg>
          <span>Ticket ID: {ticket.id}</span>
        </div>
      </div>
    </div>
  )
}
