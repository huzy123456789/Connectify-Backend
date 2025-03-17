## Messaging APIs

The Messaging API provides endpoints for real-time messaging between users, including one-to-one conversations and group chats. All messaging is organization-specific, meaning users can only message others within the same organization.

### Key Features
- One-to-one conversations
- Group chats with multiple participants
- Message reactions with emojis
- File attachments (images, videos, documents, audio)
- Read receipts
- Message replies
- User blocking
- Group chat administration

### Conversations (One-to-One)

#### Create Conversation
Start a new conversation with another user in the same organization.

- **URL**: `/api/messaging/conversations/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "participant_id": 2,
    "organization_id": 1,
    "initial_message": "Hello, let's chat!"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Conversation object with participants and initial message
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "detail": "The participant doesn't belong to this organization"
    }
    ```
  - OR
    ```json
    {
      "detail": "Conversation already exists",
      "conversation_id": 5
    }
    ```
  - OR
    ```json
    {
      "detail": "You have been blocked by this user"
    }
    ```

#### List Conversations
Get all conversations for the authenticated user.

- **URL**: `/api/messaging/conversations/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of conversation objects with last message preview and unread count

#### Get Conversation Detail
Get detailed information about a specific conversation.

- **URL**: `/api/messaging/conversations/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Conversation object with participants and messages

#### Get Conversation Messages
Get paginated messages for a specific conversation.

- **URL**: `/api/messaging/conversations/<id>/messages/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of messages per page (default: 20, max: 100)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of messages with reactions and read status

#### Send Message
Send a message in a conversation.

- **URL**: `/api/messaging/conversations/<id>/send_message/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Hello, how are you?",
    "reply_to": null,
    "attachments": [file1, file2],
    "attachment_types": ["image", "document"]
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Created message object
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "You have been blocked by this user"
    }
    ```

### Group Chats

#### Create Group Chat
Create a new group chat with multiple participants from the same organization.

- **URL**: `/api/messaging/group-chats/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "Project Team",
    "description": "Group chat for our project team",
    "organization_id": 1,
    "member_ids": [2, 3, 4],
    "initial_message": "Welcome to the project team chat!",
    "avatar": file
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Group chat object with members and initial message
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "detail": "User with ID 3 doesn't belong to this organization"
    }
    ```
  - OR
    ```json
    {
      "detail": "You are blocked by: username1, username2"
    }
    ```

#### List Group Chats
Get all group chats for the authenticated user.

- **URL**: `/api/messaging/group-chats/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of group chat objects with last message preview and unread count

#### Get Group Chat Detail
Get detailed information about a specific group chat.

- **URL**: `/api/messaging/group-chats/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Group chat object with members and messages

#### Get Group Chat Messages
Get paginated messages for a specific group chat.

- **URL**: `/api/messaging/group-chats/<id>/messages/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of messages per page (default: 20, max: 100)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of messages with reactions and read status

#### Send Message to Group
Send a message in a group chat.

- **URL**: `/api/messaging/group-chats/<id>/send_message/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Hello everyone!",
    "reply_to": null,
    "attachments": [file1, file2],
    "attachment_types": ["image", "document"]
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Created message object
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "You are not a member of this group chat"
    }
    ```

#### Add Members to Group
Add new members to a group chat (admin only).

- **URL**: `/api/messaging/group-chats/<id>/add_members/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "member_ids": [5, 6]
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Updated group chat object
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "Only admins can add members"
    }
    ```

#### Remove Member from Group
Remove a member from a group chat (admin only, or self-removal).

- **URL**: `/api/messaging/group-chats/<id>/remove_member/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "member_id": 5
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Updated group chat object
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "Only admins can remove other members"
    }
    ```

#### Change Member Role
Change a member's role in a group chat (admin only).

- **URL**: `/api/messaging/group-chats/<id>/change_role/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "member_id": 5,
    "role": "admin"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Updated membership object
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "Only admins can change roles"
    }
    ```

### Messages

#### Get Message Detail
Get detailed information about a specific message.

