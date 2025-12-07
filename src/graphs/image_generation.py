"""LangGraph workflow for image generation."""
from typing import Optional, TypedDict, List
from langgraph.graph import StateGraph, START, END

from src.config import settings
from src.services.kie_client import KieClient


class ImageGenerationState(TypedDict):
    """State for image generation workflow."""
    # Input
    prompt: str
    image_url: Optional[str]  # URL of image to edit
    aspect_ratio: str
    resolution: str
    output_format: str
    
    # Processing
    api_key: Optional[str]
    
    # Output
    success: bool
    image_url_out: Optional[str]
    image_urls: Optional[List[str]]
    task_id: Optional[str]
    state: Optional[str]
    error: Optional[str]


async def validate_input(state: ImageGenerationState) -> ImageGenerationState:
    """Validate input parameters."""
    if not state.get("prompt"):
        return {
            **state,
            "success": False,
            "error": "Prompt is required"
        }
    
    api_key = state.get("api_key") or settings.kie_api_key
    if not api_key:
        return {
            **state,
            "success": False,
            "error": "API key not configured. Use /api/key endpoint to set it."
        }
    
    return {
        **state,
        "api_key": api_key,
    }


async def generate_image(state: ImageGenerationState) -> ImageGenerationState:
    """Call kie.ai API to generate/edit image."""
    # Skip if validation failed
    if state.get("error"):
        return state
    
    client = KieClient(state["api_key"])
    try:
        # Prepare image URLs if provided
        image_urls = None
        if state.get("image_url"):
            image_urls = [state["image_url"]]
        
        result = await client.generate_image(
            prompt=state["prompt"],
            image_urls=image_urls,
            aspect_ratio=state.get("aspect_ratio", "1:1"),
            resolution=state.get("resolution", "1K"),
            output_format=state.get("output_format", "png"),
        )
        
        return {
            **state,
            "success": result.success,
            "image_url_out": result.image_url,
            "image_urls": result.image_urls,
            "task_id": result.task_id,
            "state": result.state,
            "error": result.error,
        }
    finally:
        await client.close()


def should_generate(state: ImageGenerationState) -> str:
    """Determine if we should proceed with generation."""
    if state.get("error"):
        return "end"
    return "generate"


# Build the graph
def create_image_generation_graph():
    """Create and compile the image generation graph."""
    workflow = StateGraph(ImageGenerationState)
    
    # Add nodes
    workflow.add_node("validate", validate_input)
    workflow.add_node("generate", generate_image)
    
    # Add edges
    workflow.add_edge(START, "validate")
    workflow.add_conditional_edges(
        "validate",
        should_generate,
        {
            "generate": "generate",
            "end": END,
        }
    )
    workflow.add_edge("generate", END)
    
    return workflow.compile()


# Compiled graph instance
image_generation_graph = create_image_generation_graph()


async def run_image_generation(
    prompt: str,
    image_url: Optional[str] = None,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    output_format: str = "png",
) -> dict:
    """Run the image generation workflow."""
    initial_state: ImageGenerationState = {
        "prompt": prompt,
        "image_url": image_url,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "output_format": output_format,
        "api_key": None,
        "success": False,
        "image_url_out": None,
        "image_urls": None,
        "task_id": None,
        "state": None,
        "error": None,
    }
    
    result = await image_generation_graph.ainvoke(initial_state)
    
    # Map output field name
    return {
        "success": result["success"],
        "image_url": result.get("image_url_out"),
        "image_urls": result.get("image_urls"),
        "task_id": result.get("task_id"),
        "state": result.get("state"),
        "error": result.get("error"),
    }
