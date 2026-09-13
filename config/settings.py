from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    #APPLICATION
    app_name:str="Agentic_SDLC"
    app_env:str="development"
    log_level:str="INFO"
    #LLM
    openai_API_Key:str=""
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
    #FIGMA MCP
    figma_mcp_url:str="https://mcp.figma.com/mcp"
    figma_team_plan_key:str=""
    figma_token_storage_path:str=".figma_mcp_tokens.json"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
settings=Settings()
