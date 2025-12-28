"""Streamlit frontend for Image Generation Game."""
import streamlit as st
import requests
from pathlib import Path
import base64
from io import BytesIO
import os

# API Configuration - Docker internal network
API_BASE = os.getenv("API_URL", "http://api:8000")
API_URL = f"{API_BASE}/api"

# Reference image path (in container)
REFERENCE_IMAGE = "/app/images/reference.png"


@st.cache_data(ttl=60)
def get_api_url():
    """Get the API URL (always use Docker internal)."""
    return API_URL


def get_api_base():
    """Get the API base URL without /api suffix."""
    return API_BASE


def set_api_key(api_key: str) -> dict:
    """Set the API key."""
    url = get_api_url()
    response = requests.post(
        f"{url}/key",
        json={"api_key": api_key},
        timeout=10
    )
    return response.json()


def check_api_status() -> dict:
    """Check API health."""
    url = get_api_url()
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def generate_image(prompt: str, image_url: str = None) -> dict:
    """Generate or edit an image."""
    url = get_api_url()
    data = {
        "prompt": prompt,
        "resolution": "1K",
        "aspect_ratio": "1:1",
        "output_format": "png"
    }
    if image_url:
        data["image_url"] = image_url
    
    response = requests.post(
        f"{url}/generate",
        data=data,
        timeout=120
    )
    return response.json()


def compare_images(image1_bytes: bytes, image2_bytes: bytes, method: str = None, sensitivity: float = None) -> dict:
    """Compare two images."""
    url = get_api_url()
    files = {
        "image1": ("image1.png", image1_bytes, "image/png"),
        "image2": ("image2.png", image2_bytes, "image/png"),
    }
    data = {}
    if method:
        data["method"] = method
    if sensitivity is not None:
        data["sensitivity"] = str(sensitivity)
    
    response = requests.post(
        f"{url}/compare",
        files=files,
        data=data,
        timeout=90  # Increased timeout for CLIP model loading
    )
    return response.json()


