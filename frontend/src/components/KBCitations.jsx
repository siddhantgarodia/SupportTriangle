import React, { useState } from 'react'

const NS_STYLES = {
  billing: 'bg-blue-100 text-blue-700 border-blue-200',
  technical: 'bg-purple-100 text-purple-700 border-purple-200',
  refund: 'bg-orange-100 text-orange-700 border-orange-200',
  other: 'bg-slate-100 text-slate-600 border-slate-200',
}

function CitationCard({ citation }) {
  const [expanded, setExpanded] = useState(false)
  const nsStyle = NS_STYLES[citation.namespace] || NS_STYLES.other
  const preview = citation.content.slice(0, 200)
  const hasMore = citation.content.length > 200

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white transition-shadow hover:shadow-sm">
      <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 border-b border-slate-200">
        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-semibold border ${nsStyle}`}>
          {citation.chunk_id.slice(0, 24)}{citation.chunk_id.length > 24 ? '…' : ''}
        </span>
        <span className="text-xs text-slate-500 flex items-center gap-1 ml-auto">
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {citation.source_file}
        </span>
      </div>
      <div className="px-3 py-2.5">
        <p className="text-xs text-slate-600 leading-relaxed">
          {expanded ? citation.content : preview}
          {hasMore && !expanded && '…'}
        </p>
        {hasMore && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-1.5 text-xs text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1"
          >
            {expanded ? (
              <>Show less <span className="rotate-180 inline-block">▾</span></>
            ) : (
              <>Show more <span>▾</span></>
            )}
          </button>
        )}
      </div>
    </div>
  )
}

export default function KBCitations({ citations, collapsed, onToggle }) {
  if (!citations || citations.length === 0) return null

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors border-b border-slate-200"
      >
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span className="text-sm font-semibold text-slate-700">KB Citations</span>
          <span className="bg-violet-100 text-violet-700 text-xs px-2 py-0.5 rounded-full font-medium">
            {citations.length}
          </span>
        </div>
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${collapsed ? '' : 'rotate-180'}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {!collapsed && (
        <div className="p-3 space-y-2 bg-white">
          {citations.map((c, i) => (
            <CitationCard key={`${c.chunk_id}-${i}`} citation={c} />
          ))}
        </div>
      )}
    </div>
  )
}