- **URL**: `/api/messaging/messages/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Message object with reactions and read status

#### Edit Message
Edit a message (sender only).

- **URL**: `/api/messaging/messages/<id>/edit/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Updated message content"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Updated message object
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "You can only edit your own messages"
    }
    ```

#### Delete Message
Delete a message (sender only).

- **URL**: `/api/messaging/messages/<id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 204 NO CONTENT
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "You can only delete your own messages"
    }
    ```

#### React to Message
Add an emoji reaction to a message.

- **URL**: `/api/messaging/messages/<id>/react/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "emoji": "👍"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Reaction object

#### Remove Reaction
Remove an emoji reaction from a message.

- **URL**: `/api/messaging/messages/<id>/unreact/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Query Parameters**:
  - `emoji`: Specific emoji to remove (optional, removes all if not specified)
- **Success Response**:
  - **Code**: 204 NO CONTENT

### User Blocking

#### Block User
Block a user from messaging you in a specific organization.

- **URL**: `/api/messaging/blocks/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "blocked_id": 3,
    "organization_id": 1
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Block object
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "detail": "The user to block doesn't belong to this organization"
    }
    ```

#### List Blocked Users
Get all users blocked by the authenticated user.

- **URL**: `/api/messaging/blocks/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Array of block objects

#### Unblock User
Unblock a previously blocked user.

- **URL**: `/api/messaging/blocks/<id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 204 NO CONTENT
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "You can only unblock users you have blocked"
    }
    ```

    ## WebSocket Implementation

The Connectify application uses WebSockets for real-time messaging, typing indicators, and read receipts.

### Connection Setup

#### One-to-One Conversations

Connect to a WebSocket for a specific conversation:
ws://domain/ws/messaging/conversations/{conversation_id}/?token={jwt_token}


#### Group Chats

Connect to a WebSocket for a specific group chat:
ws://domain/ws/messaging/group-chats/{group_chat_id}/?token={jwt_token}


### Message Types

#### Sending Messages

To send a message through WebSocket:

```json
{
  "type": "message",
  "content": "Hello, this is a message",
  "reply_to": null
}
```

#### Typing Indicators

To indicate that a user is typing:

```json
{
  "type": "typing",
  "is_typing": true
}
```

To indicate that a user has stopped typing:

```json
{
  "type": "typing",
  "is_typing": false
}
```

#### Read Receipts

To mark a message as read:

```json
{
  "type": "read",
  "message_id": 123
}
```

### Event Handling

#### Receiving Messages

When a new message is sent to the conversation/group chat:

```json
{
  "type": "message",
  "message": {
    "id": 123,
    "sender_id": 1,
    "sender_username": "user1",
    "content": "Hello, this is a message",
    "created_at": "2023-10-15T15:00:00Z",
    "reply_to": null
  }
}
```

#### Receiving Typing Indicators

When a user starts or stops typing:

```json
{
  "type": "typing",
  "user_id": 1,
  "username": "user1",
  "is_typing": true
}
```

#### Receiving Read Receipts

When a user reads a message:

```json
{
  "type": "read",
  "user_id": 1,
  "message_id": 123
}
```

## React Native Implementation Guide

This section provides guidance on implementing the messaging functionality in a React Native application.

### Setting Up API Services

#### API Client Setup

```javascript
// api/client.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://your-api-domain.com/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;
```

#### Messaging Service

