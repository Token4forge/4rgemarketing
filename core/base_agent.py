"""
Base Agent Framework for AI Marketing System
"""
import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import redis
import openai
from config.settings import settings, AGENT_CONFIGS

# Import business context loader if available
try:
    from business_info_loader import get_business_loader, BusinessContext, WebsiteInfo
    BUSINESS_CONTEXT_AVAILABLE = True
except ImportError:
    BUSINESS_CONTEXT_AVAILABLE = False
    BusinessContext = None
    WebsiteInfo = None


class AgentStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    LEARNING = "learning"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str
    agent_id: str
    task_type: str
    priority: TaskPriority
    data: Dict[str, Any]
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentPerformance:
    """Tracks agent performance metrics"""
    agent_id: str
    metric_name: str
    value: float
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None


@dataclass
class AgentMessage:
    """Inter-agent communication message"""
    id: str
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: TaskPriority = TaskPriority.MEDIUM


class BaseAgent(ABC):
    """Base class for all AI marketing agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = AgentStatus.INACTIVE
        self.logger = self._setup_logger()
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.performance_model = RandomForestRegressor(n_estimators=100)
        self.learning_data = []
        self.last_update = datetime.now()
        self.task_queue = asyncio.Queue()
        self.message_handlers = {}
        self.performance_metrics = {}
        
        # Business context integration (optional)
        self.business_loader = None
        self.business_context = None
        if BUSINESS_CONTEXT_AVAILABLE:
            try:
                self.business_loader = get_business_loader()
                self.business_context = self.business_loader.get_business_context()
                self.logger.info("Business context loaded successfully")
            except Exception as e:
                self.logger.warning(f"Could not load business context: {e}")
        
        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    def _setup_logger(self) -> logging.Logger:
        """Setup agent-specific logger"""
        logger = logging.getLogger(f"agent.{self.agent_id}")
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.agent_id} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def start(self):
        """Start the agent"""
        self.logger.info(f"Starting agent {self.agent_id}")
        self.status = AgentStatus.ACTIVE
        
        # Start background tasks
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._performance_monitor())
        asyncio.create_task(self._learning_loop())
        
        await self.initialize()
    
    async def stop(self):
        """Stop the agent"""
        self.logger.info(f"Stopping agent {self.agent_id}")
        self.status = AgentStatus.INACTIVE
        await self.cleanup()
    
    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific components"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup agent resources"""
        pass
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a specific task"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    async def add_task(self, task: AgentTask):
        """Add a task to the agent's queue"""
        await self.task_queue.put(task)
        self.logger.info(f"Task {task.id} added to queue")
    
    async def _task_processor(self):
        """Process tasks from the queue"""
        while self.status == AgentStatus.ACTIVE:
            try:
                # Get task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Check if task should be executed now
                if task.scheduled_at and task.scheduled_at > datetime.now():
                    # Re-queue for later
                    await asyncio.sleep(1)
                    await self.task_queue.put(task)
                    continue
                
                # Process the task
                start_time = time.time()
                try:
                    result = await self.process_task(task)
                    task.result = result
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    
                    # Record performance
                    execution_time = time.time() - start_time
                    await self._record_performance("task_execution_time", execution_time, {"task_type": task.task_type})
                    
                    self.logger.info(f"Task {task.id} completed successfully")
                    
                except Exception as e:
                    task.error = str(e)
                    task.status = "failed"
                    self.logger.error(f"Task {task.id} failed: {e}")
                    
                    # Record failure
                    await self._record_performance("task_failure_rate", 1.0, {"task_type": task.task_type})
                
                # Store task result
                await self._store_task_result(task)
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(5)
    
    async def _performance_monitor(self):
        """Monitor agent performance"""
        while self.status == AgentStatus.ACTIVE:
            try:
                # Collect performance metrics
                metrics = await self._collect_performance_metrics()
                
                # Store metrics
                for metric_name, value in metrics.items():
                    await self._record_performance(metric_name, value)
                
                # Check for performance issues
                await self._check_performance_thresholds()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.config.get("update_frequency", 300))
                
            except Exception as e:
                self.logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(60)
    
    async def _learning_loop(self):
        """Continuous learning loop"""
        while self.status == AgentStatus.ACTIVE:
            try:
                if len(self.learning_data) >= settings.LEARNING_BATCH_SIZE:
                    self.status = AgentStatus.LEARNING
                    await self._update_models()
                    self.status = AgentStatus.ACTIVE
                
                await asyncio.sleep(3600)  # Learn every hour
                
            except Exception as e:
                self.logger.error(f"Error in learning loop: {e}")
                self.status = AgentStatus.ACTIVE
                await asyncio.sleep(300)
    
    async def _collect_performance_metrics(self) -> Dict[str, float]:
        """Collect current performance metrics"""
        metrics = {}
        
        # Queue size
        metrics["queue_size"] = self.task_queue.qsize()
        
        # Memory usage (simplified)
        metrics["memory_usage"] = len(self.learning_data)
        
        # Time since last update
        time_diff = (datetime.now() - self.last_update).total_seconds()
        metrics["time_since_update"] = time_diff
        
        return metrics
    
    async def _record_performance(self, metric_name: str, value: float, context: Optional[Dict[str, Any]] = None):
        """Record a performance metric"""
        performance = AgentPerformance(
            agent_id=self.agent_id,
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            context=context
        )
        
        # Store in Redis for real-time access
        key = f"performance:{self.agent_id}:{metric_name}"
        data = asdict(performance)
        data["timestamp"] = data["timestamp"].isoformat()
        
        await self.redis_client.setex(key, 3600, json.dumps(data))
        
        # Add to learning data
        self.learning_data.append({
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.now(),
            "context": context or {}
        })
        
        # Keep only recent data
        if len(self.learning_data) > 1000:
            self.learning_data = self.learning_data[-500:]
    
    async def _check_performance_thresholds(self):
        """Check if performance is below thresholds"""
        for metric_name, threshold in self.config.get("performance_thresholds", {}).items():
            recent_values = [
                item["value"] for item in self.learning_data[-10:]
                if item["metric"] == metric_name
            ]
            
            if recent_values:
                avg_value = np.mean(recent_values)
                if avg_value < threshold:
                    self.logger.warning(f"Performance threshold breach: {metric_name} = {avg_value} < {threshold}")
                    await self._handle_performance_issue(metric_name, avg_value, threshold)
    
    async def _handle_performance_issue(self, metric_name: str, current_value: float, threshold: float):
        """Handle performance issues"""
        # Implement performance recovery strategies
        self.logger.info(f"Implementing recovery strategy for {metric_name}")
        
        # Could trigger retraining, parameter adjustment, etc.
        if metric_name == "task_execution_time" and current_value > threshold:
            # Reduce task complexity or increase resources
            pass
        elif metric_name == "task_failure_rate" and current_value > threshold:
            # Review and improve error handling
            pass
    
    async def _update_models(self):
        """Update machine learning models with new data"""
        if len(self.learning_data) < 10:
            return
        
        try:
            # Prepare training data
            X, y = self._prepare_training_data()
            
            if len(X) > 0:
                # Update performance prediction model
                self.performance_model.fit(X, y)
                
                # Calculate model accuracy
                predictions = self.performance_model.predict(X)
                mse = mean_squared_error(y, predictions)
                
                await self._record_performance("model_mse", mse)
                self.logger.info(f"Model updated with MSE: {mse}")
        
        except Exception as e:
            self.logger.error(f"Error updating models: {e}")
    
    def _prepare_training_data(self):
        """Prepare training data from learning history"""
        X, y = [], []
        
        for item in self.learning_data:
            if item["metric"] in ["task_execution_time", "success_rate"]:
                # Create feature vector from context
                features = [
                    item["timestamp"].hour,  # Hour of day
                    item["timestamp"].weekday(),  # Day of week
                    len(str(item["context"])),  # Context complexity
                ]
                
                X.append(features)
                y.append(item["value"])
        
        return np.array(X), np.array(y)
    
    async def _store_task_result(self, task: AgentTask):
        """Store task result in Redis"""
        key = f"task_result:{task.id}"
        data = asdict(task)
        
        # Convert datetime objects to strings
        for field in ["created_at", "scheduled_at", "completed_at"]:
            if data[field]:
                data[field] = data[field].isoformat()
        
        await self.redis_client.setex(key, 86400, json.dumps(data))  # Store for 24 hours
    
    async def send_message(self, recipient_id: str, message_type: str, content: Dict[str, Any], priority: TaskPriority = TaskPriority.MEDIUM):
        """Send message to another agent"""
        message = AgentMessage(
            id=f"{self.agent_id}_{recipient_id}_{int(time.time())}",
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            priority=priority
        )
        
        # Store message in Redis for recipient
        key = f"messages:{recipient_id}"
        data = asdict(message)
        data["timestamp"] = data["timestamp"].isoformat()
        
        await self.redis_client.lpush(key, json.dumps(data))
        await self.redis_client.expire(key, 86400)  # Expire after 24 hours
        
        self.logger.info(f"Message sent to {recipient_id}: {message_type}")
    
    async def receive_messages(self) -> List[AgentMessage]:
        """Receive messages from other agents"""
        key = f"messages:{self.agent_id}"
        messages = []
        
        while True:
            message_data = await self.redis_client.rpop(key)
            if not message_data:
                break
            
            try:
                data = json.loads(message_data)
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                data["priority"] = TaskPriority(data["priority"])
                
                message = AgentMessage(**data)
                messages.append(message)
                
            except Exception as e:
                self.logger.error(f"Error parsing message: {e}")
        
        return messages
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
    
    async def process_messages(self):
        """Process incoming messages"""
        messages = await self.receive_messages()
        
        for message in messages:
            handler = self.message_handlers.get(message.message_type)
            if handler:
                try:
                    await handler(message)
                except Exception as e:
                    self.logger.error(f"Error processing message {message.id}: {e}")
            else:
                self.logger.warning(f"No handler for message type: {message.message_type}")
    
    async def predict_performance(self, context: Dict[str, Any]) -> float:
        """Predict performance for given context"""
        try:
            if hasattr(self.performance_model, "predict"):
                # Create feature vector from context
                features = [
                    datetime.now().hour,
                    datetime.now().weekday(),
                    len(str(context))
                ]
                
                prediction = self.performance_model.predict([features])[0]
                return float(prediction)
        except Exception as e:
            self.logger.error(f"Error predicting performance: {e}")
        
        return 0.5  # Default prediction
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "queue_size": self.task_queue.qsize(),
            "last_update": self.last_update.isoformat(),
            "capabilities": self.get_capabilities(),
            "performance_metrics": self.performance_metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "status": "healthy",
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check Redis connection
        try:
            await self.redis_client.ping()
            health["checks"]["redis"] = "ok"
        except Exception as e:
            health["checks"]["redis"] = f"error: {e}"
            health["status"] = "unhealthy"
        
        # Check queue status
        queue_size = self.task_queue.qsize()
        if queue_size > 100:
            health["checks"]["queue"] = f"warning: {queue_size} tasks"
            health["status"] = "degraded"
        else:
            health["checks"]["queue"] = "ok"
        
        # Check learning data
        if len(self.learning_data) > 0:
            health["checks"]["learning"] = "ok"
        else:
            health["checks"]["learning"] = "no_data"
        
        return health
    
    # Business Context Helper Methods
    def get_business_context(self) -> Optional[BusinessContext]:
        """Get current business context"""
        return self.business_context
    
    def get_website_context(self, website_name: str) -> Dict[str, Any]:
        """Get complete context for a specific website"""
        if not self.business_loader or not self.business_context:
            return {}
        
        try:
            website = self.business_loader.get_website_info(website_name)
            if not website:
                return {}
            
            return {
                "website": website,
                "brand_voice": self.business_loader.get_brand_voice_for_website(website_name),
                "target_audience": self.business_loader.get_target_audience_for_website(website_name),
                "content_themes": self.business_loader.get_content_themes_for_website(website_name),
                "compliance": self.business_loader.get_compliance_requirements()
            }
        except Exception as e:
            self.logger.error(f"Error getting website context for {website_name}: {e}")
            return {}
    
    def get_high_priority_websites(self) -> List[Any]:
        """Get list of high priority websites"""
        if not self.business_loader:
            return []
        try:
            return self.business_loader.get_high_priority_websites()
        except Exception as e:
            self.logger.error(f"Error getting high priority websites: {e}")
            return []
    
    def get_brand_voice_for_content(self, website_name: str) -> Dict[str, Any]:
        """Get brand voice configuration for content creation"""
        if not self.business_loader:
            return {"tone": "professional", "voice": "helpful"}
        
        try:
            return self.business_loader.get_brand_voice_for_website(website_name)
        except Exception as e:
            self.logger.error(f"Error getting brand voice for {website_name}: {e}")
            return {"tone": "professional", "voice": "helpful"}
    
    def get_compliance_requirements(self) -> Dict[str, Any]:
        """Get compliance requirements for content and campaigns"""
        if not self.business_loader:
            return {}
        try:
            return self.business_loader.get_compliance_requirements()
        except Exception as e:
            self.logger.error(f"Error getting compliance requirements: {e}")
            return {}

