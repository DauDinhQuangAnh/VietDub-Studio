import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import LoadingIndicator from "./components/LoadingIndicator";
import LocalSettings from "./pages/LocalSettings";
import MediaDownloader from "./pages/MediaDownloader";
import SubtitleEditor from "./pages/SubtitleEditor";
import JobWorkspace from "./pages/JobWorkspace";
import CreateJob from "./pages/CreateJob";
import JobDashboard from "./pages/JobDashboard";
import VoiceLibrary from "./pages/VoiceLibrary";

export default function StudioApp() {
  return (
    <BrowserRouter>
        <LoadingIndicator />
        <Routes>
          {/* Vào thẳng Studio chính của tool cá nhân */}
          <Route path="/" element={<JobDashboard />} />
          <Route path="/studio" element={<JobDashboard />} />
          <Route path="/studio/new" element={<CreateJob />} />
          <Route path="/studio/jobs/:id" element={<JobWorkspace />} />
          <Route path="/studio/jobs/:id/edit" element={<SubtitleEditor />} />
          <Route path="/voices" element={<VoiceLibrary />} />
          <Route path="/downloader" element={<MediaDownloader />} />
          <Route path="/admin" element={<LocalSettings />} />

          <Route path="/login" element={<Navigate to="/" replace />} />
          <Route path="/register" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    </BrowserRouter>
  );
}
