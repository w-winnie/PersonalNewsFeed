# app/config.py
class Config:

    CONTENT_TYPES = ["news", "papers"]
    
    SUBJECT_AREAS = {
        "astro": {
            "news": [
                "https://www.sciencedaily.com/rss/space_time/astrophysics.xml",

                "https://phys.org/rss-feed/space-news",

                "https://www.esa.int/rssfeed/TopNews",
                "https://www.esa.int/rssfeed/Our_Activities/Space_Science",

                "https://www.nasa.gov/news-release/feed",  # OR "https://www.nasa.gov/feed/",
                "https://www.nasa.gov/technology/feed/",
                "https://www.nasa.gov/aeronautics/feed/",
                "https://www.nasa.gov/missions/station/feed/",
                "https://www.nasa.gov/missions/artemis/feed/",

                "https://www.space.com/feeds/all",
                "https://www.space.com/feeds/tag/space-exploration",
                "https://www.space.com/feeds/tag/space-science",
                "https://www.space.com/feeds/tag/astronomy",
                "https://www.space.com/feeds/tag/universe",
                "https://www.space.com/feeds/tag/stargazing",

                "https://skyandtelescope.org/rss",

                "https://news.mit.edu/topic/mitspace-rss.xml",
                "https://news.mit.edu/topic/mitastrophysics-rss.xml",
                "https://news.mit.edu/topic/mitspace-exploration-rss.xml"
            ],
            "papers": [
                "http://export.arxiv.org/rss/astro-ph"
                # "https://rss.arxiv.org/rss/astro-ph.CO",
                # "https://rss.arxiv.org/rss/astro-ph.GA",
                # "https://rss.arxiv.org/rss/astro-ph.HE",
                # "https://rss.arxiv.org/rss/astro-ph.IM",
                # "https://rss.arxiv.org/rss/astro-ph.SR",
                # "https://rss.arxiv.org/rss/astro-ph.EP"
            ],
        },
        "ai": {
            "news": [
                "https://medium.com/feed/@Pinterest_Engineering",
                "https://medium.com/feed/netflix-techblog",
                "https://medium.com/feed/airbnb-engineering",
                "https://distill.pub/rss.xml",
                "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml",
                "https://bair.berkeley.edu/blog/feed.xml",
                "https://vectorinstitute.ai/feed/",
                "https://aws.amazon.com/blogs/ai/feed",
                "https://research.google/blog/rss",
                "https://www.deepmind.com/blog/rss.xml",
                "https://openai.com/news/rss.xml",
                "https://www.microsoft.com/en-us/research/feed/",
                "https://developer.nvidia.com/blog/feed/",
                "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss"
            ],
            "papers": [
                "https://rss.arxiv.org/rss/cs.AI",
                "https://rss.arxiv.org/rss/stat.ML",
                "https://rss.arxiv.org/rss/cs.LG",
                "https://rss.arxiv.org/rss/cs.CV",  
                "https://rss.arxiv.org/rss/cs.CL"
                "https://rss.arxiv.org/rss/cs.GR",
                "https://rss.arxiv.org/rss/cs.GT",
                "https://rss.arxiv.org/rss/cs.CG",
                "https://rss.arxiv.org/rss/cs.NE"

                # "https://allenai.org/papers",# "https://huggingface.co/blog/feed.xml"# "https://huggingface.co/papers/feed.xml" #"https://eng.uber.com/category/articles/ai/feed"
            ],
        },
    }

    AUDIENCES = {
        "general": "general audience with an interest in science, non-specialists, educated laypeople",
        "astro_enthusiasts": "scientifically literate readers (e.g., grad students, early career researchers), readers familiar with scientific concepts but not necessarily specialists in astrophysics",
        "ai_enthusiasts": "AI researchers and practitioners interested in latest advancements and breakthroughs, readers with a technical background in AI and machine learning"
    }



# config_options = ConfigOptions()