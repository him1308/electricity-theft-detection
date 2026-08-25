import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";
import ConsumerDetails from "./pages/ConsumerDetails";
import Consumers from "./pages/Consumers";
import DataManagement from "./pages/DataManagement";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import ModelPerformance from "./pages/ModelPerformance";
import SystemSettings from "./pages/SystemSettings";
import UploadData from "./pages/UploadData";
import UserManagement from "./pages/UserManagement";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="consumers" element={<Consumers />} />
        <Route path="consumers/:consumerId" element={<ConsumerDetails />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="model" element={<ModelPerformance />} />
        <Route path="upload" element={<UploadData />} />
        <Route
          path="admin/users"
          element={
            <RequireAuth roles={["Admin"]}>
              <UserManagement />
            </RequireAuth>
          }
        />
        <Route
          path="admin/data"
          element={
            <RequireAuth roles={["Admin"]}>
              <DataManagement />
            </RequireAuth>
          }
        />
        <Route
          path="admin/settings"
          element={
            <RequireAuth roles={["Admin"]}>
              <SystemSettings />
            </RequireAuth>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
