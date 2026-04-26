import React, { useState, useEffect, useRef } from 'react'
import KBCitations from './KBCitations.jsx'
import { approveTicket, editSendTicket, rejectTicket } from '../api.js'

const CATEGORY_STYLES = {
  billing: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
  technical: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
  refund: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-200' },
  other: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
}

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100)
  const color = pct >= 80 ? 'bg-emerald-500' : pct >= 60 ? 'bg-amber-400' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-semibold text-slate-600 tabular-nums w-8">{pct}%</span>
    </div>
  )
}

// Render inline citation tags [chunk_id] as styled pills
function CitedText({ text }) {
  if (!text) return null
  const parts = text.split(/(\[[^\]]+\])/g)
  return (
    <>
      {parts.map((part, i) => {
        if (/^\[[^\]]+\]$/.test(part)) {
          const id = part.slice(1, -1)
          return (
            <span
              key={i}
              className="inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded text-xs font-mono bg-violet-100 text-violet-700 border border-violet-200 leading-none align-baseline cursor-default"
              title={`Citation: ${id}`}
            >
              {id.length > 20 ? id.slice(0, 20) + '…' : id}
            </span>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </>
  )
}

function Toast({ message, type, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 3000)
    return () => clearTimeout(t)
  }, [onDismiss])

  const styles = {
    success: 'bg-emerald-600',
    error: 'bg-red-600',
    info: 'bg-violet-600',
  }

  return (
    <div className={`fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-xl text-white text-sm font-medium shadow-lg animate-fade-in ${styles[type]}`}>
      {type === 'success' && (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      )}
      {type === 'error' && (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
        </svg>
      )}
      {message}
      <button onClick={onDismiss} className="ml-2 opacity-70 hover:opacity-100">×</button>
    </div>
  )
}

export default function DraftReviewPanel({ ticket, onAction, onNext }) {
  const [draftText, setDraftText] = useState('')
  const [originalDraft, setOriginalDraft] = useState('')
  const [citationsCollapsed, setCitationsCollapsed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)
  const textareaRef = useRef(null)

  const draft = ticket?.draft
  const classification = ticket?.classification
  const citations = ticket?.citations || []

  // Reset draft text whenever ticket changes
  useEffect(() => {
    if (draft?.response_text) {
      setDraftText(draft.response_text)
      setOriginalDraft(draft.response_text)
    } else {
      setDraftText('')
      setOriginalDraft('')
    }
  }, [ticket?.id, draft?.response_text])

  const isModified = draftText !== originalDraft && draftText.trim() !== ''

  const showToast = (message, type = 'success') => setToast({ message, type })

  async function handleApprove() {
    setLoading(true)
    try {
      await approveTicket(ticket.id)
      showToast('Response approved and sent!', 'success')
      onAction(ticket.id, 'approved')
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  async function handleEditSend() {
    setLoading(true)
    try {
      await editSendTicket(ticket.id, draftText)
      showToast('Edited response sent! This will improve future drafts.', 'success')
      onAction(ticket.id, 'edited_sent')
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  async function handleReject() {
    setLoading(true)
    try {
      await rejectTicket(ticket.id, 'Rejected by agent')
      showToast('Ticket escalated to human handling', 'info')
      onAction(ticket.id, 'rejected')
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const isDecided = ['approved', 'edited_sent', 'rejected'].includes(ticket?.status)

  if (!ticket) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-slate-400 text-sm">Select a ticket to review</p>
      </div>
    )
  }

  if (ticket.status === 'new') {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 px-6">
        <div className="w-14 h-14 rounded-full bg-violet-100 flex items-center justify-center">
          <svg className="w-7 h-7 text-violet-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <div className="text-center">
          <p className="font-medium text-slate-700 mb-1">AI drafting response…</p>
          <p className="text-xs text-slate-400">The multi-agent pipeline is classifying and drafting a response for this ticket.</p>
        </div>
      </div>
    )
  }

  if (!draft) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 px-6">
        <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <p className="text-slate-600 text-sm text-center">No draft available for this ticket.</p>
      </div>
    )
  }

  const catStyle = CATEGORY_STYLES[classification?.category] || CATEGORY_STYLES.other

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">

        {/* Classification Card */}
        {classification && (
          <div className={`rounded-xl border p-4 ${catStyle.bg} ${catStyle.border}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">Classification</span>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold capitalize ${catStyle.bg} ${catStyle.text}`}>
                {classification.category}
              </span>
            </div>
            <ConfidenceBar value={classification.confidence} />
            {classification.reasoning && (
              <p className="text-xs text-slate-600 mt-2 leading-relaxed italic">
                "{classification.reasoning}"
              </p>
            )}
          </div>
        )}

        {/* KB Citations */}
        {citations.length > 0 && (
          <KBCitations
            citations={citations}
            collapsed={citationsCollapsed}
            onToggle={() => setCitationsCollapsed(!citationsCollapsed)}
          />
        )}

        {/* Suggested Action */}
        {draft.suggested_action && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>AI suggests: <strong className="text-slate-700 capitalize">{draft.suggested_action.replace('_', ' ')}</strong></span>
            {draft.tone_notes && <span className="text-slate-400">· {draft.tone_notes}</span>}
          </div>
        )}

        {/* Draft Response Editor */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">Drafted Response</span>
              {isModified && (
                <span className="px-1.5 py-0.5 bg-blue-100 text-blue-600 text-xs rounded font-medium">
                  Modified
                </span>
              )}
            </div>
            <span className="text-xs text-slate-400 tabular-nums">{draftText.length} chars</span>
          </div>

          {isDecided ? (
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                <CitedText text={draftText} />
              </p>
            </div>
          ) : (
            <textarea
              ref={textareaRef}
              value={draftText}
              onChange={e => setDraftText(e.target.value)}
              disabled={loading}
              rows={8}
              className="w-full resize-none rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-800 leading-relaxed focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-shadow disabled:opacity-60 placeholder:text-slate-400"
              placeholder="Draft response…"
            />
          )}
        </div>

        {/* Decided banner */}
        {isDecided && (
          <div className={`flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium ${
            ticket.status === 'approved' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
            ticket.status === 'edited_sent' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
            'bg-red-50 text-red-600 border border-red-200'
          }`}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {ticket.status === 'approved' && 'Response approved and sent'}
            {ticket.status === 'edited_sent' && 'Edited response sent — saved as few-shot example'}
            {ticket.status === 'rejected' && 'Escalated to human handling'}
          </div>
        )}
      </div>

      {/* Action buttons — sticky footer */}
      {!isDecided && (
        <div className="flex-shrink-0 border-t border-slate-200 bg-white px-5 py-4">
          <div className="flex gap-2.5">
            {/* Approve */}
            <button
              onClick={handleApprove}
              disabled={loading || isModified}
              className={`
                flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150
                ${!isModified
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm hover:shadow'
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                }
              `}
              title={isModified ? 'Undo edits to approve original draft' : 'Approve & send original draft'}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
              Approve
            </button>

            {/* Edit & Send */}
            <button
              onClick={handleEditSend}
              disabled={loading || !isModified}
              className={`
                flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-150
                ${isModified
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow'
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                }
              `}
              title={!isModified ? 'Edit the draft to enable this button' : 'Send edited response and save as example'}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Edit & Send
            </button>

            {/* Reject */}
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-red-600 border-2 border-red-200 hover:bg-red-50 transition-all duration-150 disabled:opacity-50"
              title="Reject and escalate to human agent"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              Escalate
            </button>
          </div>

          {/* Helper text */}
          <p className="text-xs text-slate-400 text-center mt-2.5">
            {isModified
              ? 'Your edit will be saved as a few-shot example to improve future drafts'
              : 'Approve sends the original AI draft · Edit the text above to enable Edit & Send'}
          </p>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onDismiss={() => setToast(null)}
        />
      )}
    </div>
  )
}