```javascript
// api/messagingService.js
import apiClient from './client';

export const messagingService = {
  // Conversations
  getConversations: () => apiClient.get('/messaging/conversations/'),
  createConversation: (data) => apiClient.post('/messaging/conversations/create/', data),
  getConversationDetail: (id) => apiClient.get(`/messaging/conversations/${id}/`),
  getConversationMessages: (id, page = 1) => 
    apiClient.get(`/messaging/conversations/${id}/messages/?page=${page}`),
  sendMessage: (id, data) => 
    apiClient.post(`/messaging/conversations/${id}/send-message/`, data),
  
  // Group Chats
  getGroupChats: () => apiClient.get('/messaging/group-chats/'),
  createGroupChat: (data) => apiClient.post('/messaging/group-chats/create/', data),
  getGroupChatDetail: (id) => apiClient.get(`/messaging/group-chats/${id}/`),
  getGroupChatMessages: (id, page = 1) => 
    apiClient.get(`/messaging/group-chats/${id}/messages/?page=${page}`),
  sendGroupMessage: (id, data) => 
    apiClient.post(`/messaging/group-chats/${id}/send-message/`, data),
  addGroupMembers: (id, data) => 
    apiClient.post(`/messaging/group-chats/${id}/add-members/`, data),
  removeGroupMember: (id, data) => 
    apiClient.post(`/messaging/group-chats/${id}/remove-member/`, data),
  changeGroupRole: (id, data) => 
    apiClient.post(`/messaging/group-chats/${id}/change-role/`, data),
  
  // Messages
  getMessageDetail: (id) => apiClient.get(`/messaging/messages/${id}/`),
  deleteMessage: (id) => apiClient.delete(`/messaging/messages/${id}/delete/`),
  editMessage: (id, data) => apiClient.put(`/messaging/messages/${id}/edit/`, data),
  reactToMessage: (id, data) => apiClient.post(`/messaging/messages/${id}/react/`, data),
  removeReaction: (id, emoji) => 
    apiClient.delete(`/messaging/messages/${id}/unreact/${emoji ? `?emoji=${emoji}` : ''}`),
  
  // User Blocks
  getBlocks: () => apiClient.get('/messaging/blocks/'),
  blockUser: (data) => apiClient.post('/messaging/blocks/create/', data),
  unblockUser: (id) => apiClient.delete(`/messaging/blocks/${id}/delete/`)
};
```

### WebSocket Integration

#### WebSocket Manager

```javascript
// utils/websocketManager.js
import AsyncStorage from '@react-native-async-storage/async-storage';

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.messageHandlers = [];
    this.typingHandlers = [];
    this.readHandlers = [];
    this.connectionHandlers = [];
    this.errorHandlers = [];
  }

  async connect(type, id) {
    // Close existing connection if any
    this.disconnect();
    
    const token = await AsyncStorage.getItem('auth_token');
    const wsUrl = `ws://your-api-domain.com/ws/messaging/${type}/${id}/?token=${token}`;
    
    this.socket = new WebSocket(wsUrl);
    
    this.socket.onopen = () => {
      console.log(`WebSocket connected to ${type} ${id}`);
      this.connectionHandlers.forEach(handler => handler(true));
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          this.messageHandlers.forEach(handler => handler(data.message));
          break;
        case 'typing':
          this.typingHandlers.forEach(handler => 
            handler(data.user_id, data.username, data.is_typing));
          break;
        case 'read':
          this.readHandlers.forEach(handler => 
            handler(data.user_id, data.message_id));
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.connectionHandlers.forEach(handler => handler(false));
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.errorHandlers.forEach(handler => handler(error));
    };
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
  
  sendMessage(content, replyTo = null) {
    if (!this.socket) return;
    
    const message = {
      type: 'message',
      content,
      reply_to: replyTo
    };
    
    this.socket.send(JSON.stringify(message));
  }
  
  sendTypingIndicator(isTyping) {
    if (!this.socket) return;
    
    const message = {
      type: 'typing',
      is_typing: isTyping
    };
    
    this.socket.send(JSON.stringify(message));
  }
  
  sendReadReceipt(messageId) {
    if (!this.socket) return;
    
    const message = {
      type: 'read',
      message_id: messageId
    };
    
    this.socket.send(JSON.stringify(message));
  }
  
  onMessage(handler) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }
  
  onTyping(handler) {
    this.typingHandlers.push(handler);
    return () => {
      this.typingHandlers = this.typingHandlers.filter(h => h !== handler);
    };
  }
  
  onRead(handler) {
    this.readHandlers.push(handler);
    return () => {
      this.readHandlers = this.readHandlers.filter(h => h !== handler);
    };
  }
  
  onConnection(handler) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(h => h !== handler);
    };
  }
  
  onError(handler) {
    this.errorHandlers.push(handler);
    return () => {
      this.errorHandlers = this.errorHandlers.filter(h => h !== handler);
    };
  }
}

export default new WebSocketManager();
```

### State Management

#### Using React Context for Messaging

```javascript
// context/MessagingContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { messagingService } from '../api/messagingService';
import websocketManager from '../utils/websocketManager';

