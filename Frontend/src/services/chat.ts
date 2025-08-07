interface SendMessageRequest {
  receiver_id?: string;
  message: string;
}

interface ChatMessage {
  id: string;
  sender_id: string;
  receiver_id?: string;
  message: string;
  timestamp: string;
  demo_mode?: boolean;
}

interface ChatResponse {
  messages?: ChatMessage[];
  error?: string;
}

class ChatService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  async sendMessage(messageData: SendMessageRequest): Promise<ChatMessage> {
    try {
      const response = await fetch(`${this.baseUrl}/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Para incluir cookies de sesión
        body: JSON.stringify(messageData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getMessages(receiverId?: string): Promise<ChatMessage[]> {
    try {
      const url = receiverId 
        ? `${this.baseUrl}/get-messages?receiver_id=${receiverId}`
        : `${this.baseUrl}/get-messages`;
        
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data.messages || [];
    } catch (error) {
      console.error('Error getting messages:', error);
      throw error;
    }
  }

  // Método para simular un chat con IA médica (puedes expandir esto)
  async sendAIMessage(message: string): Promise<ChatMessage> {
    try {
      // Por ahora, simularemos una respuesta de IA
      // En el futuro, podrías integrar con un servicio de IA real
      const aiResponse = this.generateAIResponse(message);
      
      return {
        id: `ai_${Date.now()}`,
        sender_id: 'ai_assistant',
        message: aiResponse,
        timestamp: new Date().toISOString(),
        demo_mode: true
      };
    } catch (error) {
      console.error('Error with AI message:', error);
      throw error;
    }
  }

  private generateAIResponse(userMessage: string): string {
    const lowerMessage = userMessage.toLowerCase();
    
    // Respuestas básicas según palabras clave
    if (lowerMessage.includes('dolor de cabeza') || lowerMessage.includes('cefalea')) {
      return 'Para el dolor de cabeza, es importante identificar la causa. ¿Has tenido fiebre? ¿El dolor es constante o pulsátil? Te recomiendo descansar, mantener hidratación y si persiste, consultar con un médico.';
    }
    
    if (lowerMessage.includes('fiebre') || lowerMessage.includes('temperatura')) {
      return 'La fiebre puede indicar una infección. ¿Qué temperatura has registrado? ¿Tienes otros síntomas como dolor de garganta, tos o malestar general? Es importante monitorear y consultar si la temperatura supera los 38.5°C.';
    }
    
    if (lowerMessage.includes('tos')) {
      return 'La tos puede tener varias causas. ¿Es tos seca o con flemas? ¿Desde cuándo la tienes? ¿Has tenido fiebre o dificultad para respirar? Te recomiendo mantener hidratación y si persiste más de una semana, consultar con un médico.';
    }
    
    if (lowerMessage.includes('presión') || lowerMessage.includes('hipertensión')) {
      return 'El control de la presión arterial es muy importante. ¿Tienes registros recientes de tu presión? Te recomiendo una dieta baja en sodio, ejercicio regular y seguimiento médico constante.';
    }
    
    if (lowerMessage.includes('diabetes') || lowerMessage.includes('azúcar')) {
      return 'Para el manejo de la diabetes es crucial mantener una dieta equilibrada, ejercicio regular y monitoreo constante de los niveles de glucosa. ¿Tienes un glucómetro para medirte en casa?';
    }
    
    // Respuesta general
    return 'Gracias por tu consulta. Para brindarte la mejor atención, te recomiendo que consultes con un médico para una evaluación completa. Mientras tanto, mantén hábitos saludables y observa cualquier cambio en tus síntomas.';
  }
}

export const chatService = new ChatService();
export type { ChatMessage, SendMessageRequest };
