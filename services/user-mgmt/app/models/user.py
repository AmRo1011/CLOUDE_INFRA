"""
User database models
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    __table_args__ = {"schema": "user_mgmt"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = "roles"
    __table_args__ = {"schema": "user_mgmt"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary="user_mgmt.role_permissions", back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    """Permission model for RBAC"""
    __tablename__ = "permissions"
    __table_args__ = {"schema": "user_mgmt"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary="user_mgmt.role_permissions", back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission {self.name}>"


class RolePermission(Base):
    """Association table for Role-Permission many-to-many"""
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "user_mgmt"}
    
    role_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.permissions.id", ondelete="CASCADE"), primary_key=True)


class UserSession(Base):
    """User session model for token management"""
    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "user_mgmt"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_mgmt.users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession {self.id}>"

