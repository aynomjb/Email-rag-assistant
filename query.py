from helpers.query_by_thread import (
    ask_email_agent,
    ask_email_agent2
)
result = ask_email_agent2("who was invited to the kickoff meeting?", "emails4")
print(result)