# Overview

Personal news - select RSS feeds 
- categorize latest developments in the field for a day/week  
- Get an overall summary
- Get top N stories / papers / articles
- Explore individual source of Top N sorces  
- Get Summary, details and link  

<!-- ![Demo](assets\ui.gif)  -->
![Demo](https://raw.githubusercontent.com/w-winnie/PersonalNewsFeed/main/assets/ui.gif)  



# HOW TO RUN

## New env setup:  

conda create --name rss_venv python=3.11   
conda activate rss_venv  
pip install -r requirements.txt
<!-- pip install openai gradio feedparser beautifulsoup4  -->

### OR  

conda env create -f environment.yml

## env update:  
pip freeze > requirements.txt  
<!-- conda env export > environment.yml   -->
conda env export --from-history > environment.yml  

## env variables:  
set OPENAO_API_KEY=sk-..
set LOG_DIR=./data/logs

## run:

### Console
python -m src.main
<!-- python app/main.py -->
### Application
python -m frontend.gradio_app2
<!-- python frontend/gradio_src.py -->

# Folder structure
rss_feed_app/  
├── app/  
│   ├── __init__.py  
│   ├── main.py           # file for console run  
|   |── config.py           # file with application config (prompt selection) - TODO_config (fill in your own audience description and urls)  
│   ├── llm_client.py     # Functions for connecting to an LLM (openai)  
│   ├── prompt_templates.py  # Prompt template JSON objects - TODO_prompt_template (fill in your own prompts)  
│   ├── response_parser.py   # Functions for parsing LLM response  
│   ├── token_utils.py       # Function for cost estimation  
│   ├── summarizer.py       # Mesage creator (combining prompt logic)  
│   ├── summary_manager.py   # Wrapper on summarizer - for easy access to both UI and console  
│   ├── logger.py         # Logging setup and utilities  
│   └── rss_utils.py      # Functions for fetching and parsing RSS feeds  
├── frontend/  
│   ├── __init__.py  
│   └── gradio_src.py     # Gradio-based frontend application minimal  
|   └── gradio_src.py     # Gradio-based frontend application final  
├── data/  
├── requirements.txt      # Python dependencies for pip   
├── environment.yml       # Conda environment specification  
├── README.md             # Project documentation  
├── .env                  # Env file with OPENAI_API_KEY  
└── .gitignore            # Git ignore file  

# Deployment instructions
HF private space  

git remote add hf <hf-repo-url>
git checkout hf main   
git pull origin main --allow-unrelated-histories   
git push hf main    
