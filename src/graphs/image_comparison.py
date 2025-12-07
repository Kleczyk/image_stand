"""LangGraph workflow for image comparison."""
from typing import Optional, TypedDict
from langgraph.graph import StateGraph, START, END

from src.services.comparison import compare_images


class ImageComparisonState(TypedDict):
    """State for image comparison workflow."""
    # Input
    image1_bytes: bytes
    image2_bytes: bytes
    
    # Output
    success: bool
    similarity_score: Optional[float]
    similarity_percentage: Optional[float]
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
    """Compare the two images using SSIM."""
    if state.get("error"):
        return state
    
    result = compare_images(state["image1_bytes"], state["image2_bytes"])
    
    return {
        **state,
        "success": result.success,
        "similarity_score": result.similarity_score,
        "similarity_percentage": result.similarity_percentage,
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
) -> ImageComparisonState:
    """Run the image comparison workflow."""
    initial_state: ImageComparisonState = {
        "image1_bytes": image1_bytes,
        "image2_bytes": image2_bytes,
        "success": False,
        "similarity_score": None,
        "similarity_percentage": None,
        "error": None,
    }
    
    result = await image_comparison_graph.ainvoke(initial_state)
    return result



