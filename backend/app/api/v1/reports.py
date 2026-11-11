from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.report import DailyAppointmentReportResponse, RevenueReportResponse
from backend.app.patterns.factories.report_factory import ReportGeneratorFactory
from backend.app.api.deps import get_current_user

router = APIRouter()


@router.get(
    "/reports/daily-appointments",
    response_model=DailyAppointmentReportResponse,
    tags=["Reports & Analytics"],
    summary="Daily Appointment Summary Report",
    description="Generates daily appointment counts, status breakdown (SCHEDULED, COMPLETED, CANCELLED), and doctor workload distribution using the ReportGeneratorFactory.",
)
def get_daily_appointments_report(
    report_date: Optional[date] = Query(None, alias="date", description="Target calendar date (default: today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = report_date or date.today()
    try:
        generator = ReportGeneratorFactory.create_generator("daily_appointments")
        result = generator.generate(db, {"date": target})
        return DailyAppointmentReportResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(exc)}",
        )


@router.get(
    "/reports/revenue",
    response_model=RevenueReportResponse,
    tags=["Reports & Analytics"],
    summary="Financial Revenue Analytics Report",
    description="Aggregates gross consultation billing, discounts granted, tax collected, net revenue, and payment method breakdown (Cash, Card, Mobile Banking) using the ReportGeneratorFactory.",
)
def get_revenue_report(
    start_date: Optional[date] = Query(None, description="Start date for revenue reporting window (default: today)"),
    end_date: Optional[date] = Query(None, description="End date for revenue reporting window (default: today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s_date = start_date or date.today()
    e_date = end_date or date.today()
    try:
        generator = ReportGeneratorFactory.create_generator("revenue")
        result = generator.generate(db, {"start_date": s_date, "end_date": e_date})
        return RevenueReportResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revenue report generation error: {str(exc)}",
        )
