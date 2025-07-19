import logging
from datetime import datetime, timedelta
from typing import Optional
from models.user import User, UserPlan

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        # For now, we'll use in-memory storage
        # Later this will be replaced with Supabase integration
        self.users = {}

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one"""
        
        if telegram_id in self.users:
            return self.users[telegram_id]
        
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            plan=UserPlan.FREE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_daily_reset=datetime.now(),
            last_monthly_reset=datetime.now()
        )
        
        self.users[telegram_id] = user
        logger.info(f"Created new user: {telegram_id}")
        
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return self.users.get(telegram_id)

    async def update_user_usage(self, user: User) -> None:
        """Update user usage and reset counters if needed"""
        now = datetime.now()
        
        # Reset daily counters if needed
        if user.last_daily_reset and (now - user.last_daily_reset).days >= 1:
            user.daily_gpt4o_messages = 0
            user.daily_gpt4_messages = 0
            user.last_daily_reset = now
            logger.info(f"Reset daily counters for user {user.telegram_id}")
        
        # Reset monthly counters if needed
        if user.last_monthly_reset and (now - user.last_monthly_reset).days >= 30:
            user.monthly_images = 0
            user.monthly_music = 0
            user.monthly_claude_tokens = 0
            user.last_monthly_reset = now
            logger.info(f"Reset monthly counters for user {user.telegram_id}")
        
        user.updated_at = now
        self.users[user.telegram_id] = user

    async def upgrade_user_plan(self, telegram_id: int, new_plan: UserPlan) -> bool:
        """Upgrade user plan"""
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
        
        user.plan = new_plan
        user.updated_at = datetime.now()
        self.users[telegram_id] = user
        
        logger.info(f"Upgraded user {telegram_id} to plan {new_plan}")
        return True

    async def get_user_stats(self, telegram_id: int) -> Optional[dict]:
        """Get user usage statistics"""
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        return {
            "telegram_id": user.telegram_id,
            "plan": user.plan,
            "daily_gpt4o_messages": user.daily_gpt4o_messages,
            "daily_gpt4_messages": user.daily_gpt4_messages,
            "monthly_images": user.monthly_images,
            "monthly_music": user.monthly_music,
            "monthly_claude_tokens": user.monthly_claude_tokens,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

