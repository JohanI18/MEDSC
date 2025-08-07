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

class ChatService {
  private socket: Socket | null = null;
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  private messageCallbacks: MessageCallback[] = [];
  private userStatusCallbacks: UserStatusCallback[] = [];

  connect(): Promise<void> {
    return new Promise((resolve) => {
      if (this.socket?.connected) {
        console.log('Socket already connected');
        resolve();
        return;
      }

      console.log('Attempting to connect to:', this.baseUrl);
      
      this.socket = io(this.baseUrl, {
        withCredentials: true,
        transports: ['websocket', 'polling'],
        timeout: 5000,
        forceNew: true
      });

      let connected = false;

      this.socket.on('connect', () => {
        console.log('✅ Connected to chat server successfully');
        connected = true;
        resolve();
      });

      this.socket.on('connect_error', (error: any) => {
        console.error('❌ WebSocket connection error:', error);
        console.log('Will use HTTP fallback for messaging');
      });

      // Timeout después de 6 segundos - siempre resolver para permitir HTTP fallback
      setTimeout(() => {
        if (!connected) {
          console.warn('WebSocket connection timeout, continuing with HTTP fallback');
        }
        resolve();
      }, 6000);

      this.socket.on('disconnect', (reason: string) => {
        console.warn('🔌 WebSocket disconnected:', reason);
      });

      this.socket.on('new_message', (message: ChatMessage) => {
        console.log('📨 New message received:', message);
        this.messageCallbacks.forEach(callback => callback(message));
      });

      this.socket.on('message_sent', (message: any) => {
        console.log('✅ Message sent successfully via WebSocket:', message);
      });

      this.socket.on('user_status', (data: { user_id: string; status: 'online' | 'offline' }) => {
        console.log('👤 User status change:', data);
        this.userStatusCallbacks.forEach(callback => callback(data.user_id, data.status));
      });

      this.socket.on('message_error', (error: { error: string }) => {
        console.error('❌ Message error from server:', error);
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  isSocketConnected(): boolean {
    return this.socket?.connected || false;
  }

  sendMessage(receiverId: string, message: string): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected, using HTTP fallback');
      this.sendMessageHttp(receiverId, message).catch(error => {
        console.error('Failed to send message via HTTP:', error);
      });
      return;
    }

    this.socket.emit('send_message', {
      receiver_id: receiverId,
      message: message
    });
  }

  async sendMessageHttp(receiverId: string, message: string): Promise<ChatMessage> {
    try {
      console.log(`Sending message via HTTP: receiver=${receiverId}, message="${message}"`);
      
      const response = await api.post('/send-message', {
        receiver_id: receiverId,
        message: message
      });
      
      console.log('Message sent successfully via HTTP:', response.data);
      
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
      console.error('Error sending message via HTTP:', error);
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

  async getMessages(receiverId: string): Promise<ChatMessage[]> {
    try {
      // Usar la nueva ruta que maneja UUIDs
      const response = await api.get(`/get-messages-uuid/${receiverId}`);
      return response.data.messages || [];
    } catch (error) {
      console.error('Error getting messages:', error);
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
      console.error('Error getting users:', error);
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
      console.error('Error getting unread counts:', error);
      return {};
    }
  }
}

export const chatService = new ChatService();
export type { ChatMessage, User };
