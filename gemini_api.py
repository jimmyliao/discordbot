import google.generativeai as genai
import os
from config import GEMINI_API_KEY
import logging
from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
from collections import defaultdict
import re  # Import the regular expression module
from google.api_core.exceptions import InvalidArgument # Import InvalidArgument

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
PROJECT_ID = "gde-kj"  # Replace with your project ID if different
LOCATION = "us-central1"  # Replace with your location if different
IMAGEN_MODEL_NAME = "imagen-3.0-generate-002"
GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"
PROMPT_SYSTEM = "請以繁體中文回應"
PROMPT_ERROR_EXCEPTION = "很抱歉，我們無法回答您的問題，請稍後再試。"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_NUMBER_OF_IMAGES = 1
DETECT_LANGUAGE_PROMPT = "What language is this text in? Just response the language name: "
TRANSLATE_PROMPT = "Translate the following text to English: "
FALLBACK_IMAGE_RESPONSE = "無法辨識您的圖片描述，已隨機產生圖片。"

# Global Variables
image_generation_model = None
chat_session = None
user_language_memory = defaultdict(lambda: "zh-TW")  # Default to Traditional Chinese

def initialize_gemini_model():
    """Initializes the Gemini model."""
    global chat_session
    try:
        logging.info("Initializing Gemini model...")
        genai.configure(api_key=GEMINI_API_KEY)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        gemini_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            generation_config=generation_config,
        )

        chat_session = gemini_model.start_chat(history=[{
            "role": "user",
            "parts": [PROMPT_SYSTEM],
        }])
        logging.info("Gemini model initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize Gemini model: {e}")
        raise

def initialize_imagen_model():
    """Initializes the Imagen 3 model."""
    global image_generation_model
    try:
        logging.info("Initializing Imagen 3 model...")
        logging.info(f"Initializing Vertex AI with project: {PROJECT_ID}, location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        image_generation_model = ImageGenerationModel.from_pretrained(IMAGEN_MODEL_NAME)
        logging.info("Imagen 3 model initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize Imagen 3 model: {e}")
        image_generation_model = None
        logging.error(f"Please check: 1. Project ID and location are correct. 2. Vertex AI API is enabled. 3. You have authenticated with Google Cloud. 4. You have the necessary permissions. 5. Quota project is set correctly.")
        raise

def detect_language(text):
    """Detects the language of the given text using Gemini."""
    try:
        logging.info(f"Detecting language of text: {text}")
        response = chat_session.send_message(DETECT_LANGUAGE_PROMPT + text)
        detected_language = response.text.strip()
        logging.info(f"Detected language: {detected_language}")
        return detected_language
    except Exception as e:
        logging.exception(f"Error detecting language: {e}")
        return "zh-TW"  # Default to Traditional Chinese if detection fails

def translate_to_english(text):
    """Translates the given text to English using Gemini."""
    try:
        logging.info(f"Translating text to English: {text}")
        response = chat_session.send_message(TRANSLATE_PROMPT + text)
        translated_text = response.text
        logging.info(f"Translated text: {translated_text}")
        return translated_text
    except Exception as e:
        logging.exception(f"Error translating text: {e}")
        return None

def generate_text(prompt):
    """Generates text using the Gemini model."""
    try:
        logging.info(f"Generating text for prompt: {prompt}")
        response = chat_session.send_message(prompt)
        logging.info(f"Generated text: {response.text}")
        return response.text
    except Exception as e:
        logging.exception(f"Error generating text: {e}")
        return PROMPT_ERROR_EXCEPTION

def generate_image(prompt, num_images=DEFAULT_NUMBER_OF_IMAGES, aspect_ratio=DEFAULT_ASPECT_RATIO):
    """Generates images using the Imagen 3 model.

    Args:
        prompt: The text prompt for image generation.
        num_images: The number of images to generate.
        aspect_ratio: The aspect ratio of the images.

    Returns:
        A list of image objects or None if an error occurred.
    """
    if image_generation_model is None:
        logging.error("Imagen 3 model is not initialized.")
        return None
    try:
        logging.info(f"Generating {num_images} images for prompt: {prompt}")
        images_response = image_generation_model.generate_images(
            prompt=prompt,
            number_of_images=num_images,
            aspect_ratio=aspect_ratio,
            negative_prompt="",
            person_generation="",
            safety_filter_level="",
            add_watermark=True,
        )
        images = images_response.images  # Get the list of images
        logging.info(f"Generated {len(images)} images.")  # Use len on the list
        return images
    except Exception as e:
        logging.exception(f"Error generating images: {e}")
        return None

def process_prompt(prompt, user_id):
    """Processes the prompt and either generates text or images.

    Args:
        prompt: The user's prompt.
        user_id: The ID of the user sending the prompt.

    Returns:
        Either the generated text or a list of image objects.
    """
    detected_language = detect_language(prompt)
    user_language_memory[user_id] = detected_language
    logging.info(f"User {user_id} prompt language: {detected_language}")

    if prompt.startswith("image:"):
        image_prompt = prompt[6:].strip()  # Remove "image:" prefix and any leading/trailing spaces
        if not image_prompt:
            return "請在 `image:` 後面輸入圖片描述"

        if detected_language != "English":
            translated_prompt = translate_to_english(image_prompt)
            if translated_prompt:
                images = generate_image(translated_prompt)
                if images:
                    return images
                else:
                    return PROMPT_ERROR_EXCEPTION
            else:
                return PROMPT_ERROR_EXCEPTION
        else:
            images = generate_image(image_prompt)
            if images:
                return images
            else:
                return PROMPT_ERROR_EXCEPTION
    else:
        return generate_text(prompt)

# Initialize models when the module is loaded
try:
    initialize_gemini_model()
    initialize_imagen_model()
except Exception as e:
    logging.error(f"Failed to initialize models: {e}")
    exit(1)


if __name__ == '__main__':
    # Test cases
    # test_prompt_text = "請介紹 Gemini API"
    # result_text = process_prompt(test_prompt_text, "test_user")
    # print(f"Text Result: {result_text}")

    test_prompt_image = "image: สงครามแมว"
    result_image = process_prompt(test_prompt_image, "test_user")
    if result_image and isinstance(result_image, list):
        print(f"Image Result: {len(result_image)} images generated.")
        # You can save the images here, for example:
        for i, image in enumerate(result_image):
            image.save(f"image_{i}.png")
    elif isinstance(result_image, str):
        print(f"Image Result: {result_image}")
    else:
        print(f"Image Result: Error generating images.")

    # test_prompt_image_empty = "image:"
    # result_image_empty = process_prompt(test_prompt_image_empty, "test_user")
    # print(f"Image Empty Result: {result_image_empty}")

    # # Test the new translation extraction
    # test_translation_text = "สงครามแมว"
    # result_translation = translate_to_english(test_translation_text)
    # print(f"Translation Result: {result_translation}")

    # test_translation_text2 = "你好"
    # result_translation2 = translate_to_english(test_translation_text2)
    # print(f"Translation Result2: {result_translation2}")

    # test process_prompt with multiple language
    # result_image_empty = process_prompt("image: 你好", "test_user")
    # print(f"Image Empty Result: {result_image_empty}")
