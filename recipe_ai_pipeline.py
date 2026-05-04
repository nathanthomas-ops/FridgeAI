# Required installations:
# pip install streamlit ultralytics torch torchvision openai pillow

import openai
import os
import tempfile
import base64
import streamlit as st

# --- STEP 0.5: GPT-4 Recipe Generation ---
openai.api_key = os.getenv("OPEN_AI_KEY")

# --- STEP 1: OpenAI Vision for Ingredient Detection ---

def get_ingredients_with_openai(image_path):
    """
    Uses OpenAI Vision API (GPT-4o or GPT-4-vision-preview) to detect ingredients in an image.
    Returns a list of detected ingredient names.
    """
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    prompt = (
        "You are an expert food recognition AI. Carefully examine the image and "
        "list the most likely food items or ingredients you see (e.g., 'milk, eggs, butter, chocolate'). "
        "If you see a food item like chocolate, bread, or cheese, state the food item itself (e.g., 'chocolate'), "
        "and do NOT list the ingredients that make up that food (e.g., do NOT list 'cocoa, sugar, milk' for chocolate). "
        "If you see packaging, use all visual clues, text, and context to infer what food or drink is inside. "
        "Never say 'Unknown', 'I don't know', or anything vague. Always make your best, most specific guess, "
        "even if you are uncertain. If you are unsure, use your knowledge of common foods and packaging to infer "
        "the most probable answer. Ignore nutrition, vitamin, or packaging details (like 'Vitamin D', 'organic', 'best by'). "
        "Return only a comma-separated list of food ingredient names, no extra text."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]}
        ],
        max_tokens=100
    )
    content = response.choices[0].message.content
    # Parse comma-separated list
    ingredients = [i.strip() for i in content.split(",") if i.strip()]
    return ingredients

# --- STEP 2: Get Ingredients using OpenAI Vision ---
def get_ingredients(image_path):
    return get_ingredients_with_openai(image_path)


def generate_recipe(ingredients):
    prompt = (
        "You are a helpful home cook assistant. Using the following ingredients, create a practical, easy-to-follow recipe that anyone can make at home: "
        f"{', '.join(ingredients)}.\n"
        "If there are two or more detected ingredients, you must use a combination of them in the recipe. Do not create a recipe based on only the last ingredient or a single ingredient when multiple are available. Always base the recipe on a mix of the provided ingredients. "
        "Give the dish a clear, simple name. Start with a short, friendly introduction or tip about the dish. "
        "Format the recipe as clean, modern HTML for a web page: use a large heading for the dish name. "
        "Create clear, visually separated sections for the introduction, ingredients, procedure, and a section called 'Suggested Groceries'. Use headings (like h2 or h3) and spacing to separate each section. "
        "For the ingredients, use a visually appealing list (but do NOT use bullet points or unordered lists). For the procedure, use a clear, easy-to-follow numbered list (do NOT center the elements). "
        "In the 'Suggested Groceries' section, use the subtitle: Suggested groceries in order to make <b style=\"color:#2196f3\">Dish Name</b>, where the dish name is bolded and styled in a standout color. Only suggest groceries that can be found in a regular grocery store. "
        "Display the name of the potential dish, and use an HTML <details> dropdown (with a <summary> tag) so the user can click to see more about the dish, including the recipe and instructions. Output only the HTML, no extra text. "
        "At the end, add a clear section listing the ingredients the user does NOT have (i.e., ingredients required for the recipe but not in the provided list) and must buy in order to complete the recipe."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- STREAMLIT APP ---
st.set_page_config(page_title="AI Recipe Generator", layout="centered")
st.title("🍽️ AI Recipe Generator")
st.write("Upload an image of your ingredients. We'll detect them and create a recipe!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.image(tmp_path, caption='Uploaded Image', use_column_width=True)

    with st.spinner("Detecting ingredients and generating recipe..."):
        ingredients = get_ingredients(tmp_path)
        recipe = generate_recipe(ingredients)

    st.subheader("Detected Ingredients")
    st.write(", ".join(ingredients))

    st.subheader("Generated Recipe")
    st.text_area("Recipe", recipe, height=400)

    os.remove(tmp_path)
