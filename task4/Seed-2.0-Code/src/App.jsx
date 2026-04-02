import { Routes, Route } from "react-router-dom";
import AppLayout from "./layout/AppLayout";
import Overview from "./pages/Overview";
import DataPage from "./pages/DataPage";
import TasksPage from "./pages/TasksPage";
import MonitorPage from "./pages/MonitorPage";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Overview />} />
        <Route path="data" element={<DataPage />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="monitor" element={<MonitorPage />} />
        <Route path="results" element={<ResultsPage />} />
      </Route>
    </Routes>
  );
}
