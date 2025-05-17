import argparse
import pandas as pd
import os
import sys
from src.core.sentiment_analyzer import SentimentAnalyzer
from src.extract.instagram_extractor import InstagramCommentsExtractor, website


def load_excel_with_comment_column(file_path):
    df = None
    comment_col = None

    print(f"Loading Excel file: {file_path}")
    try:
        df = pd.read_excel(file_path)
        comment_col = next((col for col in df.columns if col.strip().lower() == 'comment'), None)
        if not comment_col:
            # Skipping the first 6 rows
            try:
                df = pd.read_excel(file_path, skiprows=6)
                comment_col = next((col for col in df.columns if col.strip().lower() == 'comment'), None)
            except Exception as e_skip:
                 print(f"Warning: Could not load file by skipping rows. {e_skip}")
                 if df is not None and df.empty:
                      df = None
    except Exception as e:
        print(f"Error: Could not load Excel file or comment column is missing. {e}")

    return df, comment_col


def main():

    parser = argparse.ArgumentParser(description='Analyze sentiment of Instagram comments from an Excel file or directly from an Instagram URL')

    input_source_group = parser.add_mutually_exclusive_group(required=True) # Either url or Excel file as input

    # Non-interactive commandline arguments
    input_source_group.add_argument('--input-file', '-i', help='Path to an existing Excel file with Instagram comments.')
    input_source_group.add_argument('--instagram-url', '-u', help='Instagram post URL')

    parser.add_argument('--output', '-o', help='Path to save the output Excel file')
    parser.add_argument('--headless', action='store_true', help='Run the extractor in headless mode.')

    args = parser.parse_args()
    # Initialize path variables and other arguments
    input_file_path = args.input_file
    instagram_url = args.instagram_url
    output_file_path = args.output
    headless_mode = args.headless
    exporter_url = website

    df, comment_col = None, None

    if input_file_path:
        if not os.path.exists(input_file_path):
            print(f"Error: Input file not found at {input_file_path}")
            sys.exit(1)

        df, comment_col = load_excel_with_comment_column(input_file_path)

        if df is None or comment_col is None:
            print(f"Error: No 'comment' column found in {input_file_path}")
            sys.exit(1)

        output_file_path = output_file_path or input_file_path

    elif instagram_url:
        print(f"Extracting comments from: {instagram_url}")
        extraction_dir = output_file_path or os.path.join(os.getcwd(), "extracted_comments")
        os.makedirs(extraction_dir, exist_ok=True)

        extractor = InstagramCommentsExtractor(exporter_url=exporter_url, headless=headless_mode, download_dir=extraction_dir)
        downloaded_excel_path = extractor.extract_comments(instagram_url)
        extractor.close()

        if downloaded_excel_path:
            df, comment_col = load_excel_with_comment_column(downloaded_excel_path)
            output_file_path = output_file_path or downloaded_excel_path.replace('.xlsx', '_analyzed.xlsx')

    if df is not None and comment_col is not None:
        analyzer = SentimentAnalyzer()
        df_analyzed = analyzer.analyze_dataframe(df, comment_col)

        df_analyzed.to_excel(output_file_path, index=False)
        print(f"Sentiment analysis complete. Results saved to {output_file_path}")
    else:
        print("No valid data found. Exiting.")
        sys.exit(1)


if __name__ == '__main__':
    main()
