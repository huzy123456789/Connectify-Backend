# Real-time Messaging API Documentation

## Connection Setup

### WebSocket Connection URL
```javascript
// Format: {BASE_URL}/conversations/{conversationId}/
const wsUrl = `${BASE_URL}/conversations/${conversationId}/?token=${yourAuthToken}`;
const ws = new WebSocket(wsUrl);
```

### Connection Status Codes
- `4003`: Unauthorized (Invalid/Missing token)
- `4004`: Access denied
- `1000`: Normal closure
- `1006`: Abnormal closure (Connection lost)

---

## Message Types and Handlers

### 1. Sending a Message
#### Request
```javascript
{
    "action": "send_message",
    "conversation_id": "123",
    "content": "Hello!",
    "local_id": "temp_123" // Client-generated ID for tracking
}
```

#### Response
```javascript
// Success
{
    "type": "chat_message",
    "message": {
        "id": "456",
        "local_id": "temp_123",
        "sender_id": "789",
        "content": "Hello!",
        "timestamp": "2023-12-01T12:00:00Z",
        "status": "sent"
    }
}

// Error
{
    "type": "message.failed",
    "local_id": "temp_123",
    "error": "Error message"
}
```

---

### 2. Typing Indicators
#### Request
```javascript
{
    "action": "typing",
    "conversation_id": "123",
    "is_typing": true
}
```

#### Response (Broadcast)
```javascript
{
    "type": "typing",
    "user_id": "789",
    "username": "john_doe",
    "is_typing": true
}
```

---

### 3. Read Receipts
#### Request
```javascript
{
    "action": "read",
    "conversation_id": "123",
    "message_ids": ["456", "457"]
}
```

#### Response (Broadcast)
```javascript
{
    "type": "read",
    "user_id": "789",
    "message_ids": ["456", "457"]
}
```

---

### 4. Fetching Message History
#### Request
```javascript
{
    "action": "fetch_messages",
    "conversation_id": "123",
    "before_id": "456", // Optional - for pagination
    "limit": 20 // Optional
}
```

#### Response
```javascript
{
    "type": "messages_fetched",
    "conversation_id": "123",
    "messages": [
        {
            "id": "455",
            "sender_id": "789",
            "content": "Previous message",
            "sent_at": "2023-12-01T11:59:00Z",
            "is_edited": false,
            "is_deleted": false
        },
        // ... more messages
    ]
}
```

---

### 5. Heartbeat Acknowledgement
#### Request
```javascript
{
    "action": "heartbeat_ack"
}
```

#### Response
No response expected from the server.

---

### 6. Message Status Updates
#### Response (Automatic)
```javascript
{
    "type": "message.status",
    "message_id": "456",
    "status": "delivered", // or "sent", "read", "failed"
    "timestamp": "2023-12-01T12:00:01Z"
}
```

---

### 7. User Presence Updates
#### Response (Automatic)
```javascript
{
    "type": "user_status",
    "user_id": "789",
    "status": "online", // or "offline"
    "timestamp": "2023-12-01T12:00:00Z"
}
```

---

### 8. Chat Message Broadcast
#### Response (Broadcast)
```javascript
{
    "type": "chat_message",
    "message": {
        "id": "456",
        "local_id": "temp_123",
        "sender_id": "789",
        "content": "Hello!",
        "timestamp": "2023-12-01T12:00:00Z",
        "status": "sent"
    }
}
```

---

### 9. Heartbeat Mechanism
#### Request
```javascript
{
    "action": "heartbeat"
}
```

#### Response
No response expected from the server.

---

## Implementation Notes

1. **Connection Lifecycle**:
   - Connect when the user opens the chat screen.
   - Handle events based on message type.
   - Monitor connection and reconnect when needed.
   - Acknowledge heartbeats to keep the connection alive.

2. **Frontend Handlers**:
   - Implement handlers for all message types (`send_message`, `typing`, `read`, `fetch_messages`, `heartbeat_ack`).
   - Update the UI in real-time based on WebSocket events.

3. **Offline Support**:
   - Store unsent messages in local storage.
   - Retry sending messages on reconnection.
   - Implement message queueing for failed attempts.

4. **Best Practices**:
   - Use optimistic updates for better UX.
   - Track message states (`sending`, `sent`, `delivered`, `read`, `failed`).
   - Implement reconnection with exponential backoff.
   - Support pagination for message history.
