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
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve();
        return;
      }

      this.socket = io(this.baseUrl, {
        withCredentials: true,
        transports: ['websocket', 'polling']
      });

      this.socket.on('connect', () => {
        console.log('Connected to chat server');
        resolve();
      });

      this.socket.on('connect_error', (error: any) => {
        console.error('Connection error:', error);
        reject(error);
      });

      this.socket.on('new_message', (message: ChatMessage) => {
        this.messageCallbacks.forEach(callback => callback(message));
      });

      this.socket.on('message_sent', (message: any) => {
        console.log('Message sent successfully:', message);
      });

      this.socket.on('user_status', (data: { user_id: string; status: 'online' | 'offline' }) => {
        this.userStatusCallbacks.forEach(callback => callback(data.user_id, data.status));
      });

      this.socket.on('message_error', (error: { error: string }) => {
        console.error('Message error:', error);
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  sendMessage(receiverId: string, message: string): void {
    if (!this.socket?.connected) {
      throw new Error('Socket not connected');
    }

    this.socket.emit('send_message', {
      receiver_id: receiverId,
      message: message
    });
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
      const response = await api.get(`/get-messages?receiver_id=${receiverId}`);
      return response.data.messages || [];
    } catch (error) {
      console.error('Error getting messages:', error);
      throw error;
    }
  }

  async getUsers(): Promise<User[]> {
    try {
      const response = await api.get('/get-doctors');
      const data = response.data;
      return data.doctors?.map((doctor: any) => ({
        id: doctor.id.toString(),
        name: `${doctor.firstName} ${doctor.lastName1}`,
        email: doctor.email,
        specialty: doctor.speciality,
        status: 'offline' as const
      })) || [];
    } catch (error) {
      console.error('Error getting users:', error);
      return [
        {
          id: 'demo1',
          name: 'Dr. Juan Pérez',
          email: 'juan.perez@hospital.com',
          specialty: 'Cardiología',
          status: 'online' as const
        },
        {
          id: 'demo2',
          name: 'Dra. María González',
          email: 'maria.gonzalez@hospital.com',
          specialty: 'Neurología',
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
