# ================================================================
# Personal News Feed — Gradio + FastAPI hybrid for Hugging Face Spaces
# ================================================================

FROM python:3.9

# Create a non-root user for security
RUN useradd -m -u 1000 user
USER user

# Set Python path
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install dependencies
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the code
COPY --chown=user . /app

# Expose port 7860 (required by Hugging Face)
EXPOSE 7860

# Run the app (FastAPI + Gradio)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
