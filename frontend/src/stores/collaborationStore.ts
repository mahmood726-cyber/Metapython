/**
 * Collaboration Store (Zustand)
 * Manages real-time collaboration state
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { io, Socket } from 'socket.io-client';

interface User {
  user_id: string;
  name: string;
  color: string;
  cursor_position?: { x: number; y: number };
}

interface ChatMessage {
  user: string;
  message: string;
  timestamp: string;
}

interface CollaborationState {
  // WebSocket connection
  socket: Socket | null;
  isConnected: boolean;
  initializeSocket: () => void;
  disconnectSocket: () => void;

  // Session
  sessionId: string | null;
  users: User[];
  currentUserId: string | null;

  // Chat
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;

  // Collaborative editing
  sharedCursor: { [userId: string]: { x: number; y: number } };
  updateCursor: (userId: string, x: number, y: number) => void;

  // Actions
  joinSession: (sessionId: string, userName: string) => void;
  leaveSession: () => void;
  sendMessage: (message: string) => void;
  broadcastAnalysisUpdate: (data: any) => void;
}

export const useCollaborationStore = create<CollaborationState>()(
  devtools(
    (set, get) => ({
      socket: null,
      isConnected: false,

      initializeSocket: () => {
        const wsUrl = import.meta.env.VITE_WS_URL || 'http://localhost:8000';
        const socket = io(wsUrl, {
          transports: ['websocket'],
        });

        socket.on('connect', () => {
          console.log('WebSocket connected');
          set({ isConnected: true });
        });

        socket.on('disconnect', () => {
          console.log('WebSocket disconnected');
          set({ isConnected: false });
        });

        socket.on('user_joined', (user: User) => {
          set((state) => ({
            users: [...state.users, user],
          }));
        });

        socket.on('user_left', (userId: string) => {
          set((state) => ({
            users: state.users.filter((u) => u.user_id !== userId),
          }));
        });

        socket.on('chat_message', (message: ChatMessage) => {
          set((state) => ({
            messages: [...state.messages, message],
          }));
        });

        socket.on('cursor_update', ({ userId, x, y }) => {
          set((state) => ({
            sharedCursor: {
              ...state.sharedCursor,
              [userId]: { x, y },
            },
          }));
        });

        socket.on('analysis_update', (data: any) => {
          // Broadcast analysis updates to other components
          window.dispatchEvent(
            new CustomEvent('collaboration:analysis_update', {
              detail: data,
            })
          );
        });

        set({ socket });
      },

      disconnectSocket: () => {
        const { socket } = get();
        if (socket) {
          socket.disconnect();
          set({ socket: null, isConnected: false });
        }
      },

      sessionId: null,
      users: [],
      currentUserId: null,
      messages: [],
      sharedCursor: {},

      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      updateCursor: (userId, x, y) =>
        set((state) => ({
          sharedCursor: {
            ...state.sharedCursor,
            [userId]: { x, y },
          },
        })),

      joinSession: (sessionId, userName) => {
        const { socket } = get();
        if (socket && socket.connected) {
          const userId = `user-${Date.now()}-${Math.random()}`;
          socket.emit('join_session', { sessionId, userId, userName });
          set({ sessionId, currentUserId: userId });
        }
      },

      leaveSession: () => {
        const { socket, sessionId } = get();
        if (socket && sessionId) {
          socket.emit('leave_session', { sessionId });
          set({ sessionId: null, users: [], messages: [] });
        }
      },

      sendMessage: (message) => {
        const { socket, sessionId, currentUserId } = get();
        if (socket && sessionId) {
          const chatMessage: ChatMessage = {
            user: currentUserId || 'Anonymous',
            message,
            timestamp: new Date().toISOString(),
          };
          socket.emit('chat_message', { sessionId, ...chatMessage });
          set((state) => ({
            messages: [...state.messages, chatMessage],
          }));
        }
      },

      broadcastAnalysisUpdate: (data) => {
        const { socket, sessionId } = get();
        if (socket && sessionId) {
          socket.emit('analysis_update', { sessionId, data });
        }
      },
    }),
    { name: 'CollaborationStore' }
  )
);
