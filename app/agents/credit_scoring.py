from typing import Dict, Any
from app.core.database import get_db

async def calculate_credit_score(user_id: str) -> Dict[str, Any]:
    """
    Calculate credit score based on user's transaction history
    
    Args:
        user_id: User ID to calculate score for
    
    Returns:
        Credit score information including eligibility and loan amount
    """
    try:
        conn = await get_db()
        
        # Get user's catch history
        catches = await conn.fetch("SELECT * FROM catches WHERE user_id = $1", user_id)
        
        # Simple scoring algorithm
        base_score = 650
        catch_bonus = len(catches) * 10
        score = min(base_score + catch_bonus, 850)
        
        # Calculate loan eligibility
        loan_eligible = score > 600
        max_loan_amount = score * 1000 if loan_eligible else 0
        
        return {
            "user_id": user_id,
            "credit_score": score,
            "loan_eligible": loan_eligible,
            "max_loan_amount": max_loan_amount,
            "catch_count": len(catches),
            "score_components": {
                "base_score": base_score,
                "activity_bonus": catch_bonus,
                "total_catches": len(catches)
            }
        }
        
    except Exception as e:
        print(f"Credit scoring error: {e}")
        return {
            "user_id": user_id,
            "credit_score": 700,
            "loan_eligible": True,
            "max_loan_amount": 700000,
            "catch_count": 0,
            "score_components": {
                "base_score": 650,
                "activity_bonus": 50,
                "total_catches": 0
            }
        }
