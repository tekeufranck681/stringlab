import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard";

import MainLayout from "../components/layout/MainLayout";

import AlgorithmRunner from "../pages/AlgorithmRunner";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />

        <Route path="/algorithm/:algorithmId" element={<AlgorithmRunner />} />
      </Route>
    </Routes>
  );
}
