"""
AI Marketing System Configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Marketing System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://marketing_admin:secure_password@localhost:5432/ai_marketing")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET: str = "your-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "ai_marketing"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Agent Configuration
    AGENT_UPDATE_INTERVAL: int = 300  # 5 minutes
    LEARNING_BATCH_SIZE: int = 100
    PERFORMANCE_THRESHOLD: float = 0.8
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    PROMETHEUS_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Agent-specific configurations
AGENT_CONFIGS = {
    "content_strategist": {
        "name": "Content Strategist Agent",
        "description": "Develops content strategies and creates high-quality content",
        "capabilities": [
            "content_generation",
            "seo_optimization", 
            "trend_analysis",
            "competitor_analysis"
        ],
        "update_frequency": 3600,  # 1 hour
        "learning_rate": 0.01
    },
    "social_media_orchestrator": {
        "name": "Social Media Orchestrator",
        "description": "Manages social media activities and engagement",
        "capabilities": [
            "social_posting",
            "engagement_management",
            "sentiment_analysis",
            "influencer_identification"
        ],
        "update_frequency": 900,  # 15 minutes
        "learning_rate": 0.02
    },
    "seo_domination": {
        "name": "SEO Domination Agent",
        "description": "Achieves top search engine rankings",
        "capabilities": [
            "keyword_research",
            "technical_seo",
            "content_optimization",
            "link_building"
        ],
        "update_frequency": 7200,  # 2 hours
        "learning_rate": 0.015
    },
    "email_marketing_maestro": {
        "name": "Email Marketing Maestro",
        "description": "Creates sophisticated email marketing campaigns",
        "capabilities": [
            "email_automation",
            "personalization",
            "segmentation",
            "deliverability_optimization"
        ],
        "update_frequency": 1800,  # 30 minutes
        "learning_rate": 0.02
    },
    "analytics_intelligence": {
        "name": "Analytics Intelligence Agent",
        "description": "Provides deep insights and analytics",
        "capabilities": [
            "data_analysis",
            "predictive_modeling",
            "attribution_modeling",
            "roi_calculation"
        ],
        "update_frequency": 3600,  # 1 hour
        "learning_rate": 0.01
    },
    "lead_generation_specialist": {
        "name": "Lead Generation Specialist",
        "description": "Identifies and qualifies leads",
        "capabilities": [
            "prospect_identification",
            "lead_scoring",
            "intent_detection",
            "outreach_automation"
        ],
        "update_frequency": 1800,  # 30 minutes
        "learning_rate": 0.025
    },
    "brand_guardian": {
        "name": "Brand Guardian Agent",
        "description": "Monitors and protects brand reputation",
        "capabilities": [
            "brand_monitoring",
            "sentiment_tracking",
            "crisis_detection",
            "reputation_management"
        ],
        "update_frequency": 600,  # 10 minutes
        "learning_rate": 0.02
    },
    "paid_advertising_optimizer": {
        "name": "Paid Advertising Optimizer",
        "description": "Manages and optimizes paid advertising campaigns",
        "capabilities": [
            "campaign_management",
            "bid_optimization",
            "audience_targeting",
            "creative_optimization"
        ],
        "update_frequency": 900,  # 15 minutes
        "learning_rate": 0.03
    },
    "customer_journey_architect": {
        "name": "Customer Journey Architect",
        "description": "Maps and optimizes customer journeys",
        "capabilities": [
            "journey_mapping",
            "personalization",
            "conversion_optimization",
            "experience_measurement"
        ],
        "update_frequency": 3600,  # 1 hour
        "learning_rate": 0.015
    }
}


# Database table configurations
DATABASE_TABLES = {
    "agents": "agent_instances",
    "tasks": "agent_tasks", 
    "performance": "agent_performance",
    "communications": "agent_communications",
    "learning_data": "agent_learning_data",
    "campaigns": "marketing_campaigns",
    "content": "content_library",
    "leads": "lead_database",
    "analytics": "analytics_data",
    "social_accounts": "social_media_accounts",
    "email_lists": "email_subscriber_lists"
}


# API endpoint configurations
API_ENDPOINTS = {
    "agents": "/api/v1/agents",
    "tasks": "/api/v1/tasks",
    "performance": "/api/v1/performance", 
    "communications": "/api/v1/communications",
    "campaigns": "/api/v1/campaigns",
    "analytics": "/api/v1/analytics",
    "dashboard": "/api/v1/dashboard"
}

