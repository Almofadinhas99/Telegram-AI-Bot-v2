from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json

from config.settings import settings
from services.telegram_service import TelegramService
from services.user_service import UserService

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Telegram AI Bot",
    description="Bot multifuncional de IA para Telegram",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
telegram_service = TelegramService()
user_service = UserService()

# Initialize Telegram bot application
telegram_app = Application.builder().token(settings.telegram_bot_token).build()

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("Starting Telegram AI Bot...")
    
    # Add handlers to telegram app
    telegram_app.add_handler(CommandHandler("start", telegram_service.start_command))
    telegram_app.add_handler(CommandHandler("help", telegram_service.help_command))
    telegram_app.add_handler(CommandHandler("plans", telegram_service.plans_command))
    telegram_app.add_handler(CommandHandler("status", telegram_service.status_command))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_service.handle_message))
    telegram_app.add_handler(MessageHandler(filters.PHOTO, telegram_service.handle_photo))
    
    # Initialize telegram app
    await telegram_app.initialize()
    await telegram_app.start()
    
    logger.info("Bot started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Telegram AI Bot...")
    await telegram_app.stop()
    await telegram_app.shutdown()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Telegram AI Bot is running!", "status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook endpoint for Telegram updates"""
    try:
        # Get the raw body
        body = await request.body()
        
        # Parse the update
        update_dict = json.loads(body.decode('utf-8'))
        update = Update.de_json(update_dict, telegram_app.bot)
        
        # Process the update
        await telegram_app.process_update(update)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "bot_info": {
            "username": telegram_app.bot.username if telegram_app.bot else None,
            "webhook_configured": bool(settings.telegram_webhook_url)
        }
    }


