import asyncio
import logging
from services.payment_service import PaymentService
from config.settings import settings

logging.basicConfig(
    format=r'%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    payment_service = PaymentService()
    logger.info("Creating Stripe products and prices...")
    result = await payment_service.create_products_and_prices()
    
    if result["success"]:
        logger.info("Stripe products and prices created successfully!")
        for product in result["products"]:
           logger.info(f"  Product: {product['lookup_key']} - Price ID: {product['price_id']} - Amount: ${product['amount'] / 100:.2f}")
    else:
        logger.error(f"Failed to create Stripe products and prices: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())

