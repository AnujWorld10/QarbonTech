from fastapi import APIRouter
from src.endpoints import (
    cancel_product_order, charge, charge_notification, cross_connect_move,
    events_subscription, get_auth_token, health_check,
    modify_productorderItem_requested_deliverydate_notification,
    modify_request_deliverydate, performance_profile, performance_report,
    performanceprofile_notification, performancereport_notification,
    product_order, product_ordering_notification, get_auth_token,delete_attachment,upload_attachment)

router = APIRouter()

router.include_router(get_auth_token.router)
router.include_router(health_check.router)
router.include_router(performance_profile.router)
router.include_router(performance_report.router)
router.include_router(product_order.router)
router.include_router(product_ordering_notification.router)
router.include_router(performanceprofile_notification.router)
router.include_router(performancereport_notification.router)
router.include_router(cancel_product_order.router)
router.include_router(events_subscription.router)
router.include_router(charge_notification.router)
router.include_router(modify_request_deliverydate.router)
router.include_router(charge.router)
router.include_router(modify_productorderItem_requested_deliverydate_notification.router)
router.include_router(cross_connect_move.router)
router.include_router(upload_attachment.router)
router.include_router(delete_attachment.router)

