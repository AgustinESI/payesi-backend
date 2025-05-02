from paypalserversdk.models.payment_token_request import PaymentTokenRequest
from paypalserversdk.models.payment_token_request_payment_source import PaymentTokenRequestPaymentSource
from paypalserversdk.models.payment_token_request_card import PaymentTokenRequestCard
from paypalserversdk.models.card_brand import CardBrand
from paypalserversdk.exceptions.error_exception import ErrorException
from paypalserversdk.exceptions.api_exception import ApiException
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.configuration import Environment
import logging
from paypalserversdk.logging.configuration.api_logging_configuration import LoggingConfiguration
from paypalserversdk.logging.configuration.api_logging_configuration import RequestLoggingConfiguration
from paypalserversdk.logging.configuration.api_logging_configuration import ResponseLoggingConfiguration
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.payment_source import PaymentSource
from paypalserversdk.models.card_request import CardRequest
from os import getenv
import uuid

client = PaypalServersdkClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id=getenv('PAYPAL_CLIENT_ID', 'your_client_id'),
        o_auth_client_secret=getenv('PAYPAL_CLIENT_SECRET', 'your_client_secret')
    ),
    environment=Environment.SANDBOX,
    logging_configuration=LoggingConfiguration(
        log_level=logging.INFO,
        request_logging_config=RequestLoggingConfiguration(
            log_body=True
        ),
        response_logging_config=ResponseLoggingConfiguration(
            log_headers=True
        )
    )
)

CARD_BRAND_MAPPING = {
    "visa": CardBrand.VISA,
    "mastercard": CardBrand.MASTERCARD,
    "amex": CardBrand.AMEX
}

class PaypalService:
    """Service class for PayPal operations."""

    @staticmethod
    def validate_card(card_data):
        """Validate a card."""
        vault_controller = client.vault
        day, month, year = card_data.get('expiration_date').split('/')
        expiration_date = f"{year}-{month}"
        collect = {
            'body': PaymentTokenRequest(
                payment_source=PaymentTokenRequestPaymentSource(
                    card=PaymentTokenRequestCard(
                        name=card_data.get('card_holder_name'),
                        number=card_data.get('number'),
                        expiry=expiration_date,
                        security_code=card_data.get('cvv'),
                        brand= CARD_BRAND_MAPPING.get(card_data.get('type'), CardBrand.UNKNOWN)
                    )
                )
            )
        }
        try:
            result =  vault_controller.create_payment_token(collect)
            return result.body.id
        except ErrorException as e: 
            raise e
        except ApiException as e: 
            raise e
        
    @staticmethod
    def authorize_charge(card_token, amount):
        """Authorize the charge of funds to a card."""
        orders_controller = client.orders
        collect = {
            'body': OrderRequest(
                intent=CheckoutPaymentIntent.CAPTURE,
                purchase_units=[
                    PurchaseUnitRequest(
                        amount=AmountWithBreakdown(
                            currency_code='EUR',
                            value=amount
                        )
                    )
                ],
                payment_source=PaymentSource(
                    card=CardRequest(
                        vault_id=card_token
                    )
                )
            ),
            'paypal_request_id': uuid.uuid4(),
            'prefer': 'return=minimal'
        }
        try:
            result = orders_controller.create_order(collect)
            return result
        except ErrorException as e: 
            raise e
        except ApiException as e: 
            raise e