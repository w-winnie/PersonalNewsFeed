# app/prompt_templates.py

PROMPT_TEMPLATES = {
    "news": {
        "entry": """
            Summarize the following {subject_area} article. Include:
                - The topic being discussed
                - The date this is happening / happened
                - Why this is exciting
                - Any other relevant information

            Avoid copying directly from the summary unless unavoidable.

            Title: {title}
            Summary: {summary}
            Link: {link}""",

        "bulk": """
            You are a science writer summarizing recent developments in {subject_area}. Use the articles below to write a clear, engaging, and structured overview.

            1. **Group the articles into themes** based on common topics, questions, or areas of research.
            2. For each theme:
               - Briefly describe the shared topic or problem.
               - Summarize the key contributions of relevant articles.
               - Include timing and relevance where applicable.
            3. **After the summary**, output a clearly marked section listing the most notable individual articles.

            ---

            ### Top Sources

            List the most impactful or interesting articles using the exact format below. Include only {top_entries} articles.

            Format (strictly follow this line structure — one per article):

            `Title` - `Link` - `One-line summary`

            Example:

            Top Source Links:
            1. Dark Matter Mapping Breakthrough - https://example.com/article1 - New simulation reveals potential dark matter distribution.
            2. AI Accelerates Galaxy Classification - https://example.com/article2 - Researchers apply neural networks to automate morphology detection.

            ---

            Limit total response to {summary_length} characters.

            ### Articles:
            {blocks}

        """
    },
    
    "papers": {
        "entry": """
             Summarize the following {subject_area} paper. Include:
                 - The core idea or research question
                 - The methods used (if available)
                 - Key findings or contributions
                 - Context: why this work matters
                 - Any implications or broader relevance

             Avoid copying directly from the abstract unless unavoidable.

             Title: {title}
             Abstract: {summary}
             Link: {link}""",

        "bulk": """
            Based on the papers below, write a summary of what’s happening today in {subject_area} research.

            1. **Group the papers into themes** based on their topics, types or research questions 
            2. For each theme, summarize:
               - The key questions or ideas being explored
               - The methods used (if relevant)
               - The main findings or proposals
               - Why it matters or how it fits into ongoing research
            3. **After the summary**, output a clearly marked section listing the most notable individual papers.

            ---

            ### Top Sources

            List the most impactful or interesting papers using the exact format below. Include only {top_entries} papers.

            Format (strictly follow this line structure — one per article):

            `Title` - `Link` - `One-line summary`

            Example:

            Top Source Links:
            1. Dark Matter Mapping Breakthrough - https://example.com/article1 - New simulation reveals potential dark matter distribution.
            2. AI Accelerates Galaxy Classification - https://example.com/article2 - Researchers apply neural networks to automate morphology detection.

            ---

            Limit total response to {summary_length} characters.

            ### Papers:
            {blocks}"""
    }
}
