import { io, Socket } from 'socket.io-client';
import api from '@/lib/api';

interface ChatMessage {
  id: string;
  sender_id: string;
  receiver_id?: string;
  sender_name: string;
  message: string;
  timestamp: string;
  is_mine: boolean;
}

interface User {
  id: string;
  supabase_id?: string;
  name: string;
  email?: string;
  specialty?: string;
  status: 'online' | 'offline';
}

interface MessageCallback {
  (message: ChatMessage): void;
}

interface UserStatusCallback {
  (userId: string, status: 'online' | 'offline'): void;
}

interface ConnectionStatusCallback {
  (connected: boolean): void;
}

interface TypingCallback {
  (userId: string, isTyping: boolean): void;
}

interface UnreadMessageCallback {
  (data: { sender_id: string; sender_name: string; message_preview: string; timestamp: string }): void;
}

class ChatService {
  private socket: Socket | null = null;
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  private messageCallbacks: MessageCallback[] = [];
  private userStatusCallbacks: UserStatusCallback[] = [];
  private connectionStatusCallbacks: ConnectionStatusCallback[] = [];
  private typingCallbacks: TypingCallback[] = [];
  private unreadMessageCallbacks: UnreadMessageCallback[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private isConnecting = false;
  private typingTimer: NodeJS.Timeout | null = null;
  private connectPromise: Promise<void> | null = null;

  connect(): Promise<void> {
    // Si ya tenemos una promesa de conexión en curso, la retornamos
    if (this.connectPromise) {
      return this.connectPromise;
    }

    this.connectPromise = new Promise((resolve) => {
      if (this.socket?.connected) {
        console.log('Socket already connected');
        resolve();
        return;
      }

      if (this.isConnecting) {
        console.log('Already connecting...');
        resolve();
        return;
      }

      this.isConnecting = true;
      console.log('Attempting to connect to Socket.IO server...');
      
      this.socket = io(this.baseUrl, {
        withCredentials: true,
        transports: ['polling', 'websocket'],
        timeout: 20000,
        reconnection: true,
        reconnectionAttempts: 3,
        reconnectionDelay: 2000,
        reconnectionDelayMax: 10000,
        forceNew: false,
        autoConnect: true,
        upgrade: true,
        rememberUpgrade: false
      });

      this.socket.on('connect', () => {
        console.log('✅ Socket.IO connected successfully');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.connectionStatusCallbacks.forEach(callback => callback(true));
        resolve();
      });

      this.socket.on('connect_error', (error: any) => {
        console.error('❌ Socket.IO connection error:', error);
        this.isConnecting = false;
        this.connectionStatusCallbacks.forEach(callback => callback(false));
        
        // Solo intentar reconectar automáticamente en errores de red
        if (error.message && !error.message.includes('xhr poll error')) {
          setTimeout(() => {
            if (!this.socket?.connected && !this.isConnecting) {
              this.attemptReconnect();
            }
          }, 2000);
        }
      });

      this.socket.on('disconnect', (reason: string) => {
        console.log('🔌 Socket.IO disconnected:', reason);
        this.isConnecting = false;
        this.connectionStatusCallbacks.forEach(callback => callback(false));
        
        // Auto-reconectar solo si no fue una desconexión intencional
        if (reason !== 'io client disconnect' && reason !== 'io server disconnect') {
          setTimeout(() => {
            if (!this.socket?.connected && !this.isConnecting) {
              this.attemptReconnect();
            }
          }, 2000);
        }
      });

      // Timeout más generoso para permitir la conexión
      setTimeout(() => {
        this.isConnecting = false;
        if (!this.socket?.connected) {
          console.log('⚠️ Socket.IO connection timeout, falling back to HTTP');
          this.connectionStatusCallbacks.forEach(callback => callback(false));
        }
        resolve();
      }, 15000);

      this.socket.on('new_message', (message: ChatMessage) => {
        console.log('📨 New message received:', message);
        // Mostrar notificación de nuevo mensaje
        this.showNotification(message);
        this.messageCallbacks.forEach(callback => callback(message));
      });

      this.socket.on('message_sent', (message: any) => {
        console.log('✅ Message sent confirmation:', message);
      });

      this.socket.on('user_status', (data: { user_id: string; status: 'online' | 'offline' }) => {
        console.log('👤 User status change:', data);
        this.userStatusCallbacks.forEach(callback => callback(data.user_id, data.status));
      });

      this.socket.on('user_typing', (data: { user_id: string; is_typing: boolean }) => {
        console.log('⌨️ User typing:', data);
        this.typingCallbacks.forEach(callback => callback(data.user_id, data.is_typing));
      });

      this.socket.on('unread_message', (data: { sender_id: string; sender_name: string; message_preview: string; timestamp: string }) => {
        console.log('🔔 Unread message notification:', data);
        this.unreadMessageCallbacks.forEach(callback => callback(data));
      });

      this.socket.on('message_error', (error: { error: string }) => {
        console.error('❌ Message error:', error.error);
      });
    });

    return this.connectPromise;
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    setTimeout(() => {
      if (!this.socket?.connected && !this.isConnecting) {
        this.connectPromise = null; // Reset promise
        this.connect();
      }
    }, delay);
  }

  private showNotification(message: ChatMessage): void {
    // Solo mostrar notificación si el usuario no está en la página del chat
    if ('Notification' in window && Notification.permission === 'granted') {
      if (document.hidden) {
        new Notification(`Nuevo mensaje de ${message.sender_name}`, {
          body: message.message,
          icon: '/favicon.ico',
          tag: 'chat-message'
        });
      }
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.reconnectAttempts = 0;
    this.isConnecting = false;
    this.connectPromise = null; // Reset promise
    this.connectionStatusCallbacks.forEach(callback => callback(false));
  }

  isSocketConnected(): boolean {
    return this.socket?.connected || false;
  }

  sendMessage(receiverId: string, message: string): void {
    if (!this.socket?.connected) {
      this.sendMessageHttp(receiverId, message).catch(error => {
        console.error('Error enviando mensaje por HTTP:', error);
      });
      return;
    }

    this.socket.emit('send_message', {
      receiver_id: receiverId,
      message: message
    });
  }

  sendTypingIndicator(receiverId: string, isTyping: boolean): void {
    if (this.socket?.connected) {
      this.socket.emit('typing', {
        receiver_id: receiverId,
        is_typing: isTyping
      });
    }
  }

  startTyping(receiverId: string): void {
    this.sendTypingIndicator(receiverId, true);
    
    // Limpiar timer anterior si existe
    if (this.typingTimer) {
      clearTimeout(this.typingTimer);
    }
    
    // Enviar "stop typing" después de 3 segundos
    this.typingTimer = setTimeout(() => {
      this.sendTypingIndicator(receiverId, false);
    }, 3000);
  }

  stopTyping(receiverId: string): void {
    if (this.typingTimer) {
      clearTimeout(this.typingTimer);
      this.typingTimer = null;
    }
    this.sendTypingIndicator(receiverId, false);
  }

  async sendMessageHttp(receiverId: string, message: string): Promise<ChatMessage> {
    try {
      const response = await api.post('/send-message', {
        receiver_id: receiverId,
        message: message
      });
      
      const messageData: ChatMessage = {
        id: response.data.id.toString(),
        sender_id: response.data.sender_id.toString(),
        receiver_id: response.data.receiver_id.toString(),
        sender_name: 'Tú',
        message: response.data.message,
        timestamp: response.data.timestamp,
        is_mine: true
      };
      
      // Notificar a los callbacks
      this.messageCallbacks.forEach(callback => callback(messageData));
      
      return messageData;
    } catch (error) {
      throw error;
    }
  }

  onMessage(callback: MessageCallback): () => void {
    this.messageCallbacks.push(callback);
    
    return () => {
      const index = this.messageCallbacks.indexOf(callback);
      if (index > -1) {
        this.messageCallbacks.splice(index, 1);
      }
    };
  }

  onUserStatusChange(callback: UserStatusCallback): () => void {
    this.userStatusCallbacks.push(callback);
    
    return () => {
      const index = this.userStatusCallbacks.indexOf(callback);
      if (index > -1) {
        this.userStatusCallbacks.splice(index, 1);
      }
    };
  }

  onConnectionStatus(callback: ConnectionStatusCallback): () => void {
    this.connectionStatusCallbacks.push(callback);
    
    return () => {
      const index = this.connectionStatusCallbacks.indexOf(callback);
      if (index > -1) {
        this.connectionStatusCallbacks.splice(index, 1);
      }
    };
  }

  onTyping(callback: TypingCallback): () => void {
    this.typingCallbacks.push(callback);
    
    return () => {
      const index = this.typingCallbacks.indexOf(callback);
      if (index > -1) {
        this.typingCallbacks.splice(index, 1);
      }
    };
  }

  onUnreadMessage(callback: UnreadMessageCallback): () => void {
    this.unreadMessageCallbacks.push(callback);
    
    return () => {
      const index = this.unreadMessageCallbacks.indexOf(callback);
      if (index > -1) {
        this.unreadMessageCallbacks.splice(index, 1);
      }
    };
  }

  requestNotificationPermission(): void {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  async getMessages(receiverId: string): Promise<ChatMessage[]> {
    try {
      // Usar la nueva ruta que maneja UUIDs
      const response = await api.get(`/get-messages-uuid/${receiverId}`);
      return response.data.messages || [];
    } catch (error) {
      throw error;
    }
  }

  async getUsers(): Promise<User[]> {
    try {
      const response = await api.get('/get-chat-doctors');
      const data = response.data;
      return data.doctors?.map((doctor: any) => ({
        id: doctor.id.toString(),
        supabase_id: doctor.supabase_id,
        name: `${doctor.firstName} ${doctor.lastName1}`,
        email: doctor.email,
        specialty: doctor.speciality,
        status: 'offline' as const
      })) || [];
    } catch (error) {
      return [
        {
          id: '1',
          supabase_id: crypto.randomUUID(),  // Generar UUID real
          name: 'Dr. Juan Pérez',
          email: 'juan.perez@hospital.com',
          specialty: 'Cardiología',
          status: 'online' as const
        },
        {
          id: '2',
          supabase_id: crypto.randomUUID(),  // Generar UUID real
          name: 'Dra. María González',
          email: 'maria.gonzalez@hospital.com',
          specialty: 'Neurología',
          status: 'offline' as const
        },
        {
          id: '3',
          supabase_id: crypto.randomUUID(),  // Generar UUID real
          name: 'Dr. Carlos López',
          email: 'carlos.lopez@hospital.com',
          specialty: 'Pediatría',
          status: 'offline' as const
        }
      ];
    }
  }

  async getUnreadCounts(): Promise<{ [userId: string]: number }> {
    try {
      const response = await api.get('/get-unread-counts');
      const data = response.data;
      return data.unread_counts || {};
    } catch (error) {
      return {};
    }
  }
}

export const chatService = new ChatService();
export type { ChatMessage, User, ConnectionStatusCallback, TypingCallback, UnreadMessageCallback };
