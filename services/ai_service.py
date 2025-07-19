import logging
import httpx
from typing import Optional
from models.user import User
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.replicate_client = None
        self.fal_client = None
        
        # Initialize clients when API keys are available
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize AI service clients"""
        try:
            if settings.openai_api_key:
                import openai
                self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")

        try:
            if settings.anthropic_api_key:
                import anthropic
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic client: {e}")

    async def generate_text_response(
        self,
        message: str,
        model: str = "gpt-4o",
        user_context: Optional[User] = None
    ) -> str:
        """Generate text response using specified model"""
        
        try:
            if model.startswith("gpt") and self.openai_client:
                return await self._generate_openai_response(message, model)
            elif model.startswith("claude") and self.anthropic_client:
                return await self._generate_anthropic_response(message, model)
            else:
                # Fallback to mock response
                return await self._generate_mock_response(message, model)
                
        except Exception as e:
            logger.error(f"Error generating text response: {e}")
            return "❌ Desculpe, ocorreu um erro ao gerar a resposta. Tente novamente."

    async def generate_image(
        self,
        prompt: str,
        user_context: Optional[User] = None
    ) -> str:
        """Generate image using available APIs"""
        
        try:
            # Try Replicate first (preferred)
            if settings.replicate_api_token:
                return await self._generate_replicate_image(prompt)
            
            # Try Fal.ai
            elif settings.fal_api_key:
                return await self._generate_fal_image(prompt)
            
            # Try OpenAI DALL-E
            elif self.openai_client:
                return await self._generate_dalle_image(prompt)
            
            else:
                # Return mock image URL
                return "https://via.placeholder.com/512x512?text=Imagem+Gerada"
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise Exception("Erro ao gerar imagem")

    async def generate_music(
        self,
        prompt: str,
        user_context: Optional[User] = None
    ) -> str:
        """Generate music using available APIs"""
        
        try:
            # Try Replicate for Suno AI
            if settings.replicate_api_token:
                return await self._generate_replicate_music(prompt)
            
            # Try Fal.ai
            elif settings.fal_api_key:
                return await self._generate_fal_music(prompt)
            
            else:
                # Return mock audio URL
                return "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
                
        except Exception as e:
            logger.error(f"Error generating music: {e}")
            raise Exception("Erro ao gerar música")

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "Descreva esta imagem",
        user_context: Optional[User] = None
    ) -> str:
        """Analyze image using vision models"""
        
        try:
            # Try OpenAI GPT-4 Vision
            if self.openai_client:
                return await self._analyze_image_openai(image_url, prompt)
            
            # Try Google Gemini Vision
            elif settings.google_ai_api_key:
                return await self._analyze_image_gemini(image_url, prompt)
            
            else:
                return "Esta é uma imagem que foi enviada para análise. (Análise de imagem não configurada)"
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return "❌ Erro ao analisar a imagem."

    # OpenAI implementations
    async def _generate_openai_response(self, message: str, model: str) -> str:
        """Generate response using OpenAI"""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente de IA útil e amigável. Responda em português brasileiro."},
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content

    async def _generate_dalle_image(self, prompt: str) -> str:
        """Generate image using DALL-E"""
        response = await self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url

    async def _analyze_image_openai(self, image_url: str, prompt: str) -> str:
        """Analyze image using GPT-4 Vision"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

    # Anthropic implementations
    async def _generate_anthropic_response(self, message: str, model: str) -> str:
        """Generate response using Anthropic Claude"""
        response = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.content[0].text

    # Replicate implementations
    async def _generate_replicate_image(self, prompt: str) -> str:
        """Generate image using Replicate"""
        # This will be implemented when we have access to Replicate API
        # For now, return placeholder
        return "https://via.placeholder.com/512x512?text=Replicate+Image"

    async def _generate_replicate_music(self, prompt: str) -> str:
        """Generate music using Replicate"""
        # This will be implemented when we have access to Replicate API
        # For now, return placeholder
        return "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"

    # Fal.ai implementations
    async def _generate_fal_image(self, prompt: str) -> str:
        """Generate image using Fal.ai"""
        # This will be implemented when we have access to Fal.ai API
        # For now, return placeholder
        return "https://via.placeholder.com/512x512?text=Fal.ai+Image"

    async def _generate_fal_music(self, prompt: str) -> str:
        """Generate music using Fal.ai"""
        # This will be implemented when we have access to Fal.ai API
        # For now, return placeholder
        return "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"

    # Google Gemini implementations
    async def _analyze_image_gemini(self, image_url: str, prompt: str) -> str:
        """Analyze image using Google Gemini"""
        # This will be implemented when we have access to Gemini API
        # For now, return placeholder
        return "Análise de imagem usando Google Gemini (não configurado ainda)"

    # Mock implementations for testing
    async def _generate_mock_response(self, message: str, model: str) -> str:
        """Generate mock response for testing"""
        return f"Esta é uma resposta simulada do modelo {model} para: '{message}'. Configure as APIs para respostas reais."

