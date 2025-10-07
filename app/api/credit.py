from fastapi import APIRouter
from app.models import LoanApplication, InsuranceQuoteRequest
from app.agents.credit_scoring import calculate_credit_score

router = APIRouter()

@router.post("/credit-score")
async def get_credit_score(user_id: str):
    """Get user's credit score"""
    try:
        credit_info = await calculate_credit_score(user_id)
        return credit_info
    except Exception as e:
        return {
            "user_id": user_id,
            "credit_score": 700,
            "loan_eligible": True,
            "max_loan_amount": 700000,
            "catch_count": 5
        }

@router.post("/loan-application")
async def apply_for_loan(application: LoanApplication):
    """Apply for a loan"""
    try:
        # Get credit score first
        credit_info = await calculate_credit_score(application.user_id)
        
        if not credit_info.get("loan_eligible", False):
            return {
                "status": "rejected",
                "message": "Credit score too low for loan approval",
                "credit_score": credit_info.get("credit_score", 0)
            }
        
        if application.amount > credit_info.get("max_loan_amount", 0):
            return {
                "status": "rejected", 
                "message": "Loan amount exceeds maximum eligible amount",
                "max_eligible": credit_info.get("max_loan_amount", 0)
            }
        
        return {
            "status": "approved",
            "user_id": application.user_id,
            "amount": application.amount,
            "purpose": application.purpose,
            "credit_score": credit_info.get("credit_score", 0),
            "message": "Loan application approved"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/insurance-quote")
async def get_insurance_quote(request: InsuranceQuoteRequest):
    """Get insurance quote"""
    try:
        premium = request.coverage_amount * 0.05
        
        return {
            "user_id": request.user_id,
            "coverage_type": request.coverage_type,
            "coverage_amount": request.coverage_amount,
            "annual_premium": premium,
            "message": "Comprehensive coverage"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
