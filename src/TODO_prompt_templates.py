# app/prompt_templates.py

BASE_BULK_TEMPLATE = """
You are a science and technology analyst summarizing the most recent {content_type} in **{subject_area}**.

---

### Your Tasks


---

### Top Sources
List the most impactful or interesting sources using the exact format below. Include only {top_entries} sources.

Format (strictly follow this line structure — one per item):

`Title` - `Link` - `One-line summary`

Example:

Top Sources:
1. Example Breakthrough - https://example.com/item1 - One-sentence description.
2. Example Discovery - https://example.com/item2 - Another concise highlight.

---

### Output Constraints


---

### {content_type}:
{blocks}
"""

BASE_ENTRY_TEMPLATE = """
You are a science writer summarizing the following {content_type} in the field of **{subject_area}**.

---

### Instructions


---

### Source
**Title:** {title}  
**Summary Text:** {summary}  
**Link:** {link}

---

### Output Format
Write in clear, engaging prose with one short paragraph ({summary_length} characters).  
"""

SYSTEM_PROMPT_TEMPLATE = """
You are a science writer producing summaries about **{subject_area}**. 
Your audience is: {audience_description}. Write clearly and engagingly.
"""