import pandas as pd
from transformers import pipeline
from .data_preprocessor import clean_text

class SentimentAnalyzer: # Zero-shot sentiment analysis
    def __init__(self, model_name="facebook/bart-large-mnli"):

        # Load and initialize model
        print(f"Loading sentiment analysis model: {model_name}...")

        try: # Use gpu if available
            self.classifier = pipeline("zero-shot-classification", model=model_name, device_map='auto')
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            self.classifier = None
        self.candidate_labels = ["positive", "neutral", "negative"]


    def analyze_text(self, text):
        if not text  or self.classifier is None:
            return 'neutral', 0.0
        try:
            # Perform zero-shot classification
            result = self.classifier(text, self.candidate_labels)
            sentiment = result['labels'][0]
            confidence = result['scores'][0]
            return sentiment, confidence
        except Exception as e:
            print(f"Error analyzing text: '{text[:20]}...': {e}")
            return 'neutral', 0.0


    def analyze_dataframe(self, df: pd.DataFrame, text_column: str):
        # Analyzes sentiment for a column in a Pandas DataFrame.
        if df.empty or text_column not in df.columns or self.classifier is None:
            print("Warning: DataFrame is empty, missing text column or model failed to load")
            if 'sentiment' not in df.columns:
                 df['sentiment'] = None
            if 'confidence' not in df.columns:
                 df['confidence'] = None
            return df # Return original df

        print(f"Analyzing sentiment for '{text_column}' column...")

        sentiments = []
        confidences = []

        # Iterate through the text column
        for index, text in df[text_column].items():
            if pd.notna(text):
                cleaned_text = clean_text(str(text))

                if cleaned_text:
                    sentiment, confidence = self.analyze_text(cleaned_text)
                    sentiments.append(sentiment)
                    confidences.append(confidence)
                else:
                    # Treat as neutral
                    sentiments.append('neutral')
                    confidences.append(0.0)
            else:
                # Original text was NaN
                sentiments.append('neutral')
                confidences.append(0.0)

        df['sentiment'] = sentiments
        df['confidence'] = confidences

        print("Sentiment analysis complete.")
        return df