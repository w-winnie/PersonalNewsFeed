# app/config.py
# TODO: Fill in your own RSS feeds and audience descriptions and rename to config.py
class Config:

    CONTENT_TYPES = ["news", "papers"]

    SUBJECT_AREAS = {
        "astrophysics": {
            "news": [
                # put astrophysics news feeds here
            ],
            "papers": [
                # put astrophysics research feeds here
            ],
        },
        "ai": {
            "news": [
                # future AI news feeds
            ],
            "papers": [
                # future AI research feeds
            ],
        },
    }

    AUDIENCES = {
        "general": "general audience with an interest in science..",
        "astro_enthusiasts": "Astronomy & Physis enthusiasts..",
        "ai_enthusiasts": "AI enthusiasts.."
    }

# config_options = ConfigOptions()