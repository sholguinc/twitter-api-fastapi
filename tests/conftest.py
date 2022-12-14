# Signal
import signal
from .overtime_signal import TimeOutException, TIMEOUT

# Testing
import pytest
from fastapi.testclient import TestClient

# Database
from models import UserRegister
from tests.test_sql_app import override_get_db, mysql_test_engine
from sql_app.dependencies import get_db
from sql_app.database import Base

# Others Tools
from sql_app import crud

# App
from main import app

# Define User
user_example = UserRegister(
    first_name="UserTest1",
    last_name="SomeLastName",
    email="usertest1@example.com",
    password="thisisthetestpassword",
    country="Peru",
    birth_date="2001-01-01",
    creation_account_date="2022-01-01"
)

user_another_example = UserRegister(
    first_name="UserTest2",
    last_name="SomeLastName",
    email="usertest2@example.com",
    password="thisisthetestpassword",
    country="Peru",
    birth_date="2011-01-01",
    creation_account_date="2022-02-02"
)

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Fixtures
@pytest.fixture
def set_db():
    try:
        Base.metadata.create_all(bind=mysql_test_engine)

        # Signal that cancel test if last more than 5 second
        signal.alarm(TIMEOUT)

        yield

    except Exception:
        raise TimeOutException('Database Error!')
    finally:
        Base.metadata.drop_all(bind=mysql_test_engine)


@pytest.fixture(autouse=True)
def set_up_users(set_db):
    """Fixture to create test users."""

    # Define User
    test_user_1 = user_example
    test_user_2 = user_another_example

    # Open DB Session
    test_database = next(override_get_db())

    # Add user to database
    db_user_1 = crud.create_user_if_not_exist(test_database, test_user_1)
    db_user_2 = crud.create_user_if_not_exist(test_database, test_user_2)

    # Login Users
    response_user_1 = client.post(
        "/login",
        data={"username": db_user_1.email, "password": user_example.password}
    )
    response_user_2 = client.post(
        "/login",
        data={"username": db_user_2.email, "password": user_another_example.password}
    )

    # Header
    header_user_1 = {"Authorization": "Bearer " + response_user_1.json()["access_token"]}
    header_user_2 = {"Authorization": "Bearer " + response_user_2.json()["access_token"]}

    # Information to yield
    set_up_info = {
        "user_1": db_user_1,
        "header_1": header_user_1,
        "user_2": db_user_2,
        "header_2": header_user_2,
    }

    # Here is where the testing happens
    yield set_up_info

    # Delete user from database
    crud.delete_user_if_exists(test_database, db_user_1.user_id)
    # crud.delete_user_if_exists(test_database, db_user_2.user_id)


@pytest.fixture()
def set_up_tweets(set_up_users):
    """Fixture to create test tweets"""

    # Open DB Session
    test_database = next(override_get_db())

    # Function to make tweets
    def make_tweets_from_user(user_number):
        user_info = set_up_users[f'user_{user_number}']
        header = set_up_users[f'header_{user_number}']

        # Post Tweets
        response_tweet_1 = client.post(
            "/post",
            json={"content": f'First Test Tweet Text from User_{user_number}, provisional name.'},
            headers=header
        )
        response_tweet_2 = client.post(
            "/post",
            json={"content": f'Second Test Tweet Text from User_{user_number}, provisional name.'},
            headers=header
        )

        return {
            "user_info": user_info,
            "header": header,
            "tweet_1": response_tweet_1.json(),
            "tweet_2": response_tweet_2.json()
        }

    # Information to yield
    set_up_tweet_info = {
        "user_1": make_tweets_from_user(1),
        "user_2": make_tweets_from_user(2)
    }

    # Here is where the testing happens
    yield set_up_tweet_info

    # Delete tweets from database
    crud.delete_tweets_by_user(test_database, set_up_tweet_info["user_1"]["user_info"].user_id)
    crud.delete_tweets_by_user(test_database, set_up_tweet_info["user_2"]["user_info"].user_id)