def get_sensitivity() -> dict:
    """Get current sensitivity value."""
    url = get_api_url()
    try:
        response = requests.get(f"{url}/sensitivity", timeout=5)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_sensitivity(sensitivity: float) -> dict:
    """Set sensitivity value."""
    url = get_api_url()
    try:
        response = requests.post(
            f"{url}/sensitivity",
            json={"sensitivity": sensitivity},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_image_from_url(url: str) -> bytes:
    """Load image from URL."""
    if url.startswith("/"):
        url = f"{get_api_base()}{url}"
    response = requests.get(url, timeout=30)
    return response.content


def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 for display."""
    return base64.b64encode(image_bytes).decode()


def speech_to_text(audio_bytes: bytes, filename: str = "audio.webm") -> dict:
    """Convert speech to text using the API."""
    url = get_api_url()
    files = {
        "audio": (filename, audio_bytes, "audio/webm"),
    }
    try:
        response = requests.post(
            f"{url}/speech-to-text",
            files=files,
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# Page config
st.set_page_config(
    page_title="Image Generation Game",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .score-box {
        background: #2d2d44;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .score-value {
        font-size: 48px;
        font-weight: bold;
        color: #a855f7;
    }
    .history-item {
        display: inline-block;
        margin: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = False
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "current_image_url" not in st.session_state:
    st.session_state.current_image_url = None  # Local URL for display
if "current_public_url" not in st.session_state:
    st.session_state.current_public_url = None  # Public kie.ai URL for editing
if "reference_image" not in st.session_state:
    st.session_state.reference_image = None
if "best_score" not in st.session_state:
    st.session_state.best_score = 0
if "sensitivity" not in st.session_state:
    # Try to get current sensitivity from API
    try:
        sensitivity_result = get_sensitivity()
        if sensitivity_result.get("success"):
            st.session_state.sensitivity = sensitivity_result.get("sensitivity", 1.0)
        else:
            st.session_state.sensitivity = 1.0
    except:
        st.session_state.sensitivity = 1.0

# Title
st.title("🎨 Image Generation Game")
st.markdown("**Try to recreate the reference image using text prompts!**")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key
    api_key = st.text_input("kie.ai API Key", type="password")
    if st.button("Set API Key"):
        if api_key:
            result = set_api_key(api_key)
            if result.get("success"):
                st.session_state.api_key_set = True
                st.success("✅ API Key set!")
            else:
                st.error(f"❌ {result.get('message')}")
    
    # API Status
    st.divider()
    if st.button("Check API Status"):
        status = check_api_status()
        if status.get("status") == "ok":
            st.success(f"✅ API Online")
            st.info(f"Key configured: {status.get('api_key_configured')}")
        else:
            st.error(f"❌ API Error: {status.get('error', 'Unknown')}")
    
    # Reference image upload
    st.divider()
    st.header("📷 Reference Image")
    uploaded_file = st.file_uploader("Upload reference image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.session_state.reference_image = uploaded_file.read()
        st.success("✅ Reference image loaded!")
    
    # Best score
    st.divider()
    st.metric("🏆 Best Score", f"{st.session_state.best_score:.1f}%")
    
    # Similarity Rigour/Sensitivity
    st.divider()
    st.header("🎯 Similarity Rigour")
    st.caption("Higher = More Strict (Lower Scores)\nLower = More Lenient (Higher Scores)")
    
    sensitivity = st.slider(
        "Rigour Level",
        min_value=0.1,
        max_value=10.0,
        value=st.session_state.sensitivity,
        step=0.1,
        help="Higher values (2.0-5.0) make comparison more strict, resulting in lower similarity scores. Lower values (0.5-0.8) make it more lenient."
    )
    
    if sensitivity != st.session_state.sensitivity:
        # Update sensitivity in API
        result = set_sensitivity(sensitivity)
        if result.get("success"):
            st.session_state.sensitivity = sensitivity
            st.success(f"✅ Rigour set to {sensitivity:.1f}")
        else:
            st.error(f"❌ Failed to set rigour: {result.get('message', 'Unknown error')}")
    
    # Show current value
    st.info(f"**Current:** {st.session_state.sensitivity:.1f}")
    
    # Quick presets
    col_preset1, col_preset2, col_preset3 = st.columns(3)
    with col_preset1:
        if st.button("Lenient\n(0.5)", use_container_width=True):
            result = set_sensitivity(0.5)
            if result.get("success"):
                st.session_state.sensitivity = 0.5
                st.rerun()
    with col_preset2:
        if st.button("Normal\n(1.0)", use_container_width=True):
            result = set_sensitivity(1.0)
            if result.get("success"):
                st.session_state.sensitivity = 1.0
                st.rerun()
    with col_preset3:
        if st.button("Strict\n(3.0)", use_container_width=True):
            result = set_sensitivity(3.0)
            if result.get("success"):
                st.session_state.sensitivity = 3.0
                st.rerun()

# Main content
if not st.session_state.reference_image:
    st.warning("👆 Please upload a reference image in the sidebar to start the game!")
    st.stop()

# Two columns layout
col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Reference Image")
    st.image(st.session_state.reference_image, use_container_width=True)
    st.caption("Try to recreate this image!")

with col2:
    st.header("🖼️ Your Generated Image")
    
    if st.session_state.current_image_url:
        try:
            current_image = load_image_from_url(st.session_state.current_image_url)
            st.image(current_image, use_container_width=True)
            
            # Compare with reference (use current sensitivity)
            result = compare_images(
                st.session_state.reference_image,
                current_image,
                sensitivity=st.session_state.sensitivity
            )
            
            if result.get("success"):
                score = result.get("similarity_percentage", 0)
                st.markdown(f"""
                <div class="score-box">
                    <div>Similarity Score</div>
                    <div class="score-value">{score:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Update best score
                if score > st.session_state.best_score:
                    st.session_state.best_score = score
                    st.balloons()
            else:
                st.error(f"Compare error: {result.get('error')}")
        except Exception as e:
            st.error(f"Error loading image: {e}")
    else:
        st.info("Generate an image to see it here!")

# Speech-to-Text section (separate, just for transcription)
st.divider()
st.header("🎤 Speech-to-Text")

# Audio recording section
st.markdown("**Record audio to get text transcription:**")
audio_data = st.audio_input("Click microphone to record", label_visibility="visible")

# Show audio player if recorded
if audio_data:
    st.audio(audio_data, format="audio/webm")
    
    # Transcribe button
    transcribe_btn = st.button("📝 Transcribe Audio", type="primary", use_container_width=True)
    
    # Handle transcription
    if transcribe_btn:
        with st.spinner("🎤 Transcribing audio... (this may take a few seconds)"):
            audio_bytes = audio_data.read()
            result = speech_to_text(audio_bytes, "recording.webm")
            
            if result.get("success"):
                transcribed_text = result.get("text", "").strip()
                if transcribed_text:
                    # Save transcription to session state
                    st.session_state.transcribed_text = transcribed_text
                    st.success("✅ Audio transcribed successfully!")
                    st.rerun()  # Refresh to show transcription
                else:
                    st.warning("⚠️ Transcription returned empty text")
            else:
                error_msg = result.get("error", "Unknown error")
                st.error(f"❌ Transcription error: {error_msg}")

# Display transcription as text
if "transcribed_text" in st.session_state and st.session_state.transcribed_text:
    st.divider()
    st.markdown("### 📝 Transcription:")
    st.markdown(f"""
    <div style="background-color: #2d2d44; padding: 20px; border-radius: 10px; border-left: 4px solid #a855f7;">
        <p style="font-size: 16px; line-height: 1.6; color: #eee; margin: 0;">
            {st.session_state.transcribed_text}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("💡 You can copy this text and paste it into the prompt field below")

# Prompt input section
st.divider()
st.header("✏️ Enter Your Prompt")

# Simple text area for prompt
prompt_col1, prompt_col2 = st.columns([4, 1])

with prompt_col1:
    prompt = st.text_area(
        "Describe the image you want to generate:",
        placeholder="A cute cartoon dog with blue eyes...",
        height=100,
        label_visibility="visible"
    )

with prompt_col2:
    st.write("")  # Spacer
    st.write("")
    generate_btn = st.button("🚀 Generate", type="primary", use_container_width=True)

if generate_btn and prompt:
    # Clear prompt_from_audio after using it for generation
    if "prompt_from_audio" in st.session_state:
        del st.session_state.prompt_from_audio
    
    with st.spinner("🎨 Generating image... (this may take 30-60 seconds)"):
        result = generate_image(prompt)
        
        if result.get("success"):
            local_url = result.get("local_url")
            public_url = result.get("image_url")  # Public kie.ai URL
            if local_url:
                st.session_state.current_image_url = local_url
                st.session_state.current_public_url = public_url  # Save for editing
                st.session_state.generated_images.append({
                    "prompt": prompt,
                    "url": local_url,
                    "public_url": public_url,
                    "type": "generate"
                })
                st.success("✅ Image generated!")
                st.rerun()
            else:
                st.warning("Image generated but not saved locally")
        else:
            st.error(f"❌ Error: {result.get('error')}")

# Edit section (if we have a generated image)
if st.session_state.current_image_url:
    st.divider()
    st.header("🖌️ Edit Your Image")
    st.caption("Refine your generated image with additional prompts")
    
    edit_col1, edit_col2 = st.columns([4, 1])
    
    with edit_col1:
        edit_prompt = st.text_area(
            "Edit prompt:",
            placeholder="Add sunglasses, make the background blue...",
            height=80,
            key="edit_prompt"
        )
    
    with edit_col2:
        st.write("")
        st.write("")
        edit_btn = st.button("✨ Edit", type="secondary", use_container_width=True)
    
    if edit_btn and edit_prompt:
        # Use public kie.ai URL for editing (required by kie.ai API)
        public_url = st.session_state.current_public_url
        
        if not public_url:
            st.error("❌ No public URL available for editing. Please generate a new image first.")
        else:
            with st.spinner("🖌️ Editing image... (this may take 30-60 seconds)"):
                result = generate_image(edit_prompt, image_url=public_url)
                
                if result.get("success"):
                    local_url = result.get("local_url")
                    new_public_url = result.get("image_url")
                    if local_url:
                        st.session_state.current_image_url = local_url
                        st.session_state.current_public_url = new_public_url  # Update for next edit
                        st.session_state.generated_images.append({
                            "prompt": edit_prompt,
                            "url": local_url,
                            "public_url": new_public_url,
                            "type": "edit"
                        })
                        st.success("✅ Image edited!")
                        st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")

# History section
if st.session_state.generated_images:
    st.divider()
    st.header("📜 History")
    
    history_cols = st.columns(min(len(st.session_state.generated_images), 5))
    
    for i, item in enumerate(st.session_state.generated_images[-5:]):
        with history_cols[i % 5]:
            try:
                img_bytes = load_image_from_url(item["url"])
                st.image(img_bytes, use_container_width=True)
                
                icon = "🎨" if item["type"] == "generate" else "✨"
                st.caption(f"{icon} {item['prompt'][:30]}...")
            except:
                st.caption("Image unavailable")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888;">
    Made with ❤️ using Streamlit and kie.ai
</div>
""", unsafe_allow_html=True)

