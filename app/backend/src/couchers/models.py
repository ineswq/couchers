import enum
from datetime import date
from calendar import monthrange
from math import floor

from sqlalchemy import (Boolean, Column, Date, DateTime, Enum, Float,
                        ForeignKey, Integer)
from sqlalchemy import LargeBinary as Binary
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

Base = declarative_base()

class PhoneStatus(enum.Enum):
    # unverified
    unverified = 1
    # verified
    verified = 2


class User(Base):
    """
    Basic user and profile details
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    # stored in libsodium hash format, can be null for email login
    hashed_password = Column(Binary, nullable=True)
    # phone number
    # TODO: should it be unique?
    phone = Column(String, nullable=True, unique=True)
    phone_status = Column(Enum(PhoneStatus), nullable=True)

    joined = Column(DateTime, nullable=False, server_default=func.now())
    last_active = Column(DateTime, nullable=False, server_default=func.now())

    # display name
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)

    # name as on official docs for verification, etc. not needed until verification
    full_name = Column(String, nullable=True)

    # verification score
    verification = Column(Float, nullable=True)
    # community standing score
    community_standing = Column(Float, nullable=True)

    occupation = Column(String, nullable=True)
    about_me = Column(String, nullable=True)
    about_place = Column(String, nullable=True)
    # profile color
    color = Column(String, nullable=False, default="#643073")
    # TODO: array types once we go postgres
    languages = Column(String, nullable=True)
    countries_visited = Column(String, nullable=True)
    countries_lived = Column(String, nullable=True)

    # TODO: hosting fields

    @property
    def age(self):
        max_day = monthrange(date.today().year, self.birthdate.month)[1]
        age = date.today().year - self.birthdate.year
        #in case of leap-day babies, make sure the date is valid for this year
        safe_birthdate = self.birthdate
        if (self.birthdate.day > max_day):
            safe_birthdate = safe_birthdate.replace(day = max_day)
        if date.today() < safe_birthdate.replace(year=date.today().year):
            age -= 1
        return age

    @property
    def display_joined(self):
        """
        Returns the last active time rounded down to the nearest hour.
        """
        return self.joined.replace(minute=0, second=0, microsecond=0)

    @property
    def display_last_active(self):
        """
        Returns the last active time rounded down to the nearest 15 minutes.
        """
        return self.last_active.replace(minute=(self.last_active.minute // 15) * 15,
                                        second=0, microsecond=0)

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, username={self.username})"


class FriendStatus(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3
    cancelled = 4


class FriendRelationship(Base):
    """
    Friendship relations between users

    TODO: make this better with sqlalchemy self-referential stuff
    """
    __tablename__ = "friend_relationships"

    id = Column(Integer, primary_key=True)

    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(Enum(FriendStatus), nullable=False, default=FriendStatus.pending)

    time_sent = Column(DateTime, nullable=False, server_default=func.now())
    time_responded = Column(DateTime, nullable=True)

    from_user = relationship("User", backref="friends_from", foreign_keys="FriendRelationship.from_user_id")
    to_user = relationship("User", backref="friends_to", foreign_keys="FriendRelationship.to_user_id")


class SignupToken(Base):
    """
    A signup token allows the user to verify their email and continue signing up.
    """
    __tablename__ = "signup_tokens"
    token = Column(String, primary_key=True)

    email = Column(String, nullable=False)

    created = Column(DateTime, nullable=False, server_default=func.now())
    expiry = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"SignupToken(token={self.token}, email={self.email}, created={self.created}, expiry={self.expiry})"


class LoginToken(Base):
    """
    A login token sent in an email to a user, allows them to sign in between the times defined by created and expiry
    """
    __tablename__ = "login_tokens"
    token = Column(String, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created = Column(DateTime, nullable=False, server_default=func.now())
    expiry = Column(DateTime, nullable=False)

    user = relationship("User", backref="login_tokens")

    def __repr__(self):
        return f"LoginToken(token={self.token}, user={self.user}, created={self.created}, expiry={self.expiry})"


class UserSession(Base):
    """
    Active session on the app, for auth
    """
    __tablename__ = "sessions"
    token = Column(String, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    started = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", backref="sessions")


class Reference(Base):
    """
    Reference from one user to another
    """
    __tablename__ = "references"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False, server_default=func.now())

    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    text = Column(String, nullable=True)

    rating = Column(Integer, nullable=False)
    was_safe = Column(Boolean, nullable=False)

    from_user = relationship("User", backref="references_from", foreign_keys="Reference.from_user_id")
    to_user = relationship("User", backref="references_to", foreign_keys="Reference.to_user_id")

class MessageThread(Base):
    """
    Message thread metadata
    """

    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True)
    creation_time = Column(DateTime, nullable=False, server_default=func.now())

    title = Column(String, nullable=True)
    only_admins_invite = Column(Boolean, nullable=False, default=True)
    creator_id = Column(ForeignKey("users.id"), nullable=False)
    is_dm = Column(Boolean, nullable=False)

    creator = relationship("User")

class MessageThreadRole(enum.Enum):
    admin = 1
    participant = 2

class ThreadSubscriptionStatus(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3

class MessageThreadSubscription(Base):
    """
    The recipient of a thread and information about when they joined/left/etc.
    """

    __tablename__ = "message_thread_subscriptions"

    user_id = Column(ForeignKey("users.id"), primary_key=True)
    thread_id = Column(ForeignKey("message_threads.id"), primary_key=True)

    role = Column(Enum(MessageThreadRole), nullable=False)
    status = Column(Enum(ThreadSubscriptionStatus), nullable=False)


    added_time = Column(DateTime, nullable=False, server_default=func.now())
    added_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    left_time = Column(DateTime, nullable=True)

    user = relationship("User", backref="message_thread_subscriptions", foreign_keys="MessageThreadSubscription.user_id")
    thread = relationship("MessageThread", backref="recipient_subscriptions")
    added_by = relationship("User", foreign_keys="MessageThreadSubscription.added_by_id")

class Message(Base):
    """
    Message content.
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    thread_id = Column(ForeignKey("message_threads.id"), nullable=False)
    author_id = Column(ForeignKey("users.id"), nullable=False)

    timestamp = Column(DateTime, nullable=False, server_default=func.now())

    text = Column(String, nullable=False)

    thread = relationship("MessageThread", backref="messages", order_by="Message.timestamp.desc()")
    author = relationship("User")
