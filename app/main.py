from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.services.verifier import verify_document
from app.services.sarvam_service import process_document
from app.services.action_engine import build_action_plan
from app.services.form_service import (
    build_form_result,
    extract_document_text
)
from app.services.form_explainer import explain_form_fields
from app.services.scheme_service import (
    get_all_schemes,
    get_categories,
    get_schemes_by_category,
    search_schemes
)

app = FastAPI(title="DocuSaathi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "DocuSaathi backend is running!"}


@app.get("/verify-test")
def verify_test():
    return {
        "status": "uncertain",
        "message": "Verification test endpoint"
    }


@app.post("/verify")
async def verify(file: UploadFile = File(...)):
    file_contents = await file.read()
    file_size = len(file_contents)

    result = verify_document(
        filename=file.filename,
        content_type=file.content_type,
        file_size=file_size,
        file_contents=file_contents
    )

    return {
        "filename": file.filename,
        "verification": result
    }


@app.post("/process-document")
async def process_uploaded_document(
    file: UploadFile = File(...),
    language: str = "English"
):
    print("Selected language:", language)

    file_contents = await file.read()

    # 1. Verify document
    verification = verify_document(
        filename=file.filename,
        content_type=file.content_type,
        file_size=len(file_contents),
        file_contents=file_contents
    )

    # 2. Stop if the file itself is invalid
    if verification["status"] == "suspicious":
        return {
            "filename": file.filename,
            "verification": verification,
            "message": "Document could not pass the basic verification checks."
        }

    # 3. Process document with Sarvam
    extracted_data = process_document(
        filename=file.filename,
        file_contents=file_contents,
        content_type=file.content_type,
        language=language
    )

    # 4. Build action plan
    action_plan = build_action_plan(extracted_data)

    # 5. Return everything to frontend
    return {
        "filename": file.filename,
        "verification": verification,
        "document": extracted_data.model_dump(),
        "action_plan": action_plan
    }
@app.get("/schemes")
def all_schemes():
    return {
        "schemes": get_all_schemes()
    }


@app.get("/schemes/categories")
def scheme_categories():
    return {
        "categories": get_categories()
    }


@app.get("/schemes/category/{category}")
def schemes_by_category(category: str):
    return {
        "schemes": get_schemes_by_category(category)
    }


@app.get("/schemes/search")
def scheme_search(q: str = ""):
    return {
        "schemes": search_schemes(q)
    }

@app.post("/fill-form")
async def fill_form(file: UploadFile = File(...)):

    file_contents = await file.read()

    text = extract_document_text(
        file_contents,
        file.content_type or ""
    )


    # Detect the form and its fields
    form_result = build_form_result(text)


    # Explain every detected field
    if form_result.get("fields"):

        explained_fields = explain_form_fields(
            form_result["fields"],
            text
        )

        form_result["fields"] = explained_fields


    return {
        "filename": file.filename,
        "form": form_result
    }