'use client';

import { useState, useEffect, useRef } from 'react';
import Layout from '@/components/layout/Layout';
import { chatService, type ChatMessage, type User } from '@/services/chatRealTime';
import api from '@/lib/api';

export default function ChatPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [unreadCounts, setUnreadCounts] = useState<{ [userId: string]: number }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Demo login on component mount
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Demo login
        await api.post('/demo-login', {
          name: 'Dr. Demo'
        });

        // Connect to chat service
        await chatService.connect();
        setIsConnected(true);

        // Cargar usuarios
        const usersList = await chatService.getUsers();
        setUsers(usersList);

        // Cargar conteos de mensajes no leídos
        const counts = await chatService.getUnreadCounts();
        setUnreadCounts(counts);

        // Configurar listeners
        const unsubscribeMessage = chatService.onMessage((message: ChatMessage) => {
          if (selectedUser) {
            const selectedUserId = selectedUser.supabase_id || selectedUser.id;
            if (message.sender_id === selectedUserId || message.receiver_id === selectedUserId) {
              setMessages(prev => [...prev, message]);
            }
          }
          
          // Actualizar conteos si el mensaje no es del usuario seleccionado
          if (selectedUser) {
            const selectedUserId = selectedUser.supabase_id || selectedUser.id;
            if (message.sender_id !== selectedUserId) {
              setUnreadCounts(prev => ({
                ...prev,
                [message.sender_id]: (prev[message.sender_id] || 0) + 1
              }));
            }
          }
        });

        const unsubscribeUserStatus = chatService.onUserStatusChange((userId: string, status: 'online' | 'offline') => {
          setUsers(prev => prev.map(user => 
            (user.id === userId || user.supabase_id === userId) ? { ...user, status } : user
          ));
        });

        setIsLoading(false);

        // Cleanup function
        return () => {
          unsubscribeMessage();
          unsubscribeUserStatus();
          chatService.disconnect();
        };
      } catch (error) {
        console.error('Error initializing chat:', error);
        setIsLoading(false);
      }
    };

    const cleanup = initializeChat();
    
    return () => {
      cleanup.then(cleanupFn => cleanupFn && cleanupFn());
    };
  }, []);

  // Cargar mensajes cuando se selecciona un usuario
  useEffect(() => {
    const loadMessages = async () => {
      if (selectedUser) {
        try {
          const userId = selectedUser.supabase_id || selectedUser.id;
          const userMessages = await chatService.getMessages(userId);
          setMessages(userMessages);
          
          // Marcar mensajes como leídos (resetear contador) usando el ID correcto
          const countKey = selectedUser.supabase_id || selectedUser.id;
          setUnreadCounts(prev => ({
            ...prev,
            [countKey]: 0
          }));
        } catch (error) {
          console.error('Error loading messages:', error);
        }
      }
    };

    loadMessages();
  }, [selectedUser]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedUser) return;

    const messageText = inputMessage;
    setInputMessage(''); // Limpiar inmediatamente

    try {
      // Determinar qué ID usar para el receptor (preferir supabase_id si está disponible)
      const receiverId = selectedUser.supabase_id || selectedUser.id;
      
      // Intentar envío por WebSocket primero
      if (isConnected && chatService.isSocketConnected()) {
        chatService.sendMessage(receiverId, messageText);
        
        // Agregar mensaje propio a la lista optimísticamente
        const newMessage: ChatMessage = {
          id: `temp_${Date.now()}`,
          sender_id: 'me',
          receiver_id: receiverId,
          sender_name: 'Tú',
          message: messageText,
          timestamp: new Date().toISOString(),
          is_mine: true
        };
        
        setMessages(prev => [...prev, newMessage]);
      } else {
        // Usar HTTP como fallback
        console.log('Using HTTP fallback for message sending');
        const sentMessage = await chatService.sendMessageHttp(receiverId, messageText);
        
        // Agregar mensaje confirmado a la lista
        const newMessage: ChatMessage = {
          id: sentMessage.id,
          sender_id: sentMessage.sender_id,
          receiver_id: receiverId,
          sender_name: 'Tú',
          message: sentMessage.message,
          timestamp: sentMessage.timestamp,
          is_mine: true
        };
        
        setMessages(prev => [...prev, newMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Restaurar el mensaje si hay error
      setInputMessage(messageText);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Conectando al chat...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex h-screen bg-gray-50">
        {/* Users List */}
        <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">Chat Médico</h2>
            <div className="mt-2">
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-1 ${
                  isConnected ? 'bg-green-600' : 'bg-red-600'
                }`}></div>
                {isConnected ? 'Conectado' : 'Desconectado'}
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {users.map((user) => (
              <div
                key={user.id}
                onClick={() => setSelectedUser(user)}
                className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                  selectedUser?.id === user.id ? 'bg-blue-50 border-blue-200' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center relative">
                        <span className="text-gray-600 font-medium">
                          {user.name.charAt(0).toUpperCase()}
                        </span>
                        <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${
                          user.status === 'online' ? 'bg-green-500' : 'bg-gray-400'
                        }`}></div>
                      </div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{user.name}</p>
                      <p className="text-xs text-gray-500">{user.specialty}</p>
                    </div>
                  </div>
                  {unreadCounts[user.supabase_id || user.id] > 0 && (
                    <div className="bg-blue-600 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                      {unreadCounts[user.supabase_id || user.id]}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedUser ? (
            <>
              {/* Chat Header */}
              <div className="p-4 bg-white border-b border-gray-200">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center relative">
                    <span className="text-gray-600 font-medium">
                      {selectedUser.name.charAt(0).toUpperCase()}
                    </span>
                    <div className={`absolute bottom-0 right-0 w-2 h-2 rounded-full border border-white ${
                      selectedUser.status === 'online' ? 'bg-green-500' : 'bg-gray-400'
                    }`}></div>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-medium text-gray-900">{selectedUser.name}</h3>
                    <p className="text-sm text-gray-500">{selectedUser.specialty}</p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.is_mine ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.is_mine
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-800'
                      }`}
                    >
                      <p className="text-sm">{message.message}</p>
                      <p className={`text-xs mt-1 ${
                        message.is_mine ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 bg-white border-t border-gray-200">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Escribe un mensaje..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Enviar
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
                  <svg fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                  </svg>
                </div>
                <p className="text-lg font-medium">Selecciona un doctor</p>
                <p>Elige un doctor de la lista para comenzar a chatear</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
