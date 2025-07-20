#!/usr/bin/env python3
"""
Main AI Bot with English interface and payment system
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.settings import settings
from services.user_service import UserService
from services.fal_service import FalService
from services.replicate_service import ReplicateService
from services.payment_service import PaymentService
from models.user import UserPlan
from bot_messages import *

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize services
user_service = UserService()
fal_service = FalService()
replicate_service = ReplicateService()
payment_service = PaymentService()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Get or create user
    bot_user = await user_service.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Send welcome message first
    await update.message.reply_text(
        get_welcome_message(), 
        parse_mode='Markdown'
    )
    
    # Then send start message
    plan_features = payment_service.get_plan_features(bot_user.plan)
    await update.message.reply_text(
        get_start_message(user.first_name, plan_features["name"]), 
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(get_help_message(), parse_mode='Markdown')

async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plans command"""
    await update.message.reply_text(get_plans_message(), parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    
    # Get user stats
    stats = await user_service.get_user_stats(user.id)
    
    if stats:
        await update.message.reply_text(
            get_status_message(stats), 
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            get_error_message("general"), 
            parse_mode='Markdown'
        )

async def upgrade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /upgrade command"""
    await update.message.reply_text(get_upgrade_message(), parse_mode='Markdown')

async def upgrade_starter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /upgrade_starter command"""
    await handle_upgrade(update, context, UserPlan.STARTER)

async def upgrade_pro_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /upgrade_pro command"""
    await handle_upgrade(update, context, UserPlan.PRO)

async def upgrade_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /upgrade_premium command"""
    await handle_upgrade(update, context, UserPlan.PREMIUM)

async def upgrade_ultimate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /upgrade_ultimate command"""
    await handle_upgrade(update, context, UserPlan.ULTIMATE)

async def handle_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE, plan: UserPlan):
    """Handle upgrade to specific plan"""
    user = update.effective_user
    
    # Get plan features
    plan_features = payment_service.get_plan_features(plan)
    
    # Create checkout session
    success_url = f"https://t.me/{context.bot.username}?start=payment_success"
    cancel_url = f"https://t.me/{context.bot.username}?start=payment_cancelled"
    
    result = await payment_service.create_checkout_session(
        user_id=user.id,
        plan=plan,
        success_url=success_url,
        cancel_url=cancel_url
    )
    
    if result["success"]:
        # Create inline keyboard with payment link
        keyboard = [
            [InlineKeyboardButton("💳 Pay Now", url=result["checkout_url"])],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
💳 **Upgrade to {plan_features['name']}**

**🎯 You'll get:**
{chr(10).join(plan_features['features'])}

**💰 Price:** {plan_features['price']}

Click "Pay Now" to complete your upgrade via Stripe.
        """
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"❌ **Payment Error**\n\n{result['error']}\n\nPlease try again later.",
            parse_mode='Markdown'
        )

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /image command"""
    if not context.args:
        await update.message.reply_text(
            get_error_message("invalid_prompt"), 
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    user = update.effective_user
    
    # Get user
    bot_user = await user_service.get_or_create_user(user.id)
    plan_features = payment_service.get_plan_features(bot_user.plan)
    
    # Check usage limits
    if bot_user.monthly_images >= plan_features["monthly_images"]:
        await update.message.reply_text(
            get_limit_exceeded_message("monthly_images", plan_features["name"]),
            parse_mode='Markdown'
        )
        return
    
    # Send "generating" message
    generating_msg = await update.message.reply_text(
        get_generating_message("image"),
        parse_mode='Markdown'
    )
    
    try:
        # Choose model based on plan
        if bot_user.plan in [UserPlan.FREE, UserPlan.STARTER]:
            model = "fal-ai/flux/schnell"
        elif bot_user.plan == UserPlan.PRO:
            model = "fal-ai/flux/dev"
        else:  # PREMIUM, ULTIMATE
            model = "fal-ai/flux-pro"
        
        # Try Fal.ai first
        result = await fal_service.generate_image(prompt, model=model)
        
        if result["success"]:
            # Update user usage
            bot_user.monthly_images += 1
            await user_service.update_user_usage(bot_user)
            
            # Send image
            await update.message.reply_photo(
                photo=result["image_url"],
                caption=get_content_ready_message("image", prompt, result['cost'], "Fal.ai FLUX"),
                parse_mode='Markdown'
            )
            
            # Delete generating message
            await generating_msg.delete()
            
        else:
            # Try Replicate as fallback
            await generating_msg.edit_text(
                "🎨 **Trying alternative model...** \n\n⏱️ Please wait",
                parse_mode='Markdown'
            )
            
            result = await replicate_service.generate_image(prompt)
            
            if result["success"]:
                # Update user usage
                bot_user.monthly_images += 1
                await user_service.update_user_usage(bot_user)
                
                # Send image
                await update.message.reply_photo(
                    photo=result["image_url"],
                    caption=get_content_ready_message("image", prompt, result['cost'], "Replicate FLUX"),
                    parse_mode='Markdown'
                )
                
                # Delete generating message
                await generating_msg.delete()
            else:
                await generating_msg.edit_text(
                    get_error_message("api_error"),
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        logger.error(f"Error in image command: {e}")
        await generating_msg.edit_text(
            get_error_message("general"),
            parse_mode='Markdown'
        )

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /video command"""
    if not context.args:
        await update.message.reply_text(
            get_error_message("invalid_prompt"), 
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    user = update.effective_user
    
    # Get user
    bot_user = await user_service.get_or_create_user(user.id)
    plan_features = payment_service.get_plan_features(bot_user.plan)
    
    # Check if plan supports videos
    if plan_features["monthly_videos"] == 0:
        await update.message.reply_text(
            f"🚫 **Video generation not available in {plan_features['name']} plan**\n\nUpgrade to PRO or higher to access video generation!\n\n👆 Use `/upgrade` to see options",
            parse_mode='Markdown'
        )
        return
    
    # Check usage limits
    if bot_user.monthly_videos >= plan_features["monthly_videos"]:
        await update.message.reply_text(
            get_limit_exceeded_message("monthly_videos", plan_features["name"]),
            parse_mode='Markdown'
        )
        return
    
    # Send "generating" message
    generating_msg = await update.message.reply_text(
        get_generating_message("video"),
        parse_mode='Markdown'
    )
    
    try:
        # Try Fal.ai first
        result = await fal_service.generate_video(prompt)
        
        if result["success"]:
            # Update user usage
            bot_user.monthly_videos += 1
            await user_service.update_user_usage(bot_user)
            
            # Send video
            await update.message.reply_video(
                video=result["video_url"],
                caption=get_content_ready_message("video", prompt, result['cost'], "Fal.ai Luma"),
                parse_mode='Markdown'
            )
            
            # Delete generating message
            await generating_msg.delete()
            
        else:
            await generating_msg.edit_text(
                get_error_message("api_error"),
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error in video command: {e}")
        await generating_msg.edit_text(
            get_error_message("general"),
            parse_mode='Markdown'
        )

async def music_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /music command"""
    if not context.args:
        await update.message.reply_text(
            get_error_message("invalid_prompt"), 
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    user = update.effective_user
    
    # Get user
    bot_user = await user_service.get_or_create_user(user.id)
    plan_features = payment_service.get_plan_features(bot_user.plan)
    
    # Check usage limits
    if bot_user.monthly_music >= plan_features["monthly_music"]:
        await update.message.reply_text(
            get_limit_exceeded_message("monthly_music", plan_features["name"]),
            parse_mode='Markdown'
        )
        return
    
    # Send "generating" message
    generating_msg = await update.message.reply_text(
        get_generating_message("music"),
        parse_mode='Markdown'
    )
    
    try:
        # Try Replicate for music generation
        result = await replicate_service.generate_music(prompt)
        
        if result["success"]:
            # Update user usage
            bot_user.monthly_music += 1
            await user_service.update_user_usage(bot_user)
            
            # Send audio
            await update.message.reply_audio(
                audio=result["audio_url"],
                caption=get_content_ready_message("music", prompt, result['cost'], "Replicate Suno"),
                parse_mode='Markdown'
            )
            
            # Delete generating message
            await generating_msg.delete()
            
        else:
            await generating_msg.edit_text(
                get_error_message("api_error"),
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error in music command: {e}")
        await generating_msg.edit_text(
            get_error_message("general"),
            parse_mode='Markdown'
        )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_payment":
        await query.edit_message_text(
            "❌ **Payment Cancelled**\n\nYou can upgrade anytime using `/upgrade`",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages (AI chat)"""
    user = update.effective_user
    message_text = update.message.text
    
    # Get or create user
    bot_user = await user_service.get_or_create_user(user.id)
    plan_features = payment_service.get_plan_features(bot_user.plan)
    
    # Check daily GPT-4o limits
    if bot_user.daily_gpt4o_messages >= plan_features["daily_gpt4o_messages"]:
        await update.message.reply_text(
            get_limit_exceeded_message("daily_gpt4o", plan_features["name"]),
            parse_mode='Markdown'
        )
        return
    
    # Simple echo for now (will be replaced with actual AI chat)
    response = f"""
🤖 **AI Chat Response**

**You said:** "{message_text}"

*This is a demo response. Full AI chat integration coming soon!*

**Available commands:**
• `/image <description>` - Generate images
• `/video <description>` - Create videos
• `/music <description>` - Generate music
• `/plans` - View pricing plans
• `/upgrade` - Upgrade your plan

**Your plan:** {plan_features['name']}
**Daily messages used:** {bot_user.daily_gpt4o_messages + 1}/{plan_features['daily_gpt4o_messages']}
    """
    
    # Update usage
    bot_user.daily_gpt4o_messages += 1
    await user_service.update_user_usage(bot_user)
    
    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    """Main function to run the bot"""
    
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("plans", plans_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("upgrade", upgrade_command))
    application.add_handler(CommandHandler("upgrade_starter", upgrade_starter_command))
    application.add_handler(CommandHandler("upgrade_pro", upgrade_pro_command))
    application.add_handler(CommandHandler("upgrade_premium", upgrade_premium_command))
    application.add_handler(CommandHandler("upgrade_ultimate", upgrade_ultimate_command))
    application.add_handler(CommandHandler("image", image_command))
    application.add_handler(CommandHandler("video", video_command))
    application.add_handler(CommandHandler("music", music_command))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Handle all other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Starting AI Bot...")
# application.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__ == "__main__":
    main()



    # For webhook deployment on Render
    if s    if settings.telegram_webhook_url:
        logger.info(f"Setting webhook to {settings.telegram_webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=settings.port,
            url_path=settings.telegram_bot_token,
            webhook_url=f"{settings.telegram_webhook_url}/{settings.telegram_bot_token}"
        )
    else:
        logger.info("Starting AI Bot in polling mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


