from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    #APPLICATION
    app_name:str="Agentic_SDLC"
    app_env:str="development"
    log_level:str="INFO"
    #LLM
    openai_API_Key:str=""
    gemini_api_key:str=""
    #SLACK
    slack_bot_token:str=""
    slack_app_token:str=""
    slack_signing_secret:str=""
    #AWS
    AWS_REGION:str="ap-south-1"
    #RAG/VECTOR DATABASE
    qdrant_url:str=""
    qdrant_api_key:str=""
    #JIRA
    jira_base_url:str=""
    jira_email:str=""
    jira_api_token:str=""
    jira_project_key:str=""
    #JIRA ASSIGNEES (per-work-type default assignee accountId; see ai_agents/jira/assignee_resolver.py)
    jira_assignee_design:str=""
    jira_assignee_frontend:str=""
    jira_assignee_backend:str=""
    jira_assignee_integration:str=""
    jira_assignee_qa:str=""
    jira_assignee_devops:str=""
    #FIGMA JOB SERVICE (plugin <-> FastAPI shared secret; see integrations/figma/)
    figma_plugin_api_token:str=""
    figma_job_service_port:int=8787
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
settings=Settings()
