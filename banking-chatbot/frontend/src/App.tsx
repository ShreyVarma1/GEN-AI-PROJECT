import React, { useState } from "react";
import { useChat } from "./hooks/useChat";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import UploadPanel from "./components/UploadPanel";

export default function App() {
  const {
    messages,
    isLoading,
    error,
    sessionId,
    sessions,
    sendMessage,
    newChat,
    selectSession,
    renameSession,
    deleteSession,
  } = useChat();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadPanelOpen, setUploadPanelOpen] = useState(false);

  const handleNewChat = () => {
    newChat();
    setSidebarOpen(false);
  };

  const handleSelectSession = (id: string) => {
    selectSession(id);
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-navy-900">
      {/* Sidebar — always visible on desktop, slide-in on mobile */}
      <Sidebar
        sessions={sessions}
        currentSessionId={sessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onRenameSession={renameSession}
        onDeleteSession={deleteSession}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main chat area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSend={sendMessage}
          onUploadClick={() => setUploadPanelOpen(true)}
          onMenuClick={() => setSidebarOpen(true)}
        />
      </main>

      {/* Upload panel */}
      <UploadPanel
        isOpen={uploadPanelOpen}
        onClose={() => setUploadPanelOpen(false)}
      />
    </div>
  );
}
