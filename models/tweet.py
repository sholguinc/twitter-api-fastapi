# Python
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

# Pydantic
from pydantic import BaseModel, Field

# User
from models import User


class TweetBase(BaseModel):
    content: str = Field(..., min_length=0, max_length=280)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())
    by: User = Field(...)


class NewTweet(TweetBase):
    by: str = Field(..., min_length=36, max_length=36)


class Tweet(TweetBase):
    tweet_id: UUID = Field(default_factory=uuid4)

