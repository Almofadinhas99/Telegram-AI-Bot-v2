from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class UserPlan(str, Enum):
    FREE = "free"
    MINI = "mini"
    STARTER = "starter"
    PRO = "pro"
    PREMIUM = "premium"
    ULTIMATE = "ultimate"
    ALPHA = "alpha"

class User(BaseModel):
    id: Optional[int] = None
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    plan: UserPlan = UserPlan.FREE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Usage tracking
    daily_gpt4o_messages: int = 0
    daily_gpt4_messages: int = 0
    monthly_images: int = 0
    monthly_music: int = 0
    monthly_claude_tokens: int = 0
    
    # Reset dates
    last_daily_reset: Optional[datetime] = None
    last_monthly_reset: Optional[datetime] = None

class PlanLimits(BaseModel):
    plan: UserPlan
    price_usd: float
    price_brl: Optional[float] = None
    
    # Daily limits
    daily_gpt4o_messages: int
    daily_gpt4_messages: int
    
    # Monthly limits
    monthly_images: int
    monthly_music: int
    monthly_claude_tokens: int
    
    # Features
    has_commercial_rights: bool = False
    has_priority_queue: bool = False
    has_stealth_mode: bool = False

# Plan configurations based on the bot description
PLAN_CONFIGS = {
    UserPlan.FREE: PlanLimits(
        plan=UserPlan.FREE,
        price_usd=0.0,
        daily_gpt4o_messages=10,
        daily_gpt4_messages=0,
        monthly_images=5,
        monthly_music=0,
        monthly_claude_tokens=0
    ),
    UserPlan.MINI: PlanLimits(
        plan=UserPlan.MINI,
        price_usd=3.80,
        daily_gpt4o_messages=100,
        daily_gpt4_messages=0,
        monthly_images=10,
        monthly_music=5,
        monthly_claude_tokens=0
    ),
    UserPlan.STARTER: PlanLimits(
        plan=UserPlan.STARTER,
        price_usd=7.97,
        daily_gpt4o_messages=0,
        daily_gpt4_messages=25,
        monthly_images=30,
        monthly_music=10,
        monthly_claude_tokens=0
    ),
    UserPlan.PRO: PlanLimits(
        plan=UserPlan.PRO,
        price_usd=19.99,
        daily_gpt4o_messages=100,
        daily_gpt4_messages=0,
        monthly_images=50,
        monthly_music=10,
        monthly_videos=0,
        monthly_claude_tokens=0
    ),
    UserPlan.PREMIUM: PlanLimits(
        plan=UserPlan.PREMIUM,
        price_usd=12.97,
        daily_gpt4o_messages=0,
        daily_gpt4_messages=50,
        monthly_images=100,
        monthly_music=20,
        monthly_claude_tokens=0
    ),
    UserPlan.ULTIMATE: PlanLimits(
        plan=UserPlan.ULTIMATE,
        price_usd=18.38,
        daily_gpt4o_messages=0,
        daily_gpt4_messages=100,
        monthly_images=200,
        monthly_music=50,
        monthly_claude_tokens=0
    ),
    UserPlan.ALPHA: PlanLimits(
        plan=UserPlan.ALPHA,
        price_usd=44.95,
        daily_gpt4o_messages=-1,  # Unlimited
        daily_gpt4_messages=-1,   # Unlimited
        monthly_images=-1,        # Unlimited
        monthly_music=200,
        monthly_claude_tokens=3000000,  # 3M tokens
        has_commercial_rights=True,
        has_priority_queue=True
    )
}
