from fastapi import APIRouter

router = APIRouter(prefix="/.well-known", tags=["well-known", ".well-known", "authorization-server", "oauth-authorization-server"])

@router.get("/oauth-protected-resource", summary="Get metadata about server")
async def get_metadata():
    return {
        "resource": "https://tc-cgpt.onrender.com",
        "authorization_servers": [
        "https://accounts.zoho.in/oauth/v2/auth"
        ],
        "scopes_supported": ["TrainerCentral.sessionapi.ALL","TrainerCentral.sectionapi.ALL","TrainerCentral.courseapi.ALL","TrainerCentral.userapi.ALL","TrainerCentral.talkapi.ALL","TrainerCentral.portalapi.READ"],
        "resource_documentation": "https://tc-cgpt.onrender.com/docs",
    }

@router.get("/oauth-authorization-server", summary="Get necessary endpoints to authorize")
async def get_endpoints():
    return {
        "issuer": "https://tc-cgpt.onrender.com",
        "authorization_endpoint": "https://accounts.zoho.in/oauth/v2/auth",
        "token_endpoint": "https://accounts.zoho.in/oauth/v2/token",
        "registration_endpoint": "https://accounts.zoho.in/oauth/v2/register",
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["TrainerCentral.sessionapi.ALL","TrainerCentral.sectionapi.ALL","TrainerCentral.courseapi.ALL","TrainerCentral.userapi.ALL","TrainerCentral.talkapi.ALL","TrainerCentral.portalapi.READ"]
    }


@router.get("/openid-configuration", summary="Get necessary endpoints to authorize")
async def get_endpoints():
    return {
        "issuer": "https://tc-cgpt.onrender.com",
        "authorization_endpoint": "https://accounts.zoho.in/oauth/v2/auth",
        "token_endpoint": "https://accounts.zoho.in/oauth/v2/token",
        "registration_endpoint": "https://accounts.zoho.in/oauth/v2/register",
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["TrainerCentral.sessionapi.ALL","TrainerCentral.sectionapi.ALL","TrainerCentral.courseapi.ALL","TrainerCentral.userapi.ALL","TrainerCentral.talkapi.ALL","TrainerCentral.portalapi.READ"]
    }
