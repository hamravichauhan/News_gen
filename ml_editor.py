import torch
from transformers import pipeline

# Load a fast, lightweight summarization model (runs locally on CPU or Apple Silicon MPS)
device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

print(f"[*] Initializing local ML Editor on {device.upper()}...")
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    device=device
)

def ml_generate_takeaways(article_text, max_bullets=3):
    """Summarizes raw text into clean, human-readable takeaway points."""
    if not article_text or len(article_text.split()) < 40:
        return []

    # Truncate input to fit model context window
    truncated_text = " ".join(article_text.split()[:400])
    
    summary = summarizer(
        truncated_text,
        max_length=90,
        min_length=30,
        do_sample=False
    )[0]["summary_text"]

    # Split summary into distinct takeaway sentences
    sentences = [s.strip() for s in summary.split(". ") if len(s.strip()) > 15]
    return sentences[:max_bullets]