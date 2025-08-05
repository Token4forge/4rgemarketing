"""
AI Marketing System - Main Application
Production-ready multi-agent marketing system
"""
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import settings, AGENT_CONFIGS
from core.base_agent import BaseAgent, AgentTask, TaskPriority, AgentStatus
from core.communication import communication_hub, MessageType, MessagePriority
from agents.content_strategist import ContentStrategistAgent
from agents.social_media_orchestrator import SocialMediaOrchestratorAgent

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_marketing_system")

# FastAPI app
app = FastAPI(
    title="AI Marketing System",
    description="Production-ready AI Marketing Agent System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent registry
agent_registry: Dict[str, BaseAgent] = {}
system_status = {
    "status": "initializing",
    "start_time": None,
    "agents_active": 0,
    "total_tasks_processed": 0,
    "last_health_check": None
}


class AgentManager:
    """Manages all AI marketing agents"""
    
    def __init__(self):
        self.agents = {}
        self.running = False
        
    async def initialize_agents(self):
        """Initialize all marketing agents"""
        logger.info("Initializing AI Marketing Agents...")
        
        # Initialize agents
        agents_to_create = [
            ("content_strategist", ContentStrategistAgent),
            ("social_media_orchestrator", SocialMediaOrchestratorAgent),
            # Add other agents here as they're implemented
        ]
        
        for agent_id, agent_class in agents_to_create:
            try:
                logger.info(f"Creating {agent_id}...")
                agent = agent_class(agent_id)
                await agent.start()
                self.agents[agent_id] = agent
                agent_registry[agent_id] = agent
                
                # Register with communication hub
                await communication_hub.register_agent(agent_id)
                
                logger.info(f"Agent {agent_id} initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_id}: {e}")
                raise
        
        # Start communication hub background tasks
        await communication_hub.start_background_tasks()
        
        self.running = True
        system_status["status"] = "running"
        system_status["start_time"] = datetime.now()
        system_status["agents_active"] = len(self.agents)
        
        logger.info(f"All agents initialized. System is now running with {len(self.agents)} agents.")
    
    async def shutdown_agents(self):
        """Shutdown all agents gracefully"""
        logger.info("Shutting down AI Marketing System...")
        
        self.running = False
        system_status["status"] = "shutting_down"
        
        # Stop all agents
        for agent_id, agent in self.agents.items():
            try:
                await agent.stop()
                await communication_hub.unregister_agent(agent_id)
                logger.info(f"Agent {agent_id} stopped")
            except Exception as e:
                logger.error(f"Error stopping agent {agent_id}: {e}")
        
        self.agents.clear()
        agent_registry.clear()
        system_status["status"] = "stopped"
        system_status["agents_active"] = 0
        
        logger.info("AI Marketing System shutdown complete")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {}
        total_queue_size = 0
        
        for agent_id, agent in self.agents.items():
            status = agent.get_status()
            agent_statuses[agent_id] = status
            total_queue_size += status.get("queue_size", 0)
        
        return {
            "system": system_status,
            "agents": agent_statuses,
            "communication": await communication_hub.get_communication_stats(),
            "performance": {
                "total_queue_size": total_queue_size,
                "average_queue_size": total_queue_size / len(self.agents) if self.agents else 0
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": system_status.copy(),
            "agents": {},
            "issues": []
        }
        
        # Check each agent
        for agent_id, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health["agents"][agent_id] = agent_health
                
                if agent_health["status"] != "healthy":
                    health["issues"].append(f"Agent {agent_id}: {agent_health['status']}")
                    if health["status"] == "healthy":
                        health["status"] = "degraded"
                        
            except Exception as e:
                health["agents"][agent_id] = {"status": "error", "error": str(e)}
                health["issues"].append(f"Agent {agent_id}: health check failed")
                health["status"] = "unhealthy"
        
        system_status["last_health_check"] = datetime.now()
        return health


# Global agent manager
agent_manager = AgentManager()


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting AI Marketing System...")
    try:
        await agent_manager.initialize_agents()
        logger.info("AI Marketing System started successfully")
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    await agent_manager.shutdown_agents()


# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Marketing System",
        "version": "1.0.0",
        "status": system_status["status"],
        "agents_active": system_status["agents_active"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health = await agent_manager.health_check()
    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)


@app.get("/status")
async def get_status():
    """Get system status"""
    return await agent_manager.get_system_status()


@app.get("/agents")
async def list_agents():
    """List all agents"""
    agents = []
    for agent_id, agent in agent_registry.items():
        agents.append({
            "id": agent_id,
            "name": agent.config.get("name", agent_id),
            "status": agent.status.value,
            "capabilities": agent.get_capabilities()
        })
    return {"agents": agents}


@app.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get specific agent status"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agent_registry[agent_id]
    return agent.get_status()


@app.post("/agents/{agent_id}/tasks")
async def create_agent_task(agent_id: str, task_data: Dict[str, Any]):
    """Create a task for specific agent"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agent_registry[agent_id]
    
    # Create task
    task = AgentTask(
        id=f"{agent_id}_{int(datetime.now().timestamp())}",
        agent_id=agent_id,
        task_type=task_data.get("task_type"),
        priority=TaskPriority(task_data.get("priority", 2)),
        data=task_data.get("data", {}),
        created_at=datetime.now()
    )
    
    # Add to agent queue
    await agent.add_task(task)
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": f"Task added to {agent_id} queue"
    }


@app.post("/content/generate")
async def generate_content(content_request: Dict[str, Any]):
    """Generate content using Content Strategist Agent"""
    if "content_strategist" not in agent_registry:
        raise HTTPException(status_code=503, detail="Content Strategist Agent not available")
    
    agent = agent_registry["content_strategist"]
    
    task = AgentTask(
        id=f"content_gen_{int(datetime.now().timestamp())}",
        agent_id="content_strategist",
        task_type="generate_content",
        priority=TaskPriority.MEDIUM,
        data=content_request,
        created_at=datetime.now()
    )
    
    await agent.add_task(task)
    
    return {
        "task_id": task.id,
        "status": "processing",
        "message": "Content generation started"
    }


@app.post("/social/post")
async def create_social_post(post_request: Dict[str, Any]):
    """Create social media post using Social Media Orchestrator"""
    if "social_media_orchestrator" not in agent_registry:
        raise HTTPException(status_code=503, detail="Social Media Orchestrator not available")
    
    agent = agent_registry["social_media_orchestrator"]
    
    task = AgentTask(
        id=f"social_post_{int(datetime.now().timestamp())}",
        agent_id="social_media_orchestrator",
        task_type="create_post",
        priority=TaskPriority.MEDIUM,
        data=post_request,
        created_at=datetime.now()
    )
    
    await agent.add_task(task)
    
    return {
        "task_id": task.id,
        "status": "processing",
        "message": "Social media post creation started"
    }


@app.get("/analytics/performance")
async def get_performance_analytics():
    """Get system performance analytics"""
    performance_data = {
        "system_uptime": (datetime.now() - system_status["start_time"]).total_seconds() if system_status["start_time"] else 0,
        "total_agents": len(agent_registry),
        "active_agents": len([a for a in agent_registry.values() if a.status == AgentStatus.ACTIVE]),
        "total_tasks_processed": system_status["total_tasks_processed"],
        "communication_stats": await communication_hub.get_communication_stats()
    }
    
    return performance_data


@app.post("/system/shutdown")
async def shutdown_system():
    """Shutdown the system gracefully"""
    await agent_manager.shutdown_agents()
    return {"message": "System shutdown initiated"}


# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(agent_manager.shutdown_agents())


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    logger.info("Starting AI Marketing System server...")
    
    # Use Railway's dynamic PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level=settings.LOG_LEVEL.lower()
    )

