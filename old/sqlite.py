"""
Database models and operations for SMS Gateway application
"""
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session, joinedload
import json

# Database setup with SQLite fallback
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Use PostgreSQL if DATABASE_URL is available
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    engine = create_engine(DATABASE_URL)
    print("Using PostgreSQL database")
else:
    # Fall back to SQLite for local development
    DATABASE_URL = 'sqlite:///./sms_gateway.db'
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("Using SQLite database for local development")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Contact(Base):
    """Contact model for storing phone contacts"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, index=True, unique=True)
    email = Column(String(255))
    group_id = Column(Integer, ForeignKey("contact_groups.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group = relationship("ContactGroup", back_populates="contacts")
    sms_messages = relationship("SMSMessage", back_populates="contact")

class ContactGroup(Base):
    """Contact group model for organizing contacts"""
    __tablename__ = "contact_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contacts = relationship("Contact", back_populates="group")

class SMSTemplate(Base):
    """SMS template model for storing reusable messages"""
    __tablename__ = "sms_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usage_count = Column(Integer, default=0)

class SMSMessage(Base):
    """SMS message history model"""
    __tablename__ = "sms_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_phone = Column(String(20), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    message_content = Column(Text, nullable=False)
    message_type = Column(String(20), default='regular')  # 'regular', 'flash', 'bulk'
    status = Column(String(20), default='pending')  # 'pending', 'sent', 'failed', 'retry'
    sent_at = Column(DateTime)
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    sms_parts = Column(Integer, default=1)
    
    # Relationships
    contact = relationship("Contact", back_populates="sms_messages")

class DeliveryReport(Base):
    """Delivery report model for tracking SMS delivery status"""
    __tablename__ = "delivery_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("sms_messages.id"))
    delivery_status = Column(String(20))  # 'delivered', 'failed', 'pending'
    delivery_time = Column(DateTime)
    error_code = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

# Database operations class
class DatabaseManager:
    """Database manager for SMS Gateway operations"""
    
    def __init__(self):
        self.engine = engine
        # Create all tables
        Base.metadata.create_all(bind=engine)
        # Create default groups if they don't exist
        self._create_default_groups()
    
    def _create_default_groups(self):
        """Create default contact groups if they don't exist"""
        session = self.get_session()
        try:
            default_groups = [
                ("Family", "Family members"),
                ("Friends", "Close friends"),
                ("Work", "Work colleagues and business contacts"),
                ("Clients", "Business clients"),
                ("Other", "Other contacts")
            ]
            
            for name, description in default_groups:
                existing = session.query(ContactGroup).filter(ContactGroup.name == name).first()
                if not existing:
                    session.add(ContactGroup(name=name, description=description))
            
            session.commit()
        except Exception as e:
            print(f"Error creating default groups: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_session(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    # Contact operations
    def create_contact(self, name: str, phone: str, email: str = "", group_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new contact"""
        session = self.get_session()
        try:
            contact = Contact(name=name, phone=phone, email=email, group_id=group_id)
            session.add(contact)
            session.commit()
            session.refresh(contact)
            
            return {
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
                'email': contact.email,
                'group_id': contact.group_id,
                'created_at': contact.created_at
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_contacts(self, group_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all contacts, optionally filtered by group"""
        session = self.get_session()
        try:
            query = session.query(Contact)
            if group_id:
                query = query.filter(Contact.group_id == group_id)
            contacts = query.all()
            
            result = []
            for contact in contacts:
                result.append({
                    'id': contact.id,
                    'name': contact.name,
                    'phone': contact.phone,
                    'email': contact.email,
                    'group_id': contact.group_id,
                    'created_at': contact.created_at,
                    'updated_at': contact.updated_at
                })
            return result
        finally:
            session.close()
    
    def update_contact(self, contact_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a contact"""
        session = self.get_session()
        try:
            contact = session.query(Contact).filter(Contact.id == contact_id).first()
            if contact:
                for key, value in kwargs.items():
                    if hasattr(contact, key):
                        setattr(contact, key, value)
                setattr(contact, 'updated_at', datetime.utcnow())
                session.commit()
                session.refresh(contact)
                
                return {
                    'id': contact.id,
                    'name': contact.name,
                    'phone': contact.phone,
                    'email': contact.email,
                    'group_id': contact.group_id,
                    'created_at': contact.created_at,
                    'updated_at': contact.updated_at
                }
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact"""
        session = self.get_session()
        try:
            contact = session.query(Contact).filter(Contact.id == contact_id).first()
            if contact:
                session.delete(contact)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Contact group operations
    def create_contact_group(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new contact group"""
        session = self.get_session()
        try:
            group = ContactGroup(name=name, description=description)
            session.add(group)
            session.commit()
            session.refresh(group)
            
            return {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'created_at': group.created_at
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_contact_groups(self) -> List[Dict[str, Any]]:
        """Get all contact groups"""
        session = self.get_session()
        try:
            groups = session.query(ContactGroup).all()
            
            result = []
            for group in groups:
                result.append({
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'created_at': group.created_at
                })
            return result
        finally:
            session.close()
    
    # SMS Template operations
    def create_sms_template(self, name: str, content: str, description: str = "") -> Dict[str, Any]:
        """Create a new SMS template"""
        session = self.get_session()
        try:
            template = SMSTemplate(name=name, content=content, description=description)
            session.add(template)
            session.commit()
            session.refresh(template)
            
            return {
                'id': template.id,
                'name': template.name,
                'content': template.content,
                'description': template.description,
                'usage_count': template.usage_count,
                'created_at': template.created_at
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_sms_templates(self) -> List[Dict[str, Any]]:
        """Get all SMS templates"""
        session = self.get_session()
        try:
            templates = session.query(SMSTemplate).order_by(SMSTemplate.usage_count.desc()).all()
            
            result = []
            for template in templates:
                result.append({
                    'id': template.id,
                    'name': template.name,
                    'content': template.content,
                    'description': template.description,
                    'usage_count': template.usage_count,
                    'created_at': template.created_at,
                    'updated_at': template.updated_at
                })
            return result
        finally:
            session.close()
    
    def use_sms_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Increment usage count for a template"""
        session = self.get_session()
        try:
            template = session.query(SMSTemplate).filter(SMSTemplate.id == template_id).first()
            if template:
                template.usage_count += 1
                session.commit()
                session.refresh(template)
                
                return {
                    'id': template.id,
                    'name': template.name,
                    'content': template.content,
                    'usage_count': template.usage_count
                }
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # SMS Message operations
    def log_sms_message(self, recipient_phone: str, message_content: str, 
                       message_type: str = 'regular', contact_id: Optional[int] = None,
                       scheduled_at: Optional[datetime] = None, sms_parts: int = 1) -> Dict[str, Any]:
        """Log an SMS message"""
        session = self.get_session()
        try:
            message = SMSMessage(
                recipient_phone=recipient_phone,
                contact_id=contact_id,
                message_content=message_content,
                message_type=message_type,
                scheduled_at=scheduled_at,
                sms_parts=sms_parts
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            
            return {
                'id': message.id,
                'recipient_phone': message.recipient_phone,
                'contact_id': message.contact_id,
                'message_content': message.message_content,
                'message_type': message.message_type,
                'scheduled_at': message.scheduled_at,
                'sms_parts': message.sms_parts,
                'status': message.status,
                'created_at': message.created_at
            }
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_message_status(self, message_id: int, status: str, 
                            error_message: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update SMS message status"""
        session = self.get_session()
        try:
            message = session.query(SMSMessage).filter(SMSMessage.id == message_id).first()
            if message:
                message.status = status
                if status == 'sent':
                    message.sent_at = datetime.utcnow()
                if error_message:
                    message.error_message = error_message
                if status == 'retry':
                    message.retry_count += 1
                
                session.commit()
                session.refresh(message)
                
                return {
                    'id': message.id,
                    'status': message.status,
                    'sent_at': message.sent_at,
                    'error_message': message.error_message,
                    'retry_count': message.retry_count
                }
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_sms_history(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get SMS message history with eager loading"""
        session = self.get_session()
        try:
            query = session.query(SMSMessage).options(
                joinedload(SMSMessage.contact)
            )
            if status:
                query = query.filter(SMSMessage.status == status)
            messages = query.order_by(SMSMessage.created_at.desc()).limit(limit).all()
            
            result = []
            for msg in messages:
                result.append({
                    'id': msg.id,
                    'recipient_phone': msg.recipient_phone,
                    'contact_id': msg.contact_id,
                    'contact_name': msg.contact.name if msg.contact else None,
                    'message_content': msg.message_content,
                    'message_type': msg.message_type,
                    'status': msg.status,
                    'sent_at': msg.sent_at,
                    'scheduled_at': msg.scheduled_at,
                    'created_at': msg.created_at,
                    'error_message': msg.error_message,
                    'retry_count': msg.retry_count,
                    'sms_parts': msg.sms_parts
                })
            return result
        finally:
            session.close()
    
    def get_sms_statistics(self) -> Dict[str, Any]:
        """Get SMS statistics"""
        session = self.get_session()
        try:
            total_messages = session.query(SMSMessage).count()
            sent_messages = session.query(SMSMessage).filter(SMSMessage.status == 'sent').count()
            failed_messages = session.query(SMSMessage).filter(SMSMessage.status == 'failed').count()
            pending_messages = session.query(SMSMessage).filter(SMSMessage.status == 'pending').count()
            
            # Calculate today's stats
            today = datetime.utcnow().date()
            today_messages = session.query(SMSMessage).filter(
                SMSMessage.created_at >= today
            ).count()
            today_sent = session.query(SMSMessage).filter(
                SMSMessage.created_at >= today,
                SMSMessage.status == 'sent'
            ).count()
            
            return {
                'total_messages': total_messages,
                'sent_messages': sent_messages,
                'failed_messages': failed_messages,
                'pending_messages': pending_messages,
                'success_rate': round((sent_messages / total_messages * 100), 2) if total_messages > 0 else 0,
                'today_messages': today_messages,
                'today_sent': today_sent,
                'total_contacts': session.query(Contact).count(),
                'total_templates': session.query(SMSTemplate).count(),
                'total_groups': session.query(ContactGroup).count()
            }
        finally:
            session.close()
    
    def get_failed_messages_for_retry(self) -> List[Dict[str, Any]]:
        """Get failed messages that can be retried"""
        session = self.get_session()
        try:
            messages = session.query(SMSMessage).filter(
                SMSMessage.status == 'failed',
                SMSMessage.retry_count < 3
            ).all()
            
            result = []
            for msg in messages:
                result.append({
                    'id': msg.id,
                    'recipient_phone': msg.recipient_phone,
                    'message_content': msg.message_content,
                    'message_type': msg.message_type,
                    'status': msg.status,
                    'retry_count': msg.retry_count,
                    'error_message': msg.error_message
                })
            return result
        finally:
            session.close()

# Global database manager instance
db_manager = DatabaseManager()