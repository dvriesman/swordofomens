# swordofomens
Sword of Omens, give me sight beyond sight! A way to talk to Jira tickets (Gemini based)

# Setup
```python3 -m venv ./```
```pip install -r requirements.txt```

# Enviroments

You need to provide some environment variables, create and .env file is an option.

```
export GOOGLE_API_KEY="your google gemini api key, get in google ai studio"
export JIRA_USER="user@domain"
export JIRA_PASSWORD="your generated jira token"
export JIRA_BASE_URL="https://yourcompany.atlassian.net"
```

# Run
```streamlit run webmain.py```
