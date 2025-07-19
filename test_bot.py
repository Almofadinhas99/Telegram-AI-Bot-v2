#!/usr/bin/env python3
"""
Script de teste básico para o bot de Telegram
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config.settings import settings
from services.user_service import UserService
from services.fal_service import FalService
from services.replicate_service import ReplicateService

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
    
    welcome_message = f"""
🤖 **Bem-vindo ao Bot de IA Multifuncional!**

Olá {user.first_name}! 👋

Este bot integra várias APIs de IA para oferecer:

🎨 **Geração de Imagens**
• FLUX (Fal.ai e Replicate)
• Stable Diffusion
• DALL-E (em breve)

🎬 **Geração de Vídeos**
• Luma Dream Machine
• MiniMax Video
• Runway Gen-2

🎵 **Geração de Música**
• Suno AI
• Bark
• MusicGen

💬 **Chat com IA**
• GPT-4o (em breve)
• Claude (em breve)
• Gemini (em breve)

**Comandos disponíveis:**
/start - Mostrar esta mensagem
/help - Ajuda detalhada
/status - Ver seu plano e uso
/image <prompt> - Gerar imagem
/video <prompt> - Gerar vídeo
/music <prompt> - Gerar música

**Seu plano atual:** {bot_user.plan.value}

Digite qualquer mensagem para começar a conversar!
    """
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 **Ajuda - Como usar o bot**

**Comandos de Geração:**

🎨 `/image <prompt>` - Gerar imagem
Exemplo: `/image um gato fofo usando óculos`

🎬 `/video <prompt>` - Gerar vídeo
Exemplo: `/video um pássaro voando sobre montanhas`

🎵 `/music <prompt>` - Gerar música
Exemplo: `/music música relaxante de piano`

**Comandos de Informação:**

📊 `/status` - Ver seu plano atual e uso
💰 `/plans` - Ver planos disponíveis
🔧 `/models` - Ver modelos disponíveis

**Dicas:**
• Seja específico nos prompts para melhores resultados
• Imagens são mais rápidas que vídeos
• Vídeos podem levar alguns minutos para gerar
• Música é gerada em segmentos de 30 segundos

**Suporte:**
Se tiver problemas, entre em contato conosco!
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    
    # Get user stats
    stats = await user_service.get_user_stats(user.id)
    
    if stats:
        status_text = f"""
📊 **Seu Status**

👤 **Usuário:** {stats['telegram_id']}
📋 **Plano:** {stats['plan']}

**Uso Diário:**
• GPT-4o: {stats['daily_gpt4o_messages']}/100
• GPT-4: {stats['daily_gpt4_messages']}/50

**Uso Mensal:**
• Imagens: {stats['monthly_images']}/100
• Músicas: {stats['monthly_music']}/20
• Tokens Claude: {stats['monthly_claude_tokens']}/3M

**Conta criada:** {stats['created_at'].strftime('%d/%m/%Y')}
**Última atualização:** {stats['updated_at'].strftime('%d/%m/%Y %H:%M')}
        """
    else:
        status_text = "❌ Erro ao obter informações do usuário."
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /image command"""
    if not context.args:
        await update.message.reply_text("❌ Por favor, forneça um prompt para a imagem.\nExemplo: `/image um gato fofo`", parse_mode='Markdown')
        return
    
    prompt = " ".join(context.args)
    user = update.effective_user
    
    # Get user
    bot_user = await user_service.get_or_create_user(user.id)
    
    # Check usage limits (simplified for testing)
    if bot_user.monthly_images >= 100:
        await update.message.reply_text("❌ Você atingiu o limite mensal de imagens. Faça upgrade do seu plano!")
        return
    
    # Send "generating" message
    generating_msg = await update.message.reply_text("🎨 Gerando imagem... Isso pode levar alguns segundos.")
    
    try:
        # Try Fal.ai first (cheaper and faster)
        result = await fal_service.generate_image(prompt)
        
        if result["success"]:
            # Update user usage
            bot_user.monthly_images += 1
            await user_service.update_user_usage(bot_user)
            
            # Send image
            await update.message.reply_photo(
                photo=result["image_url"],
                caption=f"🎨 **Imagem gerada!**\n\n**Prompt:** {prompt}\n**Custo:** ${result['cost']:.4f}\n**Modelo:** Fal.ai FLUX",
                parse_mode='Markdown'
            )
            
            # Delete generating message
            await generating_msg.delete()
            
        else:
            # Try Replicate as fallback
            await generating_msg.edit_text("🎨 Tentando modelo alternativo...")
            
            result = await replicate_service.generate_image(prompt)
            
            if result["success"]:
                # Update user usage
                bot_user.monthly_images += 1
                await user_service.update_user_usage(bot_user)
                
                # Send image
                await update.message.reply_photo(
                    photo=result["image_url"],
                    caption=f"🎨 **Imagem gerada!**\n\n**Prompt:** {prompt}\n**Custo:** ${result['cost']:.4f}\n**Modelo:** Replicate FLUX",
                    parse_mode='Markdown'
                )
                
                # Delete generating message
                await generating_msg.delete()
            else:
                await generating_msg.edit_text(f"❌ Erro ao gerar imagem: {result['error']}")
    
    except Exception as e:
        logger.error(f"Error in image command: {e}")
        await generating_msg.edit_text("❌ Erro interno. Tente novamente.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user = update.effective_user
    message_text = update.message.text
    
    # Get or create user
    bot_user = await user_service.get_or_create_user(user.id)
    
    # Simple echo for now (will be replaced with AI chat)
    response = f"Você disse: '{message_text}'\n\nUse os comandos para gerar conteúdo:\n• `/image <prompt>` para imagens\n• `/video <prompt>` para vídeos\n• `/music <prompt>` para música"
    
    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    """Main function to run the bot"""
    
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("image", image_command))
    
    # Handle all other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

