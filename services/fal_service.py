import logging
import httpx
from typing import Optional, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

class FalService:
    def __init__(self):
        self.api_key = settings.fal_api_key
        self.base_url = "https://fal.run"
        self.headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_image(
        self,
        prompt: str,
        model: str = "fal-ai/flux/schnell",
        image_size: str = "square_hd",
        num_inference_steps: int = 4,
        guidance_scale: float = 3.5
    ) -> Dict[str, Any]:
        """Generate image using Fal.ai FLUX models"""
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "prompt": prompt,
                    "image_size": image_size,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale
                }
                
                response = await client.post(
                    f"{self.base_url}/{model}",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "image_url": result["images"][0]["url"],
                        "cost": self._calculate_image_cost(image_size, model)
                    }
                else:
                    logger.error(f"Fal.ai API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating image with Fal.ai: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_video(
        self,
        prompt: str,
        model: str = "fal-ai/luma-dream-machine",
        duration: int = 5
    ) -> Dict[str, Any]:
        """Generate video using Fal.ai video models"""
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "prompt": prompt,
                    "duration": duration
                }
                
                response = await client.post(
                    f"{self.base_url}/{model}",
                    headers=self.headers,
                    json=payload,
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "video_url": result["video"]["url"],
                        "cost": self._calculate_video_cost(duration, model)
                    }
                else:
                    logger.error(f"Fal.ai video API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating video with Fal.ai: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def train_lora(
        self,
        images_url: str,
        trigger_word: str,
        model: str = "fal-ai/flux-lora-fast-training"
    ) -> Dict[str, Any]:
        """Train a LoRA model using Fal.ai"""
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "images_data_url": images_url,
                    "trigger_word": trigger_word,
                    "steps": 1000
                }
                
                response = await client.post(
                    f"{self.base_url}/{model}",
                    headers=self.headers,
                    json=payload,
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "lora_url": result["diffusers_lora_file"]["url"],
                        "cost": 2.0  # Fixed cost for LoRA training
                    }
                else:
                    logger.error(f"Fal.ai LoRA training error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error training LoRA with Fal.ai: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_image_cost(self, image_size: str, model: str) -> float:
        """Calculate cost for image generation"""
        
        # Image size to megapixels mapping
        size_to_mp = {
            "square_hd": 1.0,  # 1024x1024
            "square": 0.25,    # 512x512
            "portrait_4_3": 0.75,  # ~870x1160
            "portrait_16_9": 0.5,  # ~576x1024
            "landscape_4_3": 0.75, # ~1160x870
            "landscape_16_9": 0.5  # ~1024x576
        }
        
        # Model pricing per megapixel
        model_pricing = {
            "fal-ai/flux/schnell": 0.003,
            "fal-ai/flux/dev": 0.025,
            "fal-ai/flux-pro": 0.05,
            "fal-ai/flux-pro/v1.1": 0.055
        }
        
        megapixels = size_to_mp.get(image_size, 1.0)
        price_per_mp = model_pricing.get(model, 0.025)
        
        return megapixels * price_per_mp

    def _calculate_video_cost(self, duration: int, model: str) -> float:
        """Calculate cost for video generation"""
        
        # Model pricing per video/second
        model_pricing = {
            "fal-ai/luma-dream-machine": 0.5,  # per video
            "fal-ai/hunyuan-video": 0.4,       # per video
            "fal-ai/kling-video": 0.095        # per second
        }
        
        if "kling" in model:
            return duration * model_pricing.get(model, 0.095)
        else:
            return model_pricing.get(model, 0.5)

    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        
        return {
            "image_models": [
                {
                    "id": "fal-ai/flux/schnell",
                    "name": "FLUX Schnell",
                    "description": "Fastest image generation (1-4 steps)",
                    "cost_per_mp": 0.003
                },
                {
                    "id": "fal-ai/flux/dev",
                    "name": "FLUX Dev",
                    "description": "High quality image generation",
                    "cost_per_mp": 0.025
                },
                {
                    "id": "fal-ai/flux-pro",
                    "name": "FLUX Pro",
                    "description": "Professional quality images",
                    "cost_per_mp": 0.05
                }
            ],
            "video_models": [
                {
                    "id": "fal-ai/luma-dream-machine",
                    "name": "Luma Dream Machine",
                    "description": "High quality video generation",
                    "cost_per_video": 0.5
                },
                {
                    "id": "fal-ai/hunyuan-video",
                    "name": "Hunyuan Video",
                    "description": "Advanced video generation",
                    "cost_per_video": 0.4
                }
            ],
            "training_models": [
                {
                    "id": "fal-ai/flux-lora-fast-training",
                    "name": "FLUX LoRA Training",
                    "description": "Fast LoRA training for custom styles",
                    "cost_per_training": 2.0
                }
            ]
        }

