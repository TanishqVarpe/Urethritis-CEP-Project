from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from io import StringIO
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


default_df = pd.read_csv("data/urethritis_data.csv")
print("Sample data:\n", default_df[["ua_blood", "ua_bacteria", "UTI_diag"]].head(10))

@app.post("/api/diagnose")
async def diagnose(
    symptoms: str = Form(...),
    file: UploadFile = File(None)  
):
    
    try:
        if file:
            contents = await file.read()
            df = pd.read_csv(StringIO(contents.decode("utf-8")))
            print(f"Using uploaded file: {file.filename}")
        else:
            df = default_df.copy()
            print("Using default dataset.")
    except Exception as e:
        return {
            "type": "Error",
            "recommendation": f"Failed to process uploaded file: {str(e)}"
        }

   
    input_keywords = [word.strip().lower() for word in symptoms.split()]

   
    symptom_map = {
        "burning": ["ua_blood", "ua_bili"],
        "pain": ["ua_   blood", "UTI_diag"],
        "discharge": ["ua_bacteria", "ua_leukocyte_esterase"],
        "urination": ["ua_blood", "ua_bili", "UTI_diag"],
        "itching": ["ua_protein", "ua_nitrite"],
        "fever": ["UTI_diag"],
        "swelling": ["ua_protein"],
        "smell": ["ua_nitrite"]
    }

   
    matched_columns = set()
    for word in input_keywords:
        if word in symptom_map:
            matched_columns.update(symptom_map[word])

    if not matched_columns:
        return {
            "type": "Unknown",
            "recommendation": "Symptoms not specific enough for diagnosis. Please consult a doctor."
        }

   
    filtered_df = df.copy()
    keywords = "yes|positive|abnormal|many|trace|moderate|few"

    for col in matched_columns:
        if col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[col].astype(str).str.lower().str.contains(keywords, na=False)]

    
    if not filtered_df.empty:
        result_row = filtered_df.iloc[0]
        return {
            "type": "Probable Urethritis",
            "recommendation": f"Antibiotic: {result_row.get('abxUTI', 'Not specified')}"
        }

    return {
        "type": "Unknown",
        "recommendation": "No matches found. Please consult a doctor."
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return {"error": "Only CSV files are supported."}

    try:
        contents = await file.read()
        df_uploaded = pd.read_csv(StringIO(contents.decode("utf-8")))
        preview = df_uploaded.head().to_dict(orient="records")

        return {
            "message": f"File '{file.filename}' uploaded successfully!",
            "preview": preview
        }

    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}
