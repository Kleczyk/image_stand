"""LangGraph workflow for image comparison."""
from typing import Optional, TypedDict
from concurrent.futures import Executor
import asyncio
from langgraph.graph import StateGraph, START, END

from src.services.comparison import (
    compare_images,
    compare_images_embeddings,
    compare_images_hybrid,
)
from src.config import settings

# Thread pool executor for CPU-intensive comparison tasks
# This will be set from main.py
_executor: Optional[Executor] = None


def set_executor(executor: Executor):
    """Set the thread pool executor for running synchronous comparison tasks."""
    global _executor
    _executor = executor


class ImageComparisonState(TypedDict):
    """State for image comparison workflow."""
    # Input
    image1_bytes: bytes
    image2_bytes: bytes
    method: Optional[str]  # "ssim", "embeddings", or "hybrid"
    sensitivity: Optional[float]  # Sensitivity adjustment (default 1.0)
    
    # Output
    success: bool
    similarity_score: Optional[float]
    similarity_percentage: Optional[float]
    method_used: Optional[str]  # Which method was actually used
    error: Optional[str]


async def validate_images(state: ImageComparisonState) -> ImageComparisonState:
    """Validate input images."""
    if not state.get("image1_bytes"):
        return {
            **state,
            "success": False,
            "error": "First image is required"
        }
    
    if not state.get("image2_bytes"):
        return {
            **state,
            "success": False,
            "error": "Second image is required"
        }
    
    return state


async def compare(state: ImageComparisonState) -> ImageComparisonState:
    """Compare the two images using the specified method."""
    if state.get("error"):
        return state
    
    # Determine which method to use
    method = state.get("method") or settings.similarity_model
    sensitivity = state.get("sensitivity") or settings.similarity_sensitivity
    
    # Run comparison in thread pool to avoid blocking event loop
    # This is especially important for CLIP embeddings which can be slow
    loop = asyncio.get_event_loop()
    executor = _executor or None
    
    try:
        # Select comparison function based on method
        if method == "embeddings":
            if executor:
                result = await loop.run_in_executor(
                    executor,
                    compare_images_embeddings,
                    state["image1_bytes"],
                    state["image2_bytes"],
                    sensitivity,
                )
            else:
                result = compare_images_embeddings(
                    state["image1_bytes"],
                    state["image2_bytes"],
                    sensitivity,
                )
        elif method == "hybrid":
            if executor:
                result = await loop.run_in_executor(
                    executor,
                    compare_images_hybrid,
                    state["image1_bytes"],
                    state["image2_bytes"],
                    settings.similarity_embedding_weight,
                    settings.similarity_ssim_weight,
                    sensitivity,
                )
            else:
                result = compare_images_hybrid(
                    state["image1_bytes"],
                    state["image2_bytes"],
                    embedding_weight=settings.similarity_embedding_weight,
                    ssim_weight=settings.similarity_ssim_weight,
                    sensitivity=sensitivity,
                )
        else:  # Default to SSIM
            if executor:
                result = await loop.run_in_executor(
                    executor,
                    compare_images,
                    state["image1_bytes"],
                    state["image2_bytes"],
                )
            else:
                result = compare_images(
                    state["image1_bytes"],
                    state["image2_bytes"],
                )
            if result.method is None:
                result.method = "ssim"
    except Exception as e:
        # If comparison fails, return error
        return {
            **state,
            "success": False,
            "error": f"Comparison failed: {str(e)}",
        }
    
    return {
        **state,
        "success": result.success,
        "similarity_score": result.similarity_score,
        "similarity_percentage": result.similarity_percentage,
        "method_used": result.method or method,
        "error": result.error,
    }


def should_compare(state: ImageComparisonState) -> str:
    """Determine if we should proceed with comparison."""
    if state.get("error"):
        return "end"
    return "compare"


def create_image_comparison_graph():
    """Create and compile the image comparison graph."""
    workflow = StateGraph(ImageComparisonState)
    
    # Add nodes
    workflow.add_node("validate", validate_images)
    workflow.add_node("compare", compare)
    
    # Add edges
    workflow.add_edge(START, "validate")
    workflow.add_conditional_edges(
        "validate",
        should_compare,
        {
            "compare": "compare",
            "end": END,
        }
    )
    workflow.add_edge("compare", END)
    
    return workflow.compile()


# Compiled graph instance
image_comparison_graph = create_image_comparison_graph()


async def run_image_comparison(
    image1_bytes: bytes,
    image2_bytes: bytes,
    method: Optional[str] = None,
    sensitivity: Optional[float] = None,
) -> ImageComparisonState:
    """Run the image comparison workflow."""
    initial_state: ImageComparisonState = {
        "image1_bytes": image1_bytes,
        "image2_bytes": image2_bytes,
        "method": method,
        "sensitivity": sensitivity,
        "success": False,
        "similarity_score": None,
        "similarity_percentage": None,
        "method_used": None,
        "error": None,
    }
    
    result = await image_comparison_graph.ainvoke(initial_state)
    return result



