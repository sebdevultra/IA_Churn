from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from backend.app.models.interaction import Interaction


class InteractionRepository:

    @staticmethod
    def get_by_id(db: Session, interaction_id: int) -> Optional[Interaction]:
        return (
            db.query(Interaction)
            .options(
                joinedload(Interaction.sentiment),
                joinedload(Interaction.frictions),
                joinedload(Interaction.churn_risk),
                joinedload(Interaction.customer)
            )
            .filter(Interaction.id == interaction_id)
            .first()
        )

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Interaction], int]:
        query = (
            db.query(Interaction)
            .options(
                joinedload(Interaction.sentiment),
                joinedload(Interaction.frictions),
                joinedload(Interaction.churn_risk),
                joinedload(Interaction.customer)
            )
        )

        if customer_id:
            query = query.filter(Interaction.customer_id == customer_id)
        if status:
            query = query.filter(Interaction.status == status.upper())

        total = query.count()
        items = query.order_by(desc(Interaction.created_at)).offset(skip).limit(limit).all()
        return items, total
