"""Client for kie.ai API (google/nano-banana-edit model)."""
import base64
import asyncio
import json
import httpx
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Result of image generation."""
    success: bool
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    task_id: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None
    image_data: Optional[bytes] = None
    local_filename: Optional[str] = None


class KieClient:
    """Client for interacting with kie.ai API."""
    
    BASE_URL = "https://api.kie.ai/api/v1"
    MODEL_GENERATE = "nano-banana-pro"  # Text-to-image
    MODEL_EDIT = "google/nano-banana-edit"  # Image editing (requires input image)
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def create_task(
        self,
        prompt: str,
        image_urls: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
    ) -> GenerationResult:
        """
        Create an image generation/edit task.
        
        Args:
            prompt: Text description
            image_urls: Optional list of image URLs for editing
            aspect_ratio: Aspect ratio (1:1, 16:9, etc.)
            resolution: Resolution (1K, 2K, 4K) - for nano-banana-pro
            output_format: Output format (png, jpg)
        
        Returns:
            GenerationResult with task_id
        """
        # Choose model based on whether we have input images
        if image_urls:
            # Edit mode - use nano-banana-edit
            model = self.MODEL_EDIT
            payload = {
                "model": model,
                "input": {
                    "prompt": prompt,
                    "image_urls": image_urls,
                    "output_format": output_format,
                    "image_size": aspect_ratio,
                }
            }
        else:
            # Generate mode - use nano-banana-pro
            model = self.MODEL_GENERATE
            payload = {
                "model": model,
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "output_format": output_format,
                }
            }
        
        try:
            response = await self._client.post(
                f"{self.BASE_URL}/jobs/createTask",
                json=payload,
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("code") == 200:
                task_id = data.get("data", {}).get("taskId")
                return GenerationResult(
                    success=True,
                    task_id=task_id,
                    state="created",
                )
            else:
                error_msg = data.get("message") or data.get("msg") or f"API error: {response.status_code}"
                return GenerationResult(success=False, error=error_msg)
                
        except Exception as e:
            return GenerationResult(success=False, error=f"Request failed: {str(e)}")
    
    async def query_task(self, task_id: str) -> GenerationResult:
        """
        Query the status of a task using recordInfo endpoint.
        
        Args:
            task_id: The task ID from create_task
        
        Returns:
            GenerationResult with image URLs if completed
        """
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/jobs/recordInfo",
                params={"taskId": task_id},
            )
            
            data = response.json()
            api_code = data.get("code")
            
            if response.status_code == 200 and api_code == 200:
                task_data = data.get("data", {})
                state = task_data.get("state")
                
                if state == "success":
                    # Parse resultJson to get image URLs
                    result_json_str = task_data.get("resultJson", "{}")
                    try:
                        result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                        urls = result_json.get("resultUrls", [])
                    except:
                        urls = []
                    
                    return GenerationResult(
                        success=True,
                        image_url=urls[0] if urls else None,
                        image_urls=urls,
                        task_id=task_id,
                        state=state,
                    )
                elif state == "fail":
                    return GenerationResult(
                        success=False,
                        task_id=task_id,
                        state=state,
                        error=task_data.get("failMsg") or "Task failed",
                    )
                else:
                    # Still processing (pending, processing, etc.)
                    return GenerationResult(
                        success=False,
                        task_id=task_id,
                        state=state,
                        error=f"Processing (state: {state})",
                    )
            else:
                error_msg = data.get("message") or data.get("msg") or "Unknown error"
                return GenerationResult(
                    success=False,
                    error=f"Query error: {error_msg} (HTTP {response.status_code})",
                )
                
        except Exception as e:
            return GenerationResult(success=False, error=f"Query failed: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        image_urls: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
        max_wait_seconds: int = 120,
        poll_interval: float = 3.0,
    ) -> GenerationResult:
        """
        Generate/edit an image and wait for completion.
        
        Args:
            prompt: Text description
            image_urls: Optional list of image URLs for editing
            aspect_ratio: Aspect ratio (1:1, 16:9, etc.)
            resolution: Resolution (1K, 2K, 4K)
            output_format: Output format (png, jpg)
            max_wait_seconds: Maximum time to wait for completion
            poll_interval: Seconds between status checks
        
        Returns:
            GenerationResult with image URL
        """
        if not self.api_key:
            return GenerationResult(
                success=False,
                error="API key not configured"
            )
        
        # Create the task
        result = await self.create_task(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format,
        )
        
        if not result.success or not result.task_id:
            return result
        
        # Poll for completion
        task_id = result.task_id
        elapsed = 0.0
        
        while elapsed < max_wait_seconds:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            result = await self.query_task(task_id)
            
            if result.success:
                # Download image data
                if result.image_url:
                    try:
                        img_response = await self._client.get(result.image_url)
                        if img_response.status_code == 200:
                            result.image_data = img_response.content
                            # Generate filename from task_id
                            ext = "png"
                            if result.image_url.endswith(".jpg") or result.image_url.endswith(".jpeg"):
                                ext = "jpg"
                            result.local_filename = f"{task_id}.{ext}"
                    except Exception:
                        pass  # Image download failed, but generation succeeded
                return result
            
            # Check if it's a real error vs still processing
            if result.state and result.state not in ("pending", "processing", "created"):
                if result.state == "fail":
                    return result
            
            # Continue polling if still processing
            if result.state in ("pending", "processing"):
                continue
                
            # Unknown state or error
            if result.error and "Processing" not in result.error:
                return result
        
        return GenerationResult(
            success=False,
            task_id=task_id,
            error=f"Timeout after {max_wait_seconds}s - task may still be processing. Task ID: {task_id}",
        )


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def decode_base64_to_image(base64_string: str) -> bytes:
    """Decode base64 string to image bytes."""
    return base64.b64decode(base64_string)
