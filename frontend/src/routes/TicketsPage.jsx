import { useState, useEffect, useCallback } from "react";
import TicketQueue from "../components/TicketQueue";
import TicketDetail from "../components/TicketDetail";
import DraftReviewPanel from "../components/DraftReviewPanel";
import NewTicketModal from "../components/NewTicketModal";
import { listTickets, getTicket } from "../api";
import { getUser } from "../auth";

export default function TicketsPage() {
  const [tickets, setTickets] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const user = getUser();

  const fetchTickets = useCallback(async () => {
    try {
      const data = await listTickets();
      setTickets(data);
    } catch (err) {
      console.error("Failed to fetch tickets:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTickets();
    const interval = setInterval(fetchTickets, 8000);
    return () => clearInterval(interval);
  }, [fetchTickets]);

  async function handleSelect(id) {
    setSelectedId(id);
    setDetailLoading(true);
    try {
      const ticket = await getTicket(id);
      setSelectedTicket(ticket);
    } catch (err) {
      console.error("Failed to fetch ticket:", err);
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleAction() {
    await fetchTickets();
    if (selectedId) {
      const refreshed = await getTicket(selectedId);
      setSelectedTicket(refreshed);
    }
  }

  function handleNext() {
    const idx = tickets.findIndex((t) => t.id === selectedId);
    const next = tickets[idx + 1];
    if (next) handleSelect(next.id);
  }

  return (
    <div className="flex h-[calc(100vh-48px)] -m-6 overflow-hidden">
      {/* Left: queue */}
      <div className="w-80 border-r border-slate-200 flex flex-col flex-shrink-0 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-white">
          <span className="text-xs text-slate-500">{user?.full_name}</span>
          <button
            onClick={() => setShowModal(true)}
            className="text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-md font-medium transition-colors"
          >
            + New ticket
          </button>
        </div>
        <div className="flex-1 overflow-hidden">
          <TicketQueue
            tickets={tickets}
            selectedId={selectedId}
            onSelect={handleSelect}
            loading={loading}
          />
        </div>
      </div>

      {/* Middle: ticket detail */}
      <div className="w-96 border-r border-slate-200 flex-shrink-0 overflow-y-auto bg-white">
        {selectedTicket ? (
          <TicketDetail ticket={selectedTicket} loading={detailLoading} />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-400 text-sm">
            Select a ticket to view details
          </div>
        )}
      </div>

      {/* Right: draft review */}
      <div className="flex-1 overflow-y-auto bg-slate-50">
        {selectedTicket?.status === "draft_ready" ? (
          <DraftReviewPanel
            ticket={selectedTicket}
            onAction={handleAction}
            onNext={handleNext}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-400 text-sm">
            {selectedTicket
              ? selectedTicket.status === "processing" || selectedTicket.status === "new"
                ? "AI is processing this ticket…"
                : `Ticket is ${selectedTicket.status}`
              : "No ticket selected"}
          </div>
        )}
      </div>

      {showModal && (
        <NewTicketModal
          onClose={() => setShowModal(false)}
          onCreated={(ticket) => {
            setShowModal(false);
            fetchTickets();
            handleSelect(ticket.id);
          }}
        />
      )}
    </div>
  );
}
