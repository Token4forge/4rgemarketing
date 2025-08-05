"""
Business Information Loader Module for AI Marketing System
Provides centralized access to business context and configuration data
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import jsonschema
from pathlib import Path


@dataclass
class WebsiteInfo:
    """Website information structure"""
    name: str
    url: str
    description: str
    target_audience: str
    key_services: List[str]
    unique_selling_points: List[str]
    call_to_action: str
    priority: str
    conversion_goals: List[str]
    pricing_model: Optional[str] = None
    status: Optional[str] = None


@dataclass
class BusinessContext:
    """Complete business context for agents"""
    company_portfolio: Dict[str, Any]
    websites: List[WebsiteInfo]
    brand_guidelines: Dict[str, Any]
    technical_config: Dict[str, Any]
    agent_configurations: Dict[str, Any]
    success_metrics: Dict[str, Any]
    content_strategy: Dict[str, Any]
    audience_segments: Dict[str, Any]
    compliance: Dict[str, Any]
    marketing_messages: Dict[str, List[str]]
    call_to_actions: Dict[str, str]
    content_themes: List[str]
    promotional_priorities: Dict[str, Any]


class BusinessInfoLoader:
    """Loads and manages business information for AI agents"""
    
    def __init__(self, config_path: Optional[str] = None, schema_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Set default paths
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "business_info_for_agents.json")
        if schema_path is None:
            schema_path = os.path.join(os.path.dirname(__file__), "business_info_schema.json")
            
        self.config_path = config_path
        self.schema_path = schema_path
        self._business_context: Optional[BusinessContext] = None
        self._last_loaded: Optional[datetime] = None
        
    def load_business_info(self, validate: bool = True) -> BusinessContext:
        """Load business information from JSON file"""
        try:
            # Check if file exists
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Business info file not found: {self.config_path}")
            
            # Load JSON data
            with open(self.config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Validate against schema if requested and schema exists
            if validate and os.path.exists(self.schema_path):
                self._validate_business_info(data)
            
            # Convert to structured format
            business_context = self._parse_business_data(data)
            
            # Cache the loaded data
            self._business_context = business_context
            self._last_loaded = datetime.now()
            
            self.logger.info("Business information loaded successfully")
            return business_context
            
        except Exception as e:
            self.logger.error(f"Error loading business information: {e}")
            raise
    
    def _validate_business_info(self, data: Dict[str, Any]) -> None:
        """Validate business info against JSON schema"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as schema_file:
                schema = json.load(schema_file)
            
            jsonschema.validate(data, schema)
            self.logger.info("Business info validation passed")
            
        except jsonschema.ValidationError as e:
            self.logger.error(f"Business info validation failed: {e.message}")
            raise
        except Exception as e:
            self.logger.error(f"Error validating business info: {e}")
            raise
    
    def _parse_business_data(self, data: Dict[str, Any]) -> BusinessContext:
        """Parse raw JSON data into structured business context"""
        # Parse websites
        websites = []
        for website_data in data.get("websites", []):
            website = WebsiteInfo(
                name=website_data["name"],
                url=website_data["url"],
                description=website_data["description"],
                target_audience=website_data["target_audience"],
                key_services=website_data["key_services"],
                unique_selling_points=website_data["unique_selling_points"],
                call_to_action=website_data["call_to_action"],
                priority=website_data.get("priority", "medium"),
                conversion_goals=website_data.get("conversion_goals", []),
                pricing_model=website_data.get("pricing_model"),
                status=website_data.get("status")
            )
            websites.append(website)
        
        # Create business context
        return BusinessContext(
            company_portfolio=data.get("company_portfolio", {}),
            websites=websites,
            brand_guidelines=data.get("brand_guidelines", {}),
            technical_config=data.get("technical_config", {}),
            agent_configurations=data.get("agent_configurations", {}),
            success_metrics=data.get("success_metrics", {}),
            content_strategy=data.get("content_strategy", {}),
            audience_segments=data.get("audience_segments", {}),
            compliance=data.get("compliance", {}),
            marketing_messages=data.get("marketing_messages", {}),
            call_to_actions=data.get("call_to_actions", {}),
            content_themes=data.get("content_themes", []),
            promotional_priorities=data.get("promotional_priorities", {})
        )
    
    def get_business_context(self, force_reload: bool = False) -> BusinessContext:
        """Get cached business context or load if not available"""
        if self._business_context is None or force_reload:
            return self.load_business_info()
        return self._business_context
    
    def get_website_info(self, website_name: str) -> Optional[WebsiteInfo]:
        """Get information for a specific website"""
        context = self.get_business_context()
        for website in context.websites:
            if website.name.lower() == website_name.lower():
                return website
        return None
    
    def get_high_priority_websites(self) -> List[WebsiteInfo]:
        """Get list of high priority websites"""
        context = self.get_business_context()
        high_priority = context.promotional_priorities.get("high", [])
        return [w for w in context.websites if w.name.lower() in [p.lower() for p in high_priority]]
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        context = self.get_business_context()
        return context.agent_configurations.get(agent_name, {})
    
    def get_brand_voice_for_website(self, website_name: str) -> Dict[str, Any]:
        """Get brand voice configuration for a specific website"""
        context = self.get_business_context()
        agent_config = context.agent_configurations.get("content_strategist", {})
        tone_adaptation = agent_config.get("tone_adaptation", {})
        
        # Get website-specific tone or fall back to general brand guidelines
        website_tone = tone_adaptation.get(website_name.lower())
        if website_tone:
            return {
                "tone": website_tone,
                "voice": context.brand_guidelines.get("overall_voice", ""),
                "keywords": context.brand_guidelines.get("tone_keywords", []),
                "avoid_words": context.brand_guidelines.get("avoid_words", [])
            }
        
        return context.brand_guidelines
    
    def get_target_audience_for_website(self, website_name: str) -> Dict[str, Any]:
        """Get target audience information for a specific website"""
        website = self.get_website_info(website_name)
        if not website:
            return {}
        
        context = self.get_business_context()
        
        # Try to match website audience with detailed segments
        for segment_name, segment_data in context.audience_segments.items():
            if any(keyword in website.target_audience.lower() 
                   for keyword in segment_name.replace("_", " ").split()):
                return segment_data
        
        # Fall back to website's basic audience info
        return {"target_audience": website.target_audience}
    
    def get_content_themes_for_website(self, website_name: str) -> List[str]:
        """Get relevant content themes for a specific website"""
        website = self.get_website_info(website_name)
        if not website:
            return []
        
        context = self.get_business_context()
        all_themes = context.content_themes
        
        # Filter themes based on website focus
        relevant_themes = []
        website_keywords = (website.description + " " + " ".join(website.key_services)).lower()
        
        for theme in all_themes:
            theme_keywords = theme.lower().split()
            if any(keyword in website_keywords for keyword in theme_keywords):
                relevant_themes.append(theme)
        
        return relevant_themes if relevant_themes else all_themes
    
    def get_success_metrics_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get success metrics relevant to a specific agent"""
        context = self.get_business_context()
        
        # Map agents to relevant metrics
        agent_metric_mapping = {
            "content_strategist": ["website_performance", "seo_targets"],
            "social_media_orchestrator": ["social_media_kpis"],
            "email_marketing_maestro": ["email_marketing_metrics"],
            "seo_domination": ["seo_targets", "website_performance"],
            "analytics_intelligence": ["website_performance", "social_media_kpis", "email_marketing_metrics"]
        }
        
        relevant_metrics = {}
        metric_keys = agent_metric_mapping.get(agent_name, [])
        
        for key in metric_keys:
            if key in context.success_metrics:
                relevant_metrics[key] = context.success_metrics[key]
        
        return relevant_metrics if relevant_metrics else context.success_metrics
    
    def get_seasonal_campaigns(self) -> Dict[str, Any]:
        """Get current and upcoming seasonal campaigns"""
        context = self.get_business_context()
        return context.content_strategy.get("seasonal_campaigns", {})
    
    def get_compliance_requirements(self) -> Dict[str, Any]:
        """Get compliance requirements for all platforms"""
        context = self.get_business_context()
        return context.compliance
    
    def reload_if_modified(self) -> bool:
        """Reload business info if file has been modified"""
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(self.config_path))
            if self._last_loaded is None or file_mtime > self._last_loaded:
                self.load_business_info()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking file modification: {e}")
            return False
    
    def export_agent_context(self, agent_name: str) -> Dict[str, Any]:
        """Export complete context relevant to a specific agent"""
        context = self.get_business_context()
        
        return {
            "company_info": context.company_portfolio,
            "websites": [
                {
                    "name": w.name,
                    "url": w.url,
                    "description": w.description,
                    "target_audience": w.target_audience,
                    "priority": w.priority,
                    "conversion_goals": w.conversion_goals
                } for w in context.websites
            ],
            "brand_guidelines": context.brand_guidelines,
            "agent_config": self.get_agent_config(agent_name),
            "success_metrics": self.get_success_metrics_for_agent(agent_name),
            "content_themes": context.content_themes,
            "marketing_messages": context.marketing_messages,
            "compliance": context.compliance
        }


# Global instance for easy access
_business_loader = None

def get_business_loader() -> BusinessInfoLoader:
    """Get global business info loader instance"""
    global _business_loader
    if _business_loader is None:
        _business_loader = BusinessInfoLoader()
    return _business_loader

def load_business_context() -> BusinessContext:
    """Load business context using global loader"""
    return get_business_loader().get_business_context()

def get_website_context(website_name: str) -> Dict[str, Any]:
    """Get complete context for a specific website"""
    loader = get_business_loader()
    website = loader.get_website_info(website_name)
    if not website:
        return {}
    
    return {
        "website": website,
        "brand_voice": loader.get_brand_voice_for_website(website_name),
        "target_audience": loader.get_target_audience_for_website(website_name),
        "content_themes": loader.get_content_themes_for_website(website_name),
        "compliance": loader.get_compliance_requirements()
    }
