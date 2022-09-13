# Python
import json
from datetime import datetime
from typing import List
from uuid import uuid4

# FastAPI
from fastapi import APIRouter
from fastapi import status, HTTPException
from fastapi import Path, Body

# Models
from models import Tweet, NewTweet, TweetDeleted, UpdateTweet

# Tags
from .tags import Tags

# Examples
from examples import TweetExamples


router = APIRouter(tags=[Tags.tweets])


# Tweets Path Operations

## Show all tweets
@router.get(
    path="/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets"
)
def home():
    """
    Home

    This path operation show all tweets in the app

    No-Parameters

    Returns a json list with all tweets in the app with the following keys:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_at: Optional[datetime]
    - by: User
    """

    with open("tweets.json", "r", encoding="utf-8") as f:
        content = f.read()
        results = json.loads(content)

        return results


## Post a tweet
@router.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary='Post a tweet'
)
def post_tweet(tweet: NewTweet = Body(..., examples=TweetExamples.tweet_info)):
    """
    Post Tweet

    This path operation post a tweet in the app

    Parameters:
    - Request Body parameters:
        - **tweet: NewTweet**

    Returns a json with the basic tweet information:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_at: Optional[datetime]
    - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        # Reading tweets.json and convert it to a dict
        content = f.read()
        tweets = json.loads(content)

        # Receive new tweet
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(uuid4())
        tweet_dict["created_at"] = str(tweet_dict["created_at"])

        if tweet_dict["updated_at"]:
            tweet_dict["updated_at"] = str(tweet_dict["updated_at"])

        user_id = tweet_dict["by"]

        with open("users.json", "r", encoding="utf-8") as file:
            users = json.loads(file.read())
            searched_user = [user for user in users if user["user_id"] == user_id][0]
            tweet_dict["by"] = searched_user

        # Add new tweet to tweets.json
        tweets.append(tweet_dict)

        # Move to the first line of the file
        f.seek(0)

        # Writing the new tweet list
        json_tweet_list = json.dumps(tweets)
        f.write(json_tweet_list)
        f.truncate()

        return tweet_dict


## Show a tweet
@router.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary='Show a specific tweet'
)
def show_tweet(
        tweet_id: str = Path(
            ...,
            min_length=36,
            max_length=36,
            title="Tweet ID",
            description="This is UUID4 that identifies a tweet.",
            examples=TweetExamples.tweet_id
        )
):
    """
    Show Tweet

    This path operation show a specific tweet in the app

    Parameters:
    - Path Parameters:
        - **tweet_id: str**

    Returns a json list with the tweet info with the following keys:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_at: Optional[datetime]
    - by: User
    """

    with open("tweets.json", "r", encoding="utf-8") as f:
        content = f.read()
        tweets = json.loads(content)
        searched_tweet = [tweet for tweet in tweets if tweet["tweet_id"] == tweet_id][0]

        return searched_tweet


## Delete a tweet
@router.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=TweetDeleted,
    status_code=status.HTTP_200_OK,
    summary='Delete a specific tweet'
)
def delete_tweet(
        tweet_id: str = Path(
            ...,
            min_length=36,
            max_length=36,
            title="Tweet ID",
            description="This is UUID4 that identifies a tweet.",
            examples=TweetExamples.tweet_id
        )
):
    """
    Delete Tweet

    This path operation delete a specific tweet in the app

    Parameters:
    - Path Parameters:
        - **tweet_id: str**

    Returns a json list with the tweet info with the following keys:
    - tweet_id: UUID
    - delete_message: str
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        content = f.read()
        tweets = json.loads(content)

        try:
            # Searched tweet
            searched_tweet = [tweet for tweet in tweets if tweet["tweet_id"] == tweet_id][0]

            # Response
            response = {
                "tweet_id": searched_tweet["tweet_id"],
                "delete_message": f'Tweet written by {searched_tweet["by"]["first_name"]} has been deleted!'
            }

            # Remove the specific tweet
            tweets.remove(searched_tweet)

            # Move to the first line of the file
            f.seek(0)

            # Writing the new user list
            json_tweet_list = json.dumps(tweets)
            f.write(json_tweet_list)
            f.truncate()

            return response

        except IndexError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This tweet doesn't exist!"
            )


## Update a tweet
@router.put(
    path="/tweets/{tweet_id}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary='Update a specific tweet'
)
def update_tweet(
        tweet_id: str = Path(
            ...,
            min_length=36,
            max_length=36,
            title="Tweet ID",
            description="This is UUID4 that identifies a tweet.",
            examples=TweetExamples.tweet_id
        ),
        new_tweet_info: UpdateTweet = Body(..., examples=TweetExamples.tweet_updates)
):
    """
    Update Tweet

    This path operation update a specific tweet in the app

    Parameters:
    - Path Parameters:
        - **tweet_id: str**

    - Request Body parameters:
        - **new_tweet_info: UpdateTweet**

    Returns a json with the basic tweet information:
    - tweet_id: UUID
    - content: str
    - created_at: datetime
    - updated_at: datetime
    - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        content = f.read()
        tweets = json.loads(content)

        try:
            # Searched tweet
            searched_tweet = [tweet for tweet in tweets if tweet["tweet_id"] == tweet_id][0]

            # New Tweet info
            updated_tweet = new_tweet_info.dict()
            updated_tweet["tweet_id"] = searched_tweet["tweet_id"]
            updated_tweet["created_at"] = searched_tweet["created_at"]
            updated_tweet["updated_at"] = str(datetime.now())
            updated_tweet["by"] = searched_tweet["by"]

            # Replace tweet
            index = tweets.index(searched_tweet)
            tweets[index] = updated_tweet

            # Move to the first line of the file
            f.seek(0)

            # Writing the new user list
            json_tweet_list = json.dumps(tweets)
            f.write(json_tweet_list)
            f.truncate()

            return updated_tweet

        except IndexError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This tweet doesn't exist!"
            )