const MessagingContext = createContext();

export const useMessaging = () => useContext(MessagingContext);

export const MessagingProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [groupChats, setGroupChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [typingUsers, setTypingUsers] = useState({});
  const [connected, setConnected] = useState(false);
  
  // Load conversations and group chats
  const loadChats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [conversationsRes, groupChatsRes] = await Promise.all([
        messagingService.getConversations(),
        messagingService.getGroupChats()
      ]);
      
      setConversations(conversationsRes.data);
      setGroupChats(groupChatsRes.data);
    } catch (err) {
      setError('Failed to load chats');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Load messages for a specific chat
  const loadMessages = async (chatType, chatId, page = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      let response;
      
      if (chatType === 'conversation') {
        response = await messagingService.getConversationMessages(chatId, page);
      } else {
        response = await messagingService.getGroupChatMessages(chatId, page);
      }
      
      if (page === 1) {
        setMessages(response.data.results);
      } else {
        setMessages(prev => [...prev, ...response.data.results]);
      }
      
      return response.data;
    } catch (err) {
      setError('Failed to load messages');
      console.error(err);
      return null;
    } finally {
      setLoading(false);
    }
  };
  
  // Connect to WebSocket for a specific chat
  const connectToChat = async (chatType, chatId) => {
    try {
      await websocketManager.connect(
        chatType === 'conversation' ? 'conversations' : 'group-chats',
        chatId
      );
      
      // Set current chat
      setCurrentChat({
        type: chatType,
        id: chatId
      });
      
      // Clear typing users
      setTypingUsers({});
      
      // Load initial messages
      await loadMessages(chatType, chatId);
    } catch (err) {
      setError('Failed to connect to chat');
      console.error(err);
    }
  };
  
  // Send a message
  const sendMessage = async (content, replyTo = null) => {
    if (!currentChat) return;
    
    try {
      // Send via WebSocket for real-time delivery
      websocketManager.sendMessage(content, replyTo);
      
      // Also send via REST API as a fallback
      const data = {
        content,
        reply_to: replyTo
      };
      
      if (currentChat.type === 'conversation') {
        await messagingService.sendMessage(currentChat.id, data);
      } else {
        await messagingService.sendGroupMessage(currentChat.id, data);
      }
    } catch (err) {
      setError('Failed to send message');
      console.error(err);
    }
  };
  
  // Handle typing indicator
  const setTyping = (isTyping) => {
    if (!currentChat) return;
    websocketManager.sendTypingIndicator(isTyping);
  };
  
  // Mark message as read
  const markAsRead = (messageId) => {
    if (!currentChat) return;
    websocketManager.sendReadReceipt(messageId);
  };
  
  // Set up WebSocket event handlers
  useEffect(() => {
    const messageUnsubscribe = websocketManager.onMessage((message) => {
      setMessages(prev => [message, ...prev]);
    });
    
    const typingUnsubscribe = websocketManager.onTyping((userId, username, isTyping) => {
      setTypingUsers(prev => {
        if (isTyping) {
          return { ...prev, [userId]: username };
        } else {
          const newState = { ...prev };
          delete newState[userId];
          return newState;
        }
      });
    });
    
    const readUnsubscribe = websocketManager.onRead((userId, messageId) => {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === messageId 
            ? { ...msg, read_by: [...(msg.read_by || []), userId] } 
            : msg
        )
      );
    });
    
    const connectionUnsubscribe = websocketManager.onConnection((status) => {
      setConnected(status);
    });
    
    // Clean up event handlers
    return () => {
      messageUnsubscribe();
      typingUnsubscribe();
      readUnsubscribe();
      connectionUnsubscribe();
      websocketManager.disconnect();
    };
  }, []);
  
  // Initial load of chats
  useEffect(() => {
    loadChats();
  }, []);
  
  const value = {
    conversations,
    groupChats,
    currentChat,
    messages,
    loading,
    error,
    typingUsers,
    connected,
    loadChats,
    loadMessages,
    connectToChat,
    sendMessage,
    setTyping,
    markAsRead
  };
  
  return (
    <MessagingContext.Provider value={value}>
      {children}
    </MessagingContext.Provider>
  );
};

