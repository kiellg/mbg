#pylint: disable=unused-argument
"""Router for payment endpoints."""

from fastapi import APIRouter, Depends, status

from backend.app.dependencies import get_current_user
from backend.app.schemas.payment import PaymentRequest, PaymentResponse

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/{order_id}",
             response_model=PaymentResponse,
             status_code=status.HTTP_201_CREATED,
             )
def process_payment(
    order_id: str,
    payload: PaymentRequest,
    current_user: Depends(get_current_user),
):
    """Customer submits payment details to finalize their order"""

    return NotImplementedError("""Payment service is not yet implemented
                               and will be added in SR44""")
