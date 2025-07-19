import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Optional

from models.user import User, UserPlan, PLAN_CONFIGS
from services.user_service import UserService
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.user_service = UserService()
        self.ai_service = AIService()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Register or get user
        db_user = await self.user_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_message = f"""
🤖 **Bem-vindo ao AI Bot Multifuncional!**

Olá {user.first_name}! Eu sou seu assistente de IA completo.

**🎯 O que posso fazer:**
• 💬 Conversas inteligentes (GPT-4o, GPT-4, Claude)
• 🎨 Geração de imagens (DALL-E, Stable Diffusion, Midjourney)
• 🎵 Criação de músicas (Suno AI)
• 👁️ Análise de imagens (GPT-4 Vision, Gemini)
• ✏️ Edição de imagens

**📊 Seu plano atual:** {db_user.plan.value.upper()}

Use /help para ver todos os comandos
Use /plans para ver os planos disponíveis
Use /status para verificar seu uso atual

Envie uma mensagem ou imagem para começar! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = """
🆘 **Comandos Disponíveis:**

**Comandos Básicos:**
• `/start` - Iniciar o bot
• `/help` - Mostrar esta ajuda
• `/plans` - Ver planos disponíveis
• `/status` - Ver seu uso atual

**Como usar:**
• **Texto:** Envie qualquer mensagem para conversar
• **Imagem:** Envie uma foto para análise
• **Geração de imagem:** Digite "gerar: [descrição]"
• **Música:** Digite "música: [descrição]"

**Exemplos:**
• `gerar: um gato fofo em estilo anime`
• `música: uma música relaxante de piano`
• `Explique esta imagem` (com foto anexada)

**💡 Dicas:**
• Seja específico nas descrições
• Use comandos em português
• Verifique seus limites com /status
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def plans_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /plans command"""
        plans_text = """
💎 **Planos Disponíveis:**

**🆓 FREE** - Grátis
• 10 mensagens GPT-4o/dia
• 5 imagens/mês
• Sem música

**⭐ MINI** - $3.80/mês
• 100 mensagens GPT-4o/dia
• 10 imagens/mês
• 5 músicas/mês

**🚀 STARTER** - $7.97/mês
• 25 mensagens GPT-4/dia
• 30 imagens/mês
• 10 músicas/mês

**💎 PREMIUM** - $12.97/mês
• 50 mensagens GPT-4/dia
• 100 imagens/mês
• 20 músicas/mês

**🔥 ULTIMATE** - $18.38/mês
• 100 mensagens GPT-4/dia
• 200 imagens/mês
• 50 músicas/mês

**👑 ALPHA** - $44.95/mês
• Mensagens ilimitadas
• Imagens ilimitadas
• 200 músicas/mês
• 3M tokens Claude
• Direitos comerciais

