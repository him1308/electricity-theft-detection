import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";
import ConsumerDetails from "./pages/ConsumerDetails";
import Consumers from "./pages/Consumers";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import ModelPerformance from "./pages/ModelPerformance";
import UploadData from "./pages/UploadData";

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
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
