from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from recipe_ai_pipeline import get_ingredients, generate_recipe
import os
import tempfile

app = FastAPI()

# Allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/detect-ingredients")
async def detect_ingredients(file: UploadFile = File(...)):
    """Detect ingredients in an uploaded image."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    try:
        temp_file.write(await file.read())
        temp_file.close()
        ingredients = get_ingredients(temp_file.name)
        return {"ingredients": ingredients}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

@app.post("/generate-recipe")
async def recipe(ingredients: str = Form(...)):
    """Generate a recipe from a comma-separated list of ingredients."""
    try:
        ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]
        recipe = generate_recipe(ingredient_list)
        return {"recipe": recipe}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
