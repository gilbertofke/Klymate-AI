import pytest
from fastapi.testclient import TestClient
from app.core.middleware import LoggingMiddleware
from fastapi import FastAPI

def test_logging_middleware():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 200
    assert response.json() == {"message": "test"}
