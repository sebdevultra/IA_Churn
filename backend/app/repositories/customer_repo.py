from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models.customer import Customer
from backend.app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:

    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_by_external_id(db: Session, external_id: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.external_id == external_id.strip().upper()).first()

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        risk_level: Optional[str] = None
    ) -> Tuple[List[Customer], int]:
        query = db.query(Customer)
        if risk_level:
            query = query.filter(Customer.current_risk_level == risk_level.upper())

        total = query.count()
        items = query.order_by(desc(Customer.current_risk_score), desc(Customer.last_interaction_at)).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def create(db: Session, obj_in: CustomerCreate) -> Customer:
        db_obj = Customer(
            external_id=obj_in.external_id.strip().upper(),
            name=obj_in.name,
            email=obj_in.email,
            tier=obj_in.tier,
            historical_summary=obj_in.historical_summary or "",
            current_risk_score=0,
            current_risk_level="LOW"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, db_obj: Customer, obj_in: CustomerUpdate) -> Customer:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