Para fazer upgrade, entre em contato conosco!
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Fazer Upgrade", url="https://t.me/seu_contato")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(plans_text, parse_mode='Markdown', reply_markup=reply_markup)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        user = update.effective_user
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text("❌ Usuário não encontrado. Use /start primeiro.")
            return
        
        plan_config = PLAN_CONFIGS[db_user.plan]
        
        status_text = f"""
📊 **Status da Conta:**

**👤 Usuário:** {db_user.first_name or 'N/A'}
**📋 Plano:** {db_user.plan.value.upper()}
**💰 Preço:** ${plan_config.price_usd}/mês

**📈 Uso Atual:**
• **GPT-4o:** {db_user.daily_gpt4o_messages}/{plan_config.daily_gpt4o_messages if plan_config.daily_gpt4o_messages > 0 else '∞'} (hoje)
• **GPT-4:** {db_user.daily_gpt4_messages}/{plan_config.daily_gpt4_messages if plan_config.daily_gpt4_messages > 0 else '∞'} (hoje)
• **Imagens:** {db_user.monthly_images}/{plan_config.monthly_images if plan_config.monthly_images > 0 else '∞'} (mês)
• **Músicas:** {db_user.monthly_music}/{plan_config.monthly_music if plan_config.monthly_music > 0 else '∞'} (mês)
• **Claude:** {db_user.monthly_claude_tokens}/{plan_config.monthly_claude_tokens if plan_config.monthly_claude_tokens > 0 else '∞'} tokens (mês)

Use /plans para ver outros planos disponíveis.
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages"""
        user = update.effective_user
        message_text = update.message.text.lower()
        
        # Get user from database
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("❌ Use /start primeiro para se registrar.")
            return
        
        # Check if it's an image generation request
        if message_text.startswith(('gerar:', 'generate:', 'imagem:')):
            await self._handle_image_generation(update, context, db_user)
            return
        
        # Check if it's a music generation request
        if message_text.startswith(('música:', 'music:', 'musica:')):
            await self._handle_music_generation(update, context, db_user)
            return
        
        # Handle regular chat
        await self._handle_chat(update, context, db_user)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo messages"""
        user = update.effective_user
        
        # Get user from database
        db_user = await self.user_service.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("❌ Use /start primeiro para se registrar.")
            return
        
        await self._handle_image_analysis(update, context, db_user)

    async def _handle_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
        """Handle regular chat messages"""
        # Check usage limits
        plan_config = PLAN_CONFIGS[user.plan]
        
        # Determine which model to use based on plan and availability
        if plan_config.daily_gpt4_messages > 0 and user.daily_gpt4_messages < plan_config.daily_gpt4_messages:
            model = "gpt-4"
            user.daily_gpt4_messages += 1
        elif plan_config.daily_gpt4o_messages > 0 and user.daily_gpt4o_messages < plan_config.daily_gpt4o_messages:
            model = "gpt-4o"
            user.daily_gpt4o_messages += 1
        elif plan_config.daily_gpt4_messages == -1:  # Unlimited
            model = "gpt-4"
        elif plan_config.daily_gpt4o_messages == -1:  # Unlimited
            model = "gpt-4o"
        else:
            await update.message.reply_text("❌ Você atingiu o limite de mensagens para hoje. Use /plans para fazer upgrade.")
            return
        
        # Update user usage
        await self.user_service.update_user_usage(user)
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Generate response using AI service
            response = await self.ai_service.generate_text_response(
                message=update.message.text,
                model=model,
                user_context=user
            )
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error generating text response: {e}")
            await update.message.reply_text("❌ Erro ao gerar resposta. Tente novamente.")

    async def _handle_image_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
        """Handle image generation requests"""
        plan_config = PLAN_CONFIGS[user.plan]
        
        # Check usage limits
        if plan_config.monthly_images > 0 and user.monthly_images >= plan_config.monthly_images:
            await update.message.reply_text("❌ Você atingiu o limite de imagens para este mês. Use /plans para fazer upgrade.")
            return
        
        # Extract prompt
        prompt = update.message.text.split(':', 1)[1].strip()
        if not prompt:
            await update.message.reply_text("❌ Por favor, forneça uma descrição para a imagem.")
            return
        
        # Update usage
        user.monthly_images += 1
        await self.user_service.update_user_usage(user)
        
        # Send generating indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
        
        try:
            # Generate image using AI service
            image_url = await self.ai_service.generate_image(
                prompt=prompt,
                user_context=user
            )
            
            await update.message.reply_photo(photo=image_url, caption=f"🎨 Imagem gerada: {prompt}")
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            await update.message.reply_text("❌ Erro ao gerar imagem. Tente novamente.")

    async def _handle_music_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
        """Handle music generation requests"""
        plan_config = PLAN_CONFIGS[user.plan]
        
        # Check usage limits
        if plan_config.monthly_music > 0 and user.monthly_music >= plan_config.monthly_music:
            await update.message.reply_text("❌ Você atingiu o limite de músicas para este mês. Use /plans para fazer upgrade.")
            return
        
        # Extract prompt
        prompt = update.message.text.split(':', 1)[1].strip()
        if not prompt:
            await update.message.reply_text("❌ Por favor, forneça uma descrição para a música.")
            return
        
        # Update usage
        user.monthly_music += 1
        await self.user_service.update_user_usage(user)
        
        # Send generating indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_audio")
        
        try:
            # Generate music using AI service
            audio_url = await self.ai_service.generate_music(
                prompt=prompt,
                user_context=user
            )
            
            await update.message.reply_audio(audio=audio_url, caption=f"🎵 Música gerada: {prompt}")
            
        except Exception as e:
            logger.error(f"Error generating music: {e}")
            await update.message.reply_text("❌ Erro ao gerar música. Tente novamente.")

    async def _handle_image_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
        """Handle image analysis requests"""
        # Send analyzing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Get the largest photo
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            # Analyze image using AI service
            analysis = await self.ai_service.analyze_image(
                image_url=file.file_path,
                prompt=update.message.caption or "Descreva esta imagem em detalhes.",
                user_context=user
            )
            
            await update.message.reply_text(f"👁️ **Análise da imagem:**\n\n{analysis}", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            await update.message.reply_text("❌ Erro ao analisar imagem. Tente novamente.")

