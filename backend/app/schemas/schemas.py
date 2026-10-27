from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)
    display_name: str = Field(..., min_length=2, max_length=100)
    default_currency: str = Field(default="INR", max_length=3)

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str
    client_id: Optional[str] = None

class UserOut(BaseModel):
    id: str
    email: str
    display_name: str
    default_currency: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- Account Schemas ---
class AccountBase(BaseModel):
    name: str
    account_type: str = "bank" # cash, bank, wallet, credit_card
    currency: str = "INR"
    opening_balance: Decimal = Decimal("0.00")

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    opening_balance: Optional[Decimal] = None
    is_archived: Optional[bool] = None

class AccountOut(AccountBase):
    id: str
    user_id: str
    is_archived: bool
    created_at: datetime
    current_balance: Optional[Decimal] = None

    class Config:
        from_attributes = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str
    category_type: str # income, expense, bill, savings, debt
    color: str = "#006B45"
    icon: Optional[str] = "tag"

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: str
    user_id: Optional[str] = None
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    transaction_type: str # income, expense, bill, savings, debt, transfer
    amount: Decimal = Field(..., gt=0)
    currency: str = "INR"
    transaction_date: date
    merchant: Optional[str] = None
    note: Optional[str] = None
    source: str = "manual"

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

class TransactionUpdate(BaseModel):
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    transaction_date: Optional[date] = None
    merchant: Optional[str] = None
    note: Optional[str] = None

class TransactionOut(BaseModel):
    id: str
    user_id: str
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    transaction_type: str
    amount: Decimal
    currency: str
    transaction_date: date
    merchant: Optional[str] = None
    note: Optional[str] = None
    source: str
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    account_name: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    items: List[TransactionOut]
    total: int
    page: int
    page_size: int
    total_pages: int

# --- Budget Schemas ---
class BudgetCreate(BaseModel):
    category_id: Optional[str] = None # null = overall
    period_start: date
    period_end: date
    limit_amount: Decimal = Field(..., gt=0)
    alert_threshold_pct: int = Field(default=80, ge=1, le=100)

class BudgetUpdate(BaseModel):
    limit_amount: Optional[Decimal] = Field(None, gt=0)
    alert_threshold_pct: Optional[int] = Field(None, ge=1, le=100)

class BudgetOut(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    period_start: date
    period_end: date
    limit_amount: Decimal
    alert_threshold_pct: int
    created_at: datetime
    actual_spent: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    percentage_used: float = 0.0
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True

# --- Bill Schemas ---
class BillCreate(BaseModel):
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    name: str
    expected_amount: Decimal = Field(..., gt=0)
    due_date: date
    recurrence: str = "monthly" # once, weekly, monthly, yearly
    status: str = "upcoming" # upcoming, paid, overdue, cancelled

class BillUpdate(BaseModel):
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    name: Optional[str] = None
    expected_amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[date] = None
    recurrence: Optional[str] = None
    status: Optional[str] = None

class BillOut(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    name: str
    expected_amount: Decimal
    due_date: date
    recurrence: str
    status: str
    created_at: datetime
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True

# --- Alert Schemas ---
class AlertOut(BaseModel):
    id: str
    user_id: str
    budget_id: Optional[str] = None
    alert_type: str
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Dashboard & Analytics Schemas ---
class DashboardSummaryOut(BaseModel):
    period: str
    currency: str
    total_income: Decimal
    total_expenses: Decimal
    total_bills: Decimal
    total_debt_payments: Decimal
    total_savings: Decimal
    total_outflows: Decimal
    balance_left: Decimal
    budget_limit: Decimal
    budget_used_pct: float
    recent_transactions: List[TransactionOut]
    upcoming_bills: List[BillOut]

class CategorySpendingItem(BaseModel):
    category_id: Optional[str]
    category_name: str
    category_type: str
    color: str
    amount: Decimal
    percentage: float
    transaction_count: int

class BudgetVsActualItem(BaseModel):
    category_id: Optional[str]
    category_name: str
    budget_limit: Decimal
    actual_spent: Decimal
    percentage_used: float
    remaining: Decimal
    status: str # normal, warning, exceeded

class CashFlowTrendItem(BaseModel):
    month: str # e.g. "2026-05"
    income: Decimal
    expenses: Decimal
    bills: Decimal
    savings: Decimal
    net_savings: Decimal

# --- ML & Forecast Schemas ---
class ForecastOut(BaseModel):
    target_period: str
    predicted_expense: Decimal
    currency: str
    method: str
    history_months: int
    confidence_label: str # high, medium, low
    lower_bound: Optional[Decimal] = None
    upper_bound: Optional[Decimal] = None
    explanation: str
    historical_points: List[Dict[str, Any]]
    limitations: str

class BudgetRecommendationOut(BaseModel):
    category_id: str
    category_name: str
    current_budget: Optional[Decimal]
    recent_avg_spend: Decimal
    recommended_budget_min: Decimal
    recommended_budget_max: Decimal
    explanation: str
    urgency: str # stable, adjust_up, adjust_down

class CategorySuggestionRequest(BaseModel):
    merchant: Optional[str] = None
    note: Optional[str] = None
    amount: Optional[Decimal] = None
    transaction_type: Optional[str] = "expense"

class CategorySuggestionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    suggested_category_id: Optional[str]
    suggested_category_name: Optional[str]
    confidence: float
    model_version: str
    matched_rule: Optional[str] = None

class CSVImportResult(BaseModel):
    total_rows: int
    imported_count: int
    duplicate_count: int
    errors: List[str]
