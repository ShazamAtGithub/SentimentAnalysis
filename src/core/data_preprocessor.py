import re
import emoji
import string

def clean_text(text):
    comment = str(text)
    # Skip purely numeric comments
    if comment.replace('.', '', 1).isdigit():
        return None
    # Removes mentions, hashtags, urls, punctuation and emojis
    comment = comment.lower()
    comment = re.sub(r"@[\w_]+", "", comment)
    comment = re.sub(r"#\w+", "", comment)
    comment = re.sub(r"https?://\S+|www\.\S+", "", comment)
    comment = comment.translate(str.maketrans("", "", string.punctuation))
    comment = emoji.replace_emoji(comment, replace='')
    comment = re.sub(r"\s+", " ", comment).strip()

    return comment if comment else None

