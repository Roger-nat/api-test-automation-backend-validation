from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, projects, results, testcases, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="QA Test Management API",
    version="1.0.0",
    description="REST API used to demonstrate automated API testing and backend validation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(testcases.router)
app.include_router(results.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "qa-test-management-api"}
