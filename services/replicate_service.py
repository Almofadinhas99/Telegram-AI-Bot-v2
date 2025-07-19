import logging
import httpx
from typing import Optional, Dict, Any, List
from config.settings import settings

logger = logging.getLogger(__name__)

class ReplicateService:
    def __init__(self):
        self.api_token = settings.replicate_api_token
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

    async def generate_image(
        self,
        prompt: str,
        model: str = "black-forest-labs/flux-dev",
        aspect_ratio: str = "1:1",
        num_outputs: int = 1,
        output_format: str = "jpg",
        output_quality: int = 80
    ) -> Dict[str, Any]:
        """Generate image using Replicate models"""
        
        try:
            async with httpx.AsyncClient() as client:
                # Create prediction
                payload = {
                    "version": await self._get_model_version(model),
                    "input": {
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "num_outputs": num_outputs,
                        "output_format": output_format,
                        "output_quality": output_quality
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/predictions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 201:
                    prediction = response.json()
                    
                    # Wait for completion
                    result = await self._wait_for_prediction(prediction["id"])
                    
                    if result["status"] == "succeeded":
                        return {
                            "success": True,
                            "image_url": result["output"][0] if result["output"] else None,
                            "cost": self._calculate_image_cost(model),
                            "prediction_id": result["id"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Prediction failed: {result.get('error', 'Unknown error')}"
                        }
                else:
                    logger.error(f"Replicate API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating image with Replicate: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_video(
        self,
        prompt: str,
        model: str = "minimax/video-01",
        duration: int = 6
    ) -> Dict[str, Any]:
        """Generate video using Replicate models"""
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "version": await self._get_model_version(model),
                    "input": {
                        "prompt": prompt,
                        "duration": duration
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/predictions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 201:
                    prediction = response.json()
                    
                    # Wait for completion (videos take longer)
                    result = await self._wait_for_prediction(prediction["id"], timeout=300)
                    
                    if result["status"] == "succeeded":
                        return {
                            "success": True,
                            "video_url": result["output"],
                            "cost": self._calculate_video_cost(model, duration),
                            "prediction_id": result["id"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Prediction failed: {result.get('error', 'Unknown error')}"
                        }
                else:
                    logger.error(f"Replicate video API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating video with Replicate: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_music(
        self,
        prompt: str,
        model: str = "suno-ai/bark",
        duration: int = 30
    ) -> Dict[str, Any]:
        """Generate music using Replicate models"""
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "version": await self._get_model_version(model),
                    "input": {
                        "prompt": prompt,
                        "duration": duration
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/predictions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 201:
                    prediction = response.json()
                    
                    # Wait for completion
                    result = await self._wait_for_prediction(prediction["id"], timeout=180)
                    
                    if result["status"] == "succeeded":
                        return {
                            "success": True,
                            "audio_url": result["output"],
                            "cost": self._calculate_music_cost(model, duration),
                            "prediction_id": result["id"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Prediction failed: {result.get('error', 'Unknown error')}"
                        }
                else:
                    logger.error(f"Replicate music API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating music with Replicate: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _wait_for_prediction(self, prediction_id: str, timeout: int = 120) -> Dict[str, Any]:
        """Wait for prediction to complete"""
        
        import asyncio
        
        async with httpx.AsyncClient() as client:
            start_time = asyncio.get_event_loop().time()
            
            while True:
                response = await client.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result["status"] in ["succeeded", "failed", "canceled"]:
                        return result
                    
                    # Check timeout
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        return {
                            "status": "failed",
                            "error": "Timeout waiting for prediction"
                        }
                    
                    # Wait before next check
                    await asyncio.sleep(2)
                else:
                    return {
                        "status": "failed",
                        "error": f"Failed to check prediction status: {response.status_code}"
                    }

    async def _get_model_version(self, model: str) -> str:
        """Get the latest version of a model"""
        
        # Model version mapping (these would need to be updated periodically)
        model_versions = {
            "black-forest-labs/flux-dev": "5ac81c6dcf8b4c4f8a47b64c8df6af7b2c2c4fbb8d2b2b2b2b2b2b2b2b2b2b2b",
            "black-forest-labs/flux-schnell": "5ac81c6dcf8b4c4f8a47b64c8df6af7b2c2c4fbb8d2b2b2b2b2b2b2b2b2b2b2b",
            "minimax/video-01": "5ac81c6dcf8b4c4f8a47b64c8df6af7b2c2c4fbb8d2b2b2b2b2b2b2b2b2b2b2b",
            "suno-ai/bark": "5ac81c6dcf8b4c4f8a47b64c8df6af7b2c2c4fbb8d2b2b2b2b2b2b2b2b2b2b2b"
        }
        
        # In production, you would fetch this dynamically
        return model_versions.get(model, "latest")

    def _calculate_image_cost(self, model: str) -> float:
        """Calculate cost for image generation"""
        
        # Approximate costs based on Replicate pricing
        model_costs = {
            "black-forest-labs/flux-dev": 0.025,
            "black-forest-labs/flux-schnell": 0.003,
            "black-forest-labs/flux-pro": 0.05,
            "stability-ai/sdxl": 0.0025
        }
        
        return model_costs.get(model, 0.01)

    def _calculate_video_cost(self, model: str, duration: int) -> float:
        """Calculate cost for video generation"""
        
        # Approximate costs based on Replicate pricing
        model_costs = {
            "minimax/video-01": 0.5,  # per video
            "runway/gen-2": 0.05,     # per second
            "stability-ai/stable-video-diffusion": 0.1  # per video
        }
        
        base_cost = model_costs.get(model, 0.1)
        
        # Some models charge per second, others per video
        if "runway" in model:
            return base_cost * duration
        else:
            return base_cost

    def _calculate_music_cost(self, model: str, duration: int) -> float:
        """Calculate cost for music generation"""
        
        # Approximate costs based on Replicate pricing
        model_costs = {
            "suno-ai/bark": 0.02,     # per second
            "riffusion/riffusion": 0.01,  # per second
            "meta/musicgen": 0.015    # per second
        }
        
        cost_per_second = model_costs.get(model, 0.01)
        return cost_per_second * duration

    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        
        return {
            "image_models": [
                {
                    "id": "black-forest-labs/flux-dev",
                    "name": "FLUX Dev",
                    "description": "High quality image generation",
                    "cost_estimate": 0.025
                },
                {
                    "id": "black-forest-labs/flux-schnell",
                    "name": "FLUX Schnell",
                    "description": "Fast image generation",
                    "cost_estimate": 0.003
                },
                {
                    "id": "stability-ai/sdxl",
                    "name": "Stable Diffusion XL",
                    "description": "Popular image generation model",
                    "cost_estimate": 0.0025
                }
            ],
            "video_models": [
                {
                    "id": "minimax/video-01",
                    "name": "MiniMax Video",
                    "description": "High quality video generation",
                    "cost_estimate": 0.5
                },
                {
                    "id": "runway/gen-2",
                    "name": "Runway Gen-2",
                    "description": "Professional video generation",
                    "cost_estimate": 0.05
                }
            ],
            "music_models": [
                {
                    "id": "suno-ai/bark",
                    "name": "Bark",
                    "description": "Text-to-speech and music generation",
                    "cost_estimate": 0.02
                },
                {
                    "id": "meta/musicgen",
                    "name": "MusicGen",
                    "description": "Music generation from text",
                    "cost_estimate": 0.015
                }
            ]
        }

    async def get_prediction_status(self, prediction_id: str) -> Dict[str, Any]:
        """Get status of a specific prediction"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"Failed to get prediction status: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting prediction status: {e}")
            return {
                "error": str(e)
            }

