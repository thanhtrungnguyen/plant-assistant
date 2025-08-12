from authlib.integrations.starlette_client import OAuth  # type: ignore

from src.core.config import settings

oauth = OAuth()
oauth.register(  # type: ignore
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
