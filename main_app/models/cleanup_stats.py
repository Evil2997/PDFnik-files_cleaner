from pydantic import BaseModel


class CleanupStats(BaseModel):
    scanned: int = 0
    deleted: int = 0
    errors: int = 0
