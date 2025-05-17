import pandas as pd
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.core.data_preprocessor import clean_text
from src.core.sentiment_analyzer import SentimentAnalyzer

app = FastAPI(
    title="Instagram Comment Sentiment Analysis API",
    description="API to perform sentiment analysis on Instagram comments from an uploaded Excel file.",
    version="1.0.0",
)

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()

class CommentSentiment(BaseModel):
    original_comment: Optional[str] = None
    cleaned_comment: Optional[str] = None
    sentiment: Optional[str] = 'neutral'
    confidence: Optional[float] = 0.0

class SentimentAnalysisResult(BaseModel):
    filename: str
    total_comments_processed: int
    analysis_results: List[CommentSentiment]

@app.post("/analyze_comments", response_model=SentimentAnalysisResult)
async def analyze_comments_endpoint(excel_file: UploadFile = File(...)):
    if not excel_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Upload an Excel file.")

    excel_content = await excel_file.read()
    try:
        df = pd.read_excel(io.BytesIO(excel_content))
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"Error reading Excel file: {e}")

    comment_col = next((col for col in df.columns if col.strip().lower() == 'comment'), None)

    if not comment_col:
        try:
            df = pd.read_excel(io.BytesIO(excel_content), skiprows=6)
            comment_col = next((col for col in df.columns if col.strip().lower() == 'comment'), None)
        except Exception:
            raise HTTPException(status_code=400, detail="Excel file must contain a 'Comment' column.")

    analysis_results = []

    for index, row in df.iterrows():
        original_text = row[comment_col]

        if pd.isna(original_text):
            original_text_for_pydantic = None
        else:
            original_text_for_pydantic = str(original_text)

        cleaned_text = clean_text(original_text_for_pydantic) if original_text_for_pydantic else None
        # Analyze text only if cleaned_text is not None or empty
        sentiment, confidence = ('neutral', 0.0)
        if cleaned_text:
             sentiment, confidence = sentiment_analyzer.analyze_text(cleaned_text)

        analysis_results.append(CommentSentiment(
            original_comment=original_text_for_pydantic,
            cleaned_comment=cleaned_text,
            sentiment=sentiment,
            confidence=confidence
        ))

    return SentimentAnalysisResult(
        filename=excel_file.filename,
        total_comments_processed=len(df),
        analysis_results=analysis_results
    )

@app.get("/")
async def read_root():
    return {"message": "Instagram Sentiment Analysis API is running. Go to /docs for documentation and try out."}
