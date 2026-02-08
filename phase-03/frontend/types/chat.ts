// UI state for floating launcher wrapper (separate from ChatKit state)
export interface ChatUIState {
  isOpen: boolean;        // Whether chat interface is open
  isMinimized: boolean;   // Whether chat interface is minimized
}

// Context value for launcher wrapper
export interface ChatUIContextValue {
  uiState: ChatUIState;
  openChat: () => void;
  closeChat: () => void;
  minimizeChat: () => void;
  toggleChat: () => void;
}
