"""
User Repository Implementation

This module provides the UserRepository class that handles all database
operations related to User entities, extending the base repository pattern.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime, timedelta

from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for User entity operations.
    
    Extends BaseRepository to provide user-specific database operations
    including authentication, profile management, and analytics.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize UserRepository with User model."""
        super().__init__(User, db_session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            query = select(User).where(User.email == email.lower())
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                logger.debug(f"Found user by email: {email}")
            else:
                logger.debug(f"No user found with email: {email}")
                
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise
    
    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """
        Get user by Firebase UID.
        
        Args:
            firebase_uid: Firebase user identifier
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            query = select(User).where(User.firebase_uid == firebase_uid)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                logger.debug(f"Found user by Firebase UID: {firebase_uid}")
            else:
                logger.debug(f"No user found with Firebase UID: {firebase_uid}")
                
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by Firebase UID {firebase_uid}: {str(e)}")
            raise
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with proper validation and defaults.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created User instance
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        try:
            # Check if email already exists
            existing_user = await self.get_by_email(user_data.email)
            if existing_user:
                raise ValueError(f"User with email {user_data.email} already exists")
            
            # Check if Firebase UID already exists (if provided)
            if user_data.firebase_uid:
                existing_firebase_user = await self.get_by_firebase_uid(user_data.firebase_uid)
                if existing_firebase_user:
                    raise ValueError(f"User with Firebase UID {user_data.firebase_uid} already exists")
            
            # Normalize email
            user_dict = user_data.model_dump(exclude_unset=True)
            user_dict['email'] = user_dict['email'].lower()
            
            # Set default values
            user_dict.setdefault('is_active', True)
            user_dict.setdefault('is_verified', False)
            user_dict.setdefault('onboarding_completed', False)
            user_dict.setdefault('login_count', 0)
            
            # Create user
            user = await self.create(user_dict)
            
            logger.info(f"Created new user: {user.email} (ID: {user.id})")
            return user
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def update_login_info(self, user_id: int) -> Optional[User]:
        """
        Update user's login information (last login time and count).
        
        Args:
            user_id: User's ID
            
        Returns:
            Updated User instance if found, None otherwise
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            user.update_login_info()
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated login info for user {user_id}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating login info for user {user_id}: {str(e)}")
            raise
    
    async def complete_onboarding(self, user_id: int, onboarding_data: Dict[str, Any]) -> Optional[User]:
        """
        Mark user onboarding as completed and store onboarding data.
        
        Args:
            user_id: User's ID
            onboarding_data: Dictionary containing onboarding survey responses
            
        Returns:
            Updated User instance if found, None otherwise
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            # Store onboarding data as JSON
            import json
            user.preferences = json.dumps(onboarding_data)
            user.complete_onboarding()
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Completed onboarding for user {user_id}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error completing onboarding for user {user_id}: {str(e)}")
            raise
    
    async def update_baseline_footprint(self, user_id: int, baseline_footprint: float) -> Optional[User]:
        """
        Update user's baseline carbon footprint.
        
        Args:
            user_id: User's ID
            baseline_footprint: Calculated baseline carbon footprint in kg CO2/year
            
        Returns:
            Updated User instance if found, None otherwise
        """
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            user.baseline_footprint = baseline_footprint
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Updated baseline footprint for user {user_id}: {baseline_footprint} kg CO2/year")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating baseline footprint for user {user_id}: {str(e)}")
            raise
    
    async def get_active_users(self, limit: int = 100) -> List[User]:
        """
        Get list of active users.
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of active User instances
        """
        try:
            query = (
                select(User)
                .where(and_(User.is_active == True, User.is_deleted == False))
                .order_by(desc(User.last_login_at))
                .limit(limit)
            )
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            logger.debug(f"Retrieved {len(users)} active users")
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting active users: {str(e)}")
            raise
    
    async def get_users_by_location(self, location: str, limit: int = 100) -> List[User]:
        """
        Get users by location for regional analytics.
        
        Args:
            location: Location string to search for
            limit: Maximum number of users to return
            
        Returns:
            List of User instances in the specified location
        """
        try:
            query = (
                select(User)
                .where(and_(
                    User.location.ilike(f"%{location}%"),
                    User.is_active == True,
                    User.is_deleted == False
                ))
                .order_by(desc(User.created_at))
                .limit(limit)
            )
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            logger.debug(f"Retrieved {len(users)} users in location: {location}")
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting users by location {location}: {str(e)}")
            raise
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get overall user statistics for analytics.
        
        Returns:
            Dictionary containing user statistics
        """
        try:
            # Total users
            total_users_query = select(func.count(User.id)).where(User.is_deleted == False)
            total_users_result = await self.db.execute(total_users_query)
            total_users = total_users_result.scalar()
            
            # Active users
            active_users_query = select(func.count(User.id)).where(
                and_(User.is_active == True, User.is_deleted == False)
            )
            active_users_result = await self.db.execute(active_users_query)
            active_users = active_users_result.scalar()
            
            # Verified users
            verified_users_query = select(func.count(User.id)).where(
                and_(User.is_verified == True, User.is_deleted == False)
            )
            verified_users_result = await self.db.execute(verified_users_query)
            verified_users = verified_users_result.scalar()
            
            # Users who completed onboarding
            onboarded_users_query = select(func.count(User.id)).where(
                and_(User.onboarding_completed == True, User.is_deleted == False)
            )
            onboarded_users_result = await self.db.execute(onboarded_users_query)
            onboarded_users = onboarded_users_result.scalar()
            
            # New users in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            new_users_query = select(func.count(User.id)).where(
                and_(
                    User.created_at >= thirty_days_ago,
                    User.is_deleted == False
                )
            )
            new_users_result = await self.db.execute(new_users_query)
            new_users_30d = new_users_result.scalar()
            
            # Average baseline footprint
            avg_footprint_query = select(func.avg(User.baseline_footprint)).where(
                and_(
                    User.baseline_footprint.isnot(None),
                    User.is_deleted == False
                )
            )
            avg_footprint_result = await self.db.execute(avg_footprint_query)
            avg_baseline_footprint = avg_footprint_result.scalar()
            
            statistics = {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "onboarded_users": onboarded_users,
                "new_users_30d": new_users_30d,
                "avg_baseline_footprint": float(avg_baseline_footprint) if avg_baseline_footprint else None,
                "onboarding_completion_rate": (onboarded_users / total_users * 100) if total_users > 0 else 0,
                "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
            }
            
            logger.debug("Retrieved user statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise
    
    async def search_users(
        self, 
        query: str, 
        limit: int = 50,
        include_inactive: bool = False
    ) -> List[User]:
        """
        Search users by name, email, or display name.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            include_inactive: Whether to include inactive users
            
        Returns:
            List of matching User instances
        """
        try:
            search_term = f"%{query.lower()}%"
            
            conditions = [
                User.name.ilike(search_term),
                User.display_name.ilike(search_term),
                User.email.ilike(search_term)
            ]
            
            if not include_inactive:
                conditions.append(User.is_active == True)
            
            conditions.append(User.is_deleted == False)
            
            search_query = (
                select(User)
                .where(and_(*conditions))
                .order_by(desc(User.last_login_at))
                .limit(limit)
            )
            
            result = await self.db.execute(search_query)
            users = result.scalars().all()
            
            logger.debug(f"Found {len(users)} users matching query: {query}")
            return list(users)
            
        except Exception as e:
            logger.error(f"Error searching users with query {query}: {str(e)}")
            raise
    
    async def get_users_needing_onboarding(self, limit: int = 100) -> List[User]:
        """
        Get users who haven't completed onboarding.
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of User instances who need to complete onboarding
        """
        try:
            query = (
                select(User)
                .where(and_(
                    User.onboarding_completed == False,
                    User.is_active == True,
                    User.is_deleted == False
                ))
                .order_by(User.created_at)
                .limit(limit)
            )
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            logger.debug(f"Found {len(users)} users needing onboarding")
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting users needing onboarding: {str(e)}")
            raise