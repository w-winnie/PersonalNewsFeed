# app/config.py
class Config:

    CONTENT_TYPES = ["news", "papers"]

    SUBJECT_AREAS = {
        "astrophysics": {
            "news": [
                "https://www.space.com/feeds/all",
                # "https://news.mit.edu/topic/mitastrophysics-rss.xml",
                # "https://news.mit.edu/topic/mitspace-rss.xml",
                # "https://www.nasa.gov/news-release/feed/",
                # "https://www.esa.int/rssfeed/Our_Activities/Space_Science",
            ],
            "papers": [
                # "http://export.arxiv.org/rss/astro-ph",
                "https://rss.arxiv.org/rss/astro-ph.CO"
                # "https://phys.org/rss-feed/space-news/astrophysics/"
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
        "general": "general audience with an interest in science, non-specialists, educated laypeople",
        "astro_enthusiasts": "scientifically literate readers (e.g., grad students, early career researchers), readers familiar with scientific concepts but not necessarily specialists in astrophysics",
        "ai_enthusiasts": "AI researchers and practitioners interested in latest advancements and breakthroughs, readers with a technical background in AI and machine learning"
    }

    


# config_options = ConfigOptions()