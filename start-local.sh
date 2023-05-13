export DATABASE_URL="sqlite:///example.db"
export JWE_KEY="D9F8273A5B1C6E9D4F7A2B5C8E3F6A9D"
export JWT_KEY="A3B5D8E7C6F4A1B9D5E8C3A7B2F5D8E6"
export AUTH_EXP=30
uvicorn --factory zwallet.api:create_api --reload
