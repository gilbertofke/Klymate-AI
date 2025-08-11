"""
Base Repository Pattern Implementation

This module provides the base repository class that implements common
database operations following the Repository pattern for clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.exc import IntegrityError, NoResultFound
import logging
from datetime import datetime

from app.models.base import BaseModel

logger = logging.getLogger(__name__)

# Generic type for model classes
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType], ABC):
    """
    Base repository class implementing common CRUD operations.
    
    This class follows the Repository pattern to abstract database operations
    and provide a clean interface for data access.
    """
    
    def __init__(self, model: type[ModelType], db_session: AsyncSession):
        """
        Initialize repository with model class and database session.
        
        Args:
            model: SQLAlchemy model class
            db_session: Async database session
        """
        self.model = model
        self.db = db_session
    
    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Create a new record in the database.
        
        Args:
            obj_in: Pydantic schema or dictionary with creation data
            
        Returns:
            Created model instance
            
        Raises:
            IntegrityError: If unique constraints are violated
            ValueError: If required fields are missing
        """
        try:
            # Convert Pydantic model to dict if necessary
            if hasattr(obj_in, 'model_dump'):
                obj_data = obj_in.model_dump(exclude_unset=True)
            elif hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Create model instance
            db_obj = self.model(**obj_data)
            
            # Add to session and commit
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            
            logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
            return db_obj
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error creating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Data integrity violation: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    async def get_by_id(self, id: Any, load_relationships: bool = False) -> Optional[ModelType]:
        """
        Get a record by its ID.
        
        Args:
            id: Primary key value
            load_relationships: Whether to eagerly load relationships
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            query = select(self.model).where(self.model.id == id)
            
            # Add relationship loading if requested
            if load_relationships:
                query = self._add_relationship_loading(query)
            
            result = await self.db.execute(query)
            instance = result.scalar_one_or_none()
            
            if instance:
                logger.debug(f"Found {self.model.__name__} with id: {id}")
            else:
                logger.debug(f"No {self.model.__name__} found with id: {id}")
                
            return instance
            
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by id {id}: {str(e)}")
            raise
    
    async def get_by_field(
        self, 
        field_name: str, 
        field_value: Any,
        load_relationships: bool = False
    ) -> Optional[ModelType]:
        """
        Get a record by a specific field value.
        
        Args:
            field_name: Name of the field to search by
            field_value: Value to search for
            load_relationships: Whether to eagerly load relationships
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            field = getattr(self.model, field_name)
            query = select(self.model).where(field == field_value)
            
            if load_relationships:
                query = self._add_relationship_loading(query)
            
            result = await self.db.execute(query)
            instance = result.scalar_one_or_none()
            
            logger.debug(f"Found {self.model.__name__} by {field_name}: {field_value}")
            return instance
            
        except AttributeError:
            logger.error(f"Field {field_name} not found in {self.model.__name__}")
            raise ValueError(f"Invalid field name: {field_name}")
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by {field_name}: {str(e)}")
            raise
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        load_relationships: bool = False
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            order_by: Field name to order by
            load_relationships: Whether to eagerly load relationships
            
        Returns:
            List of model instances
        """
        try:
            query = select(self.model)
            
            # Apply filters
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        if isinstance(field_value, list):
                            query = query.where(field.in_(field_value))
                        else:
                            query = query.where(field == field_value)
            
            # Apply ordering
            if order_by:
                if hasattr(self.model, order_by):
                    order_field = getattr(self.model, order_by)
                    query = query.order_by(order_field)
                else:
                    query = query.order_by(self.model.created_at.desc())
            else:
                query = query.order_by(self.model.created_at.desc())
            
            # Add relationship loading
            if load_relationships:
                query = self._add_relationship_loading(query)
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            instances = result.scalars().all()
            
            logger.debug(f"Retrieved {len(instances)} {self.model.__name__} records")
            return list(instances)
            
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {str(e)}")
            raise
    
    async def update(
        self, 
        id: Any, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Update a record by ID.
        
        Args:
            id: Primary key value
            obj_in: Pydantic schema or dictionary with update data
            
        Returns:
            Updated model instance if found, None otherwise
        """
        try:
            # Get existing record
            db_obj = await self.get_by_id(id)
            if not db_obj:
                logger.warning(f"No {self.model.__name__} found with id: {id}")
                return None
            
            # Convert update data to dict
            if hasattr(obj_in, 'model_dump'):
                update_data = obj_in.model_dump(exclude_unset=True)
            elif hasattr(obj_in, 'dict'):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            # Update timestamp
            if hasattr(db_obj, 'updated_at'):
                db_obj.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with id: {id}")
            return db_obj
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error updating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Data integrity violation: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise
    
    async def delete(self, id: Any) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Check if record exists
            db_obj = await self.get_by_id(id)
            if not db_obj:
                logger.warning(f"No {self.model.__name__} found with id: {id}")
                return False
            
            # Soft delete if supported
            if hasattr(db_obj, 'soft_delete'):
                db_obj.soft_delete()
                await self.db.commit()
                logger.info(f"Soft deleted {self.model.__name__} with id: {id}")
            else:
                # Hard delete
                await self.db.delete(db_obj)
                await self.db.commit()
                logger.info(f"Hard deleted {self.model.__name__} with id: {id}")
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Number of matching records
        """
        try:
            query = select(func.count(self.model.id))
            
            # Apply filters
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        query = query.where(field == field_value)
            
            result = await self.db.execute(query)
            count = result.scalar()
            
            logger.debug(f"Counted {count} {self.model.__name__} records")
            return count
            
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise
    
    async def exists(self, id: Any) -> bool:
        """
        Check if a record exists by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            True if exists, False otherwise
        """
        try:
            query = select(func.count(self.model.id)).where(self.model.id == id)
            result = await self.db.execute(query)
            count = result.scalar()
            
            exists = count > 0
            logger.debug(f"{self.model.__name__} with id {id} exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {str(e)}")
            raise
    
    def _add_relationship_loading(self, query):
        """
        Add relationship loading to query.
        Override in subclasses to specify relationships to load.
        
        Args:
            query: SQLAlchemy query object
            
        Returns:
            Query with relationship loading options
        """
        return query
    
    async def bulk_create(self, objects: List[Union[CreateSchemaType, Dict[str, Any]]]) -> List[ModelType]:
        """
        Create multiple records in a single transaction.
        
        Args:
            objects: List of creation data
            
        Returns:
            List of created model instances
        """
        try:
            db_objects = []
            
            for obj_in in objects:
                # Convert to dict if necessary
                if hasattr(obj_in, 'model_dump'):
                    obj_data = obj_in.model_dump(exclude_unset=True)
                elif hasattr(obj_in, 'dict'):
                    obj_data = obj_in.dict(exclude_unset=True)
                else:
                    obj_data = obj_in
                
                db_obj = self.model(**obj_data)
                db_objects.append(db_obj)
            
            # Add all objects to session
            self.db.add_all(db_objects)
            await self.db.commit()
            
            # Refresh all objects
            for db_obj in db_objects:
                await self.db.refresh(db_obj)
            
            logger.info(f"Bulk created {len(db_objects)} {self.model.__name__} records")
            return db_objects
            
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error in bulk create {self.model.__name__}: {str(e)}")
            raise ValueError(f"Data integrity violation: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk create {self.model.__name__}: {str(e)}")
            raise