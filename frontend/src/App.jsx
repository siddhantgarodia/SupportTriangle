import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { getUser } from "./auth";
import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./routes/LoginPage";
import TicketsPage from "./routes/TicketsPage";
import AnalyticsPage from "./routes/AnalyticsPage";
import PersonasPage from "./routes/PersonasPage";
import UsersPage from "./routes/UsersPage";

export default function App() {
  const user = getUser();
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route index element={<Navigate to="/tickets" replace />} />
            <Route path="/tickets" element={<TicketsPage />} />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute roles={["senior", "admin"]}>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/personas"
              element={
                <ProtectedRoute roles={["senior", "admin"]}>
                  <PersonasPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute roles={["admin"]}>
                  <UsersPage />
                </ProtectedRoute>
              }
            />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/tickets" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
