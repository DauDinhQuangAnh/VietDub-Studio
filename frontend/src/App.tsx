import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "./auth/AuthContext";
import GlobalLoadingBar from "./components/GlobalLoadingBar";
import Admin from "./pages/Admin";
import Downloader from "./pages/Downloader";
import Editor from "./pages/Editor";
import JobDetail from "./pages/JobDetail";
import NewJob from "./pages/NewJob";
import Studio from "./pages/Studio";
import Voices from "./pages/Voices";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <GlobalLoadingBar />
        <Routes>
          {/* Vào thẳng Studio chính của tool cá nhân */}
          <Route path="/" element={<Studio />} />
          <Route path="/studio" element={<Studio />} />
          <Route path="/studio/new" element={<NewJob />} />
          <Route path="/studio/jobs/:id" element={<JobDetail />} />
          <Route path="/studio/jobs/:id/edit" element={<Editor />} />
          <Route path="/voices" element={<Voices />} />
          <Route path="/downloader" element={<Downloader />} />
          <Route path="/admin" element={<Admin />} />

          {/* Bỏ trang đăng nhập/đăng ký - chuyển hướng về trang chủ */}
          <Route path="/login" element={<Navigate to="/" replace />} />
          <Route path="/register" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
