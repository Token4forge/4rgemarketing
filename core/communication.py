"""
Inter-Agent Communication System
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import redis
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from config.settings import settings


class MessageType(Enum):
    TASK_COORDINATION = "task_coordination"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    ALERT = "alert"
    PERFORMANCE_FEEDBACK = "performance_feedback"
    RESOURCE_REQUEST = "resource_request"
    STRATEGY_UPDATE = "strategy_update"
    CRISIS_NOTIFICATION = "crisis_notification"


class MessagePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CommunicationMessage:
    """Enhanced communication message"""
    id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    requires_response: bool = False
    correlation_id: Optional[str] = None


class CommunicationHub:
    """Central communication hub for all agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("communication_hub")
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.kafka_producer = None
        self.kafka_consumer = None
        self.message_handlers = {}
        self.active_agents = set()
        self.message_history = []
        
        # Initialize Kafka
        self._init_kafka()
    
    def _init_kafka(self):
        """Initialize Kafka producer and consumer"""
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            self.kafka_consumer = KafkaConsumer(
                f"{settings.KAFKA_TOPIC_PREFIX}_communications",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='ai_marketing_system'
            )
            
            self.logger.info("Kafka initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kafka: {e}")
            # Fallback to Redis-only communication
            self.kafka_producer = None
            self.kafka_consumer = None
    
    async def register_agent(self, agent_id: str):
        """Register an agent with the communication hub"""
        self.active_agents.add(agent_id)
        await self.redis_client.sadd("active_agents", agent_id)
        
        self.logger.info(f"Agent {agent_id} registered")
        
        # Notify other agents
        await self.broadcast_message(
            sender_id="communication_hub",
            message_type=MessageType.ALERT,
            content={"event": "agent_registered", "agent_id": agent_id},
            priority=MessagePriority.LOW
        )
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        self.active_agents.discard(agent_id)
        await self.redis_client.srem("active_agents", agent_id)
        
        self.logger.info(f"Agent {agent_id} unregistered")
        
        # Notify other agents
        await self.broadcast_message(
            sender_id="communication_hub",
            message_type=MessageType.ALERT,
            content={"event": "agent_unregistered", "agent_id": agent_id},
            priority=MessagePriority.LOW
        )
    
    async def send_message(self, message: CommunicationMessage):
        """Send a message to specific agent(s)"""
        try:
            # Validate recipient
            if message.recipient_id != "all" and message.recipient_id not in self.active_agents:
                self.logger.warning(f"Recipient {message.recipient_id} not active")
                return False
            
            # Convert message to dict
            message_dict = asdict(message)
            message_dict["timestamp"] = message.timestamp.isoformat()
            if message_dict["expires_at"]:
                message_dict["expires_at"] = message.expires_at.isoformat()
            message_dict["message_type"] = message.message_type.value
            message_dict["priority"] = message.priority.value
            
            # Send via Kafka if available
            if self.kafka_producer:
                try:
                    topic = f"{settings.KAFKA_TOPIC_PREFIX}_communications"
                    self.kafka_producer.send(
                        topic,
                        key=message.recipient_id,
                        value=message_dict
                    )
                    self.kafka_producer.flush()
                except KafkaError as e:
                    self.logger.error(f"Kafka send failed: {e}")
                    # Fallback to Redis
                    await self._send_via_redis(message_dict)
            else:
                # Use Redis
                await self._send_via_redis(message_dict)
            
            # Store in message history
            self.message_history.append(message_dict)
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-500:]
            
            self.logger.info(f"Message sent: {message.sender_id} -> {message.recipient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    async def _send_via_redis(self, message_dict: Dict[str, Any]):
        """Send message via Redis"""
        if message_dict["recipient_id"] == "all":
            # Broadcast to all agents
            for agent_id in self.active_agents:
                key = f"messages:{agent_id}"
                await self.redis_client.lpush(key, json.dumps(message_dict))
                await self.redis_client.expire(key, 86400)
        else:
            # Send to specific agent
            key = f"messages:{message_dict['recipient_id']}"
            await self.redis_client.lpush(key, json.dumps(message_dict))
            await self.redis_client.expire(key, 86400)
    
    async def broadcast_message(self, sender_id: str, message_type: MessageType, content: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM):
        """Broadcast message to all agents"""
        message = CommunicationMessage(
            id=f"broadcast_{int(datetime.now().timestamp())}",
            sender_id=sender_id,
            recipient_id="all",
            message_type=message_type,
            priority=priority,
            content=content,
            timestamp=datetime.now()
        )
        
        await self.send_message(message)
    
    async def get_messages_for_agent(self, agent_id: str) -> List[CommunicationMessage]:
        """Get pending messages for an agent"""
        messages = []
        key = f"messages:{agent_id}"
        
        while True:
            message_data = await self.redis_client.rpop(key)
            if not message_data:
                break
            
            try:
                data = json.loads(message_data)
                
                # Convert back to proper types
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                if data["expires_at"]:
                    data["expires_at"] = datetime.fromisoformat(data["expires_at"])
                data["message_type"] = MessageType(data["message_type"])
                data["priority"] = MessagePriority(data["priority"])
                
                # Check if message has expired
                if data["expires_at"] and datetime.now() > data["expires_at"]:
                    continue
                
                message = CommunicationMessage(**data)
                messages.append(message)
                
            except Exception as e:
                self.logger.error(f"Error parsing message for {agent_id}: {e}")
        
        return messages
    
    async def coordinate_task(self, coordinator_id: str, task_description: str, required_agents: List[str], task_data: Dict[str, Any]):
        """Coordinate a multi-agent task"""
        coordination_id = f"coord_{int(datetime.now().timestamp())}"
        
        # Send coordination request to required agents
        for agent_id in required_agents:
            message = CommunicationMessage(
                id=f"{coordination_id}_{agent_id}",
                sender_id=coordinator_id,
                recipient_id=agent_id,
                message_type=MessageType.TASK_COORDINATION,
                priority=MessagePriority.HIGH,
                content={
                    "coordination_id": coordination_id,
                    "task_description": task_description,
                    "task_data": task_data,
                    "required_agents": required_agents,
                    "coordinator": coordinator_id
                },
                timestamp=datetime.now(),
                requires_response=True,
                correlation_id=coordination_id
            )
            
            await self.send_message(message)
        
        self.logger.info(f"Task coordination initiated: {coordination_id}")
        return coordination_id
    
    async def share_knowledge(self, sender_id: str, knowledge_type: str, knowledge_data: Dict[str, Any], target_agents: Optional[List[str]] = None):
        """Share knowledge between agents"""
        recipients = target_agents or list(self.active_agents)
        
        for agent_id in recipients:
            if agent_id != sender_id:  # Don't send to self
                message = CommunicationMessage(
                    id=f"knowledge_{sender_id}_{agent_id}_{int(datetime.now().timestamp())}",
                    sender_id=sender_id,
                    recipient_id=agent_id,
                    message_type=MessageType.KNOWLEDGE_SHARING,
                    priority=MessagePriority.MEDIUM,
                    content={
                        "knowledge_type": knowledge_type,
                        "data": knowledge_data,
                        "source_agent": sender_id
                    },
                    timestamp=datetime.now()
                )
                
                await self.send_message(message)
        
        self.logger.info(f"Knowledge shared by {sender_id}: {knowledge_type}")
    
    async def send_alert(self, sender_id: str, alert_type: str, alert_data: Dict[str, Any], priority: MessagePriority = MessagePriority.HIGH):
        """Send alert to all agents"""
        await self.broadcast_message(
            sender_id=sender_id,
            message_type=MessageType.ALERT,
            content={
                "alert_type": alert_type,
                "data": alert_data,
                "source_agent": sender_id
            },
            priority=priority
        )
        
        self.logger.warning(f"Alert sent by {sender_id}: {alert_type}")
    
    async def request_resource(self, requester_id: str, resource_type: str, resource_details: Dict[str, Any], target_agent: Optional[str] = None):
        """Request resource from another agent"""
        recipient = target_agent or "all"
        
        message = CommunicationMessage(
            id=f"resource_req_{requester_id}_{int(datetime.now().timestamp())}",
            sender_id=requester_id,
            recipient_id=recipient,
            message_type=MessageType.RESOURCE_REQUEST,
            priority=MessagePriority.MEDIUM,
            content={
                "resource_type": resource_type,
                "details": resource_details,
                "requester": requester_id
            },
            timestamp=datetime.now(),
            requires_response=True
        )
        
        await self.send_message(message)
        self.logger.info(f"Resource request sent by {requester_id}: {resource_type}")
    
    async def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        stats = {
            "active_agents": len(self.active_agents),
            "total_messages": len(self.message_history),
            "message_types": {},
            "agent_activity": {}
        }
        
        # Analyze message history
        for message in self.message_history[-100:]:  # Last 100 messages
            msg_type = message.get("message_type", "unknown")
            sender = message.get("sender_id", "unknown")
            
            stats["message_types"][msg_type] = stats["message_types"].get(msg_type, 0) + 1
            stats["agent_activity"][sender] = stats["agent_activity"].get(sender, 0) + 1
        
        return stats
    
    async def cleanup_expired_messages(self):
        """Clean up expired messages"""
        current_time = datetime.now()
        cleaned_count = 0
        
        for agent_id in self.active_agents:
            key = f"messages:{agent_id}"
            messages = await self.redis_client.lrange(key, 0, -1)
            
            valid_messages = []
            for message_data in messages:
                try:
                    data = json.loads(message_data)
                    if data.get("expires_at"):
                        expires_at = datetime.fromisoformat(data["expires_at"])
                        if current_time > expires_at:
                            cleaned_count += 1
                            continue
                    
                    valid_messages.append(message_data)
                    
                except Exception as e:
                    self.logger.error(f"Error processing message during cleanup: {e}")
                    cleaned_count += 1
            
            # Replace with valid messages
            if len(valid_messages) != len(messages):
                await self.redis_client.delete(key)
                if valid_messages:
                    await self.redis_client.lpush(key, *valid_messages)
                    await self.redis_client.expire(key, 86400)
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} expired messages")
    
    async def start_background_tasks(self):
        """Start background maintenance tasks"""
        asyncio.create_task(self._periodic_cleanup())
        asyncio.create_task(self._kafka_consumer_loop())
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired messages"""
        while True:
            try:
                await self.cleanup_expired_messages()
                await asyncio.sleep(3600)  # Clean every hour
            except Exception as e:
                self.logger.error(f"Error in periodic cleanup: {e}")
                await asyncio.sleep(300)
    
    async def _kafka_consumer_loop(self):
        """Kafka consumer loop for real-time message processing"""
        if not self.kafka_consumer:
            return
        
        while True:
            try:
                message_pack = self.kafka_consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        await self._process_kafka_message(message.value)
                
            except Exception as e:
                self.logger.error(f"Error in Kafka consumer loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_kafka_message(self, message_data: Dict[str, Any]):
        """Process message received from Kafka"""
        try:
            # Convert timestamps back
            message_data["timestamp"] = datetime.fromisoformat(message_data["timestamp"])
            if message_data.get("expires_at"):
                message_data["expires_at"] = datetime.fromisoformat(message_data["expires_at"])
            
            # Convert enums back
            message_data["message_type"] = MessageType(message_data["message_type"])
            message_data["priority"] = MessagePriority(message_data["priority"])
            
            # Create message object
            message = CommunicationMessage(**message_data)
            
            # Process based on message type
            if message.message_type == MessageType.CRISIS_NOTIFICATION:
                await self._handle_crisis_notification(message)
            elif message.message_type == MessageType.PERFORMANCE_FEEDBACK:
                await self._handle_performance_feedback(message)
            
        except Exception as e:
            self.logger.error(f"Error processing Kafka message: {e}")
    
    async def _handle_crisis_notification(self, message: CommunicationMessage):
        """Handle crisis notifications"""
        self.logger.critical(f"Crisis notification from {message.sender_id}: {message.content}")
        
        # Broadcast to all agents with high priority
        await self.broadcast_message(
            sender_id="communication_hub",
            message_type=MessageType.ALERT,
            content={
                "alert_type": "crisis_escalation",
                "original_message": message.content,
                "source_agent": message.sender_id
            },
            priority=MessagePriority.CRITICAL
        )
    
    async def _handle_performance_feedback(self, message: CommunicationMessage):
        """Handle performance feedback messages"""
        # Store performance feedback for analysis
        key = f"performance_feedback:{message.sender_id}"
        data = {
            "timestamp": message.timestamp.isoformat(),
            "content": message.content
        }
        
        await self.redis_client.lpush(key, json.dumps(data))
        await self.redis_client.ltrim(key, 0, 99)  # Keep last 100 entries
        await self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days


# Global communication hub instance
communication_hub = CommunicationHub()

