# Instagram Sentiment Analysis Tool

An instagram sentiment analysis tool for performing zero-shot sentiment classification using Hugging Face transformer models.

## Overview

This project provides both a command-line interface (CLI) and a web API for performing sentiment analysis on Instagram comments. It uses the pre-trained `facebook/bart-large-mnli` model to classify comments as positive, neutral, or negative, and a confidence score for each classification.

## Key Features

- **Dual interfaces**: Use either the CLI or API 
- **Sentiment Classification**: Accurately categorizes comments into positive, neutral, or negative sentiments
- **Confidence Scoring**: Provides confidence score for each prediction
- **Flexible Input Options**: Process comments from Excel files or extract them directly from Instagram posts

## Note 
- **Headless usage is not recommended for now.**
- **The direct url for extraction website is not provided due to uncertainty regarding legal usage restrictions.**

## Installation

```bash
# Clone the repository
git clone https://github.com/ShazamAtGithub/SentimentAnalysis.git
cd SentimentAnalysis
```
**Create and activate virtual environment**
```bash

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The CLI supports two primary workflows:

1. **Analyze comments from an Excel file:**

```bash
python -m src.cli.main --input-file /path/to/your/comments.xlsx --output /path/to/save/results.xlsx
```

2. **Extract and analyze comments from an Instagram URL:**

```bash
python -m src.cli.main --instagram-url https://www.instagram.com/p/YOUR_POST_ID/ --output /path/to/save/results.xlsx
```

Optional arguments:
- `--headless`: Run browser in headless mode 
- `--output`: Specify output file path 

### Web API

The Web API is provided for demonstration purposes and is intended for local use only.

1. **Start the API server:**

```bash
uvicorn src.api.main:app --reload
```

2. **Access the interactive documentation:**
   - Open your web browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Use the interactive interface to upload Excel files containing Instagram comments (try out)

> **Note:** The API version can only process pre-extracted comments from Excel files and does not include the Instagram data extraction functionality available in the CLI version.

## Input Format

The expected Excel file format should contain instagram comments column 'Comment'

## Output

- **CLI**: Results are appended to the input Excel file or saved to a new file if specified
- **API**: Results are returned as JSON with sentiment classifications and confidence scores



