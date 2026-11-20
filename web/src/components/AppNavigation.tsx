import { useState } from "react";
import { Link } from "react-router-dom";

import ExecutionModeToggle, { type ExecutionMode } from "./ExecutionModeToggle";

export default function AppNavigation() {
  const [executionMode, setExecutionMode] = useState<ExecutionMode>(() => {
    return (localStorage.getItem("vietdub_execution_mode") as ExecutionMode) || "CLOUD_FREE_API";
  });

  const handleModeChange = (newMode: ExecutionMode) => {
    setExecutionMode(newMode);
    localStorage.setItem("vietdub_execution_mode", newMode);
    window.dispatchEvent(new CustomEvent("vietdub_mode_change", { detail: newMode }));
  };

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-cream/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-lg font-bold">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
              V
            </span>
            VietDub<span className="text-primary">Studio</span>
          </Link>
          <ExecutionModeToggle mode={executionMode} onChange={handleModeChange} compact={true} />
        </div>
        <nav className="flex items-center gap-2 sm:gap-3">
          <Link to="/" className="btn-ghost text-sm font-medium">
            Bảng điều khiển
          </Link>
          <Link to="/downloader" className="btn-ghost text-sm font-medium">
            📥 Tải video
          </Link>
          <Link to="/voices" className="btn-ghost text-sm font-medium">
            Thư viện giọng nói
          </Link>
          <Link to="/admin" className="btn-ghost text-sm font-medium">
            Cài đặt
          </Link>
          <Link to="/studio/new" className="btn-primary text-sm">
            + Tạo video mới
          </Link>
        </nav>
      </div>
    </header>
  );
}
