# Frontend Implementation Guide

## 1. Chat Service Setup

```typescript
// Types
interface Message {
  id?: string;
  local_id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  sent_at: string;
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
  attachments?: Attachment[];
  reply_to?: string;
}

interface LocalStorageSchema {
  messages: {
    [conversationId: string]: Message[];
  };
  lastSync: {
    [conversationId: string]: string;
  };
  messageQueue: Message[];
  unreadCounts: {
    [conversationId: string]: number;
  };
}

// Chat Service
class ChatService {
  private static instance: ChatService;
  private ws: WebSocket | null = null;
  private messageQueue: Message[] = [];
  private readonly STORAGE_KEY = '@chat_storage';
  private readonly SYNC_INTERVAL = 1000 * 60 * 5; // 5 minutes

  static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  async init(token: string) {
    await this.loadFromStorage();
    this.connect(token);
    this.startPeriodicSync();
  }

  private async loadFromStorage() {
    try {
      const stored = await AsyncStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const data: LocalStorageSchema = JSON.parse(stored);
        // Populate local state
        this.messageQueue = data.messageQueue || [];
        return data;
      }
    } catch (error) {
      console.error('Failed to load from storage:', error);
    }
    return null;
  }

  private async saveToStorage(data: Partial<LocalStorageSchema>) {
    try {
      const current = await this.loadFromStorage() || {};
      const updated = { ...current, ...data };
      await AsyncStorage.setItem(this.STORAGE_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save to storage:', error);
    }
  }

  async sendMessage(message: Omit<Message, 'id' | 'sent_at' | 'status'>) {
    const localId = uuid.v4();
    const newMessage: Message = {
      ...message,
      local_id: localId,
      sent_at: new Date().toISOString(),
      status: 'sending'
    };

    // Optimistically add to local storage
    await this.addMessageToStorage(newMessage);

    // Try to send
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'send_message',
        ...message,
        local_id: localId
      }));
    } else {
      this.messageQueue.push(newMessage);
      await this.saveToStorage({ messageQueue: this.messageQueue });
    }

    return localId;
  }

  private async addMessageToStorage(message: Message) {
    const stored = await this.loadFromStorage() || {};
    const conversationMessages = stored.messages?.[message.conversation_id] || [];
    
    stored.messages = {
      ...stored.messages,
      [message.conversation_id]: [...conversationMessages, message]
    };

    await this.saveToStorage(stored);
  }

  async getMessages(conversationId: string, limit = 50, before?: string): Promise<Message[]> {
    // First try local storage
    const stored = await this.loadFromStorage();
    const localMessages = stored?.messages?.[conversationId] || [];

    if (localMessages.length >= limit && !before) {
      return localMessages.slice(-limit);
    }

    // If we need more messages, fetch from server
    try {
      const response = await fetch(`/api/messages?conversation_id=${conversationId}&limit=${limit}&before=${before}`);
      const { messages } = await response.json();

      // Merge with local messages and save
      const merged = this.mergeMessages(localMessages, messages);
      await this.saveToStorage({
        messages: {
          ...stored?.messages,
          [conversationId]: merged
        }
      });

      return merged;
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      return localMessages;
    }
  }

  private mergeMessages(local: Message[], remote: Message[]): Message[] {
    const messageMap = new Map<string, Message>();
    
    // Prefer remote messages over local ones
    [...local, ...remote].forEach(msg => {
      const key = msg.id || msg.local_id;
      if (!messageMap.has(key) || msg.id) { // Prefer messages with server IDs
        messageMap.set(key, msg);
      }
    });

    return Array.from(messageMap.values())
      .sort((a, b) => new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime());
  }

  private startPeriodicSync() {
    setInterval(async () => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        const stored = await this.loadFromStorage();
        if (!stored?.lastSync) return;

        // Sync each conversation
        Object.entries(stored.lastSync).forEach(([conversationId, lastSync]) => {
          this.ws!.send(JSON.stringify({
            action: 'sync_messages',
            conversation_id: conversationId,
            since: lastSync
          }));
        });
      }
    }, this.SYNC_INTERVAL);
  }
}

// Usage in React Native component
function ChatScreen({ conversationId }) {
  const chatService = useMemo(() => ChatService.getInstance(), []);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const loadMessages = async () => {
      const msgs = await chatService.getMessages(conversationId);
      setMessages(msgs);
    };
    loadMessages();
  }, [conversationId]);

  const sendMessage = async (content: string) => {
    const localId = await chatService.sendMessage({
      conversation_id: conversationId,
      content,
      sender_id: currentUserId
    });

    // Optimistically update UI
    setMessages(prev => [...prev, {
      local_id: localId,
      status: 'sending',
      // ... other message properties
    }]);
  };

  return (
    // Your chat UI implementation
  );
}
```

## 2. Local Storage Management

```typescript
// Storage Manager
class StorageManager {
  static async pruneOldMessages() {
    const stored = await AsyncStorage.getItem('@chat_storage');
    if (!stored) return;

    const data: LocalStorageSchema = JSON.parse(stored);
    const ONE_WEEK = 7 * 24 * 60 * 60 * 1000;

    // Keep only last week's messages
    Object.entries(data.messages).forEach(([convId, messages]) => {
      data.messages[convId] = messages.filter(msg => 
        new Date().getTime() - new Date(msg.sent_at).getTime() < ONE_WEEK
      );
    });

    await AsyncStorage.setItem('@chat_storage', JSON.stringify(data));
  }
}

// Run cleanup periodically
setInterval(StorageManager.pruneOldMessages, 24 * 60 * 60 * 1000); // Daily
```

## Key Features

1. Single WebSocket connection management
2. Local message storage and retrieval
3. Message synchronization with server
4. Offline message queueing
5. Optimistic updates
6. Periodic storage cleanup
7. Message deduplication
8. Attachment handling
9. Read receipt tracking
10. Typing indicators

## Best Practices

1. Always handle messages optimistically
2. Implement proper error recovery
3. Use proper TypeScript types
4. Implement storage quotas
5. Handle attachment uploads separately
6. Implement proper retry logic
7. Use proper state management
8. Implement proper pagination
9. Handle network changes
10. Implement proper logging

## Error Recovery

```typescript
class ErrorRecovery {
  static async recoverFromError() {
    const stored = await AsyncStorage.getItem('@chat_storage');
    if (!stored) return;

    const data: LocalStorageSchema = JSON.parse(stored);
    
    // Retry failed messages
    const failedMessages = Object.values(data.messages)
      .flat()
      .filter(msg => msg.status === 'failed');

    for (const message of failedMessages) {
      await ChatService.getInstance().sendMessage(message);
    }
  }
}
```

This implementation provides a robust foundation for a chat application with proper local storage management and offline support.
