'use client';

import { useState, useEffect, useRef } from 'react';
import Layout from '@/components/layout/Layout';
import { chatService, type ChatMessage, type User } from '@/services/chatRealTime';
import api from '@/lib/api';

export default function ChatPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  // Estado para todos los mensajes y mensajes filtrados
  const [allMessages, setAllMessages] = useState<ChatMessage[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [unreadCounts, setUnreadCounts] = useState<{ [userId: string]: number }>({});
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [typingUsers, setTypingUsers] = useState<{ [userId: string]: boolean }>({});
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat on component mount
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Solicitar permisos de notificación
        chatService.requestNotificationPermission();

        // Connect to chat service
        await chatService.connect();

        // Configurar listener de estado de conexión
        const unsubscribeConnection = chatService.onConnectionStatus((connected: boolean) => {
          setIsConnected(connected);
          if (connected) {
            setConnectionAttempts(0);
          } else {
            setConnectionAttempts(prev => prev + 1);
          }
        });

        // Cargar usuarios
        const usersList = await chatService.getUsers();
        setUsers(usersList);

        // Cargar conteos de mensajes no leídos
        const counts = await chatService.getUnreadCounts();
        setUnreadCounts(counts);

        // Configurar listeners
        const unsubscribeMessage = chatService.onMessage((message: ChatMessage) => {
          // Siempre agregar el mensaje a la lista global
          setAllMessages(prev => {
            // Evitar duplicados
            const exists = prev.some(m => m.id === message.id);
            if (exists) return prev;
            
            return [...prev, message];
          });
          
          // Actualizar conteos si el mensaje no es del usuario actual y no es mío
          if (!message.is_mine) {
            setUnreadCounts(prev => {
              const senderId = message.sender_id;
              return {
                ...prev,
                [senderId]: (prev[senderId] || 0) + 1
              };
            });
          }
        });

        const unsubscribeUserStatus = chatService.onUserStatusChange((userId: string, status: 'online' | 'offline') => {
          setUsers(prev => prev.map(user => 
            (user.id === userId || user.supabase_id === userId) ? { ...user, status } : user
          ));
        });

        const unsubscribeTyping = chatService.onTyping((userId: string, isTyping: boolean) => {
          setTypingUsers(prev => ({
            ...prev,
            [userId]: isTyping
          }));
        });

        const unsubscribeUnreadMessage = chatService.onUnreadMessage((data) => {
          // Mostrar notificación si no estamos en la conversación actual
          if (!selectedUser || (selectedUser.supabase_id !== data.sender_id && selectedUser.id !== data.sender_id)) {
            if ('Notification' in window && Notification.permission === 'granted' && document.hidden) {
              new Notification(`Nuevo mensaje de ${data.sender_name}`, {
                body: data.message_preview,
                icon: '/favicon.ico',
                tag: 'chat-notification'
              });
            }
          }
        });

        setIsConnected(chatService.isSocketConnected());
        setIsLoading(false);

        // Cleanup function
        return () => {
          unsubscribeConnection();
          unsubscribeMessage();
          unsubscribeUserStatus();
          unsubscribeTyping();
          unsubscribeUnreadMessage();
          chatService.disconnect();
        };
      } catch (error) {
        setIsLoading(false);
        setIsConnected(false);
      }
    };

    const cleanup = initializeChat();
    
    return () => {
      cleanup.then(cleanupFn => cleanupFn && cleanupFn());
    };
  }, []);

  // Filtrar mensajes cuando cambia el usuario seleccionado o los mensajes globales
  useEffect(() => {
    if (selectedUser) {
      const userId = selectedUser.supabase_id || selectedUser.id;
      const filteredMessages = allMessages.filter(message => 
        message.sender_id === userId || 
        message.receiver_id === userId ||
        message.is_mine
      );
      setMessages(filteredMessages);
    } else {
      setMessages([]);
    }
  }, [selectedUser, allMessages]);

  // Cargar mensajes cuando se selecciona un usuario
  useEffect(() => {
    const loadMessages = async () => {
      if (selectedUser) {
        try {
          const userId = selectedUser.supabase_id || selectedUser.id;
          const userMessages = await chatService.getMessages(userId);
          
          // Agregar mensajes históricos a allMessages
          setAllMessages(prev => {
            const newMessages = userMessages.filter(msg => 
              !prev.some(existingMsg => existingMsg.id === msg.id)
            );
            return [...prev, ...newMessages];
          });
          
          // Marcar mensajes como leídos (resetear contador) usando el ID correcto
          const countKey = selectedUser.supabase_id || selectedUser.id;
          setUnreadCounts(prev => ({
            ...prev,
            [countKey]: 0
          }));
        } catch (error) {
          // Error loading messages
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
        
        setAllMessages(prev => [...prev, newMessage]);
      } else {
        // Usar HTTP como fallback
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
        
        setAllMessages(prev => [...prev, newMessage]);
      }
    } catch (error) {
      // Restaurar el mensaje si hay error
      setInputMessage(messageText);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputMessage(e.target.value);
    
    // Enviar indicador de typing
    if (selectedUser && !isTyping) {
      const userId = selectedUser.supabase_id || selectedUser.id;
      chatService.startTyping(userId);
      setIsTyping(true);
      
      // Limpiar después de 3 segundos
      setTimeout(() => {
        setIsTyping(false);
      }, 3000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
      
      // Detener typing indicator al enviar mensaje
      if (selectedUser && isTyping) {
        const userId = selectedUser.supabase_id || selectedUser.id;
        chatService.stopTyping(userId);
        setIsTyping(false);
      }
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
            <div className="mt-2 flex items-center justify-between">
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-1 ${
                  isConnected ? 'bg-green-600 animate-pulse' : 'bg-red-600'
                }`}></div>
                {isConnected 
                  ? 'Tiempo Real Activo' 
                  : connectionAttempts > 0 
                    ? `Reconectando... (${connectionAttempts})`
                    : 'Sin conexión en tiempo real'
                }
              </div>
              {!isConnected && (
                <button
                  onClick={() => {
                    chatService.connect();
                  }}
                  className="text-xs text-blue-600 hover:text-blue-800 underline"
                >
                  Reconectar
                </button>
              )}
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
                
                {/* Typing Indicator */}
                {selectedUser && typingUsers[selectedUser.supabase_id || selectedUser.id] && (
                  <div className="flex justify-start">
                    <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-200 text-gray-800">
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-500">{selectedUser.name} está escribiendo</span>
                        <div className="flex space-x-1">
                          <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 bg-white border-t border-gray-200">
                {!isConnected && (
                  <div className="mb-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800 flex items-center">
                    <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    Modo offline - Los mensajes se enviarán cuando se restablezca la conexión
                  </div>
                )}
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder={isConnected ? "Escribe un mensaje..." : "Escribe un mensaje (se enviará por HTTP)"}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim()}
                    className={`px-4 py-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1 ${
                      isConnected ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-600 hover:bg-gray-700'
                    }`}
                  >
                    {isConnected ? (
                      <>
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                        </svg>
                        <span>Enviar</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                        <span>Enviar</span>
                      </>
                    )}
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
