# tests/test_pdf_service.py
import unittest
import os
from src.utils.pdf_service import PdfService
from src.models.user import UserSettings
from src.utils.database import SessionLocal, Base, engine

class TestPdfService(unittest.TestCase):
    def setUp(self):
        # Create a dummy settings object
        self.settings = UserSettings(
            company_name="Test Company",
            gstin="1234567890",
            pan_number="ABCDE1234F",
            email="test@example.com",
            upi_id="test@upi",
            tagline="This is a test tagline.",
            state_code="27"  # Maharashtra
        )
        # Create a dummy invoice data object
        self.invoice_data = {
            "invoice_number": "INV-20240101-1",
            "date": "2024-01-01",
            "vehicle_number": "MH-01-AB-1234",
            "customer": {
                "name": "Test Customer",
                "address": "Test Address",
                "gstin": "0987654321",
                "state_code": "27"  # Maharashtra
            },
            "items": [
                {
                    "product_name": "Test Product 1",
                    "quantity": 2,
                    "price_per_unit": 100.00
                },
                {
                    "product_name": "Test Product 2",
                    "quantity": 1,
                    "price_per_unit": 200.00
                }
            ]
        }

    def test_generate_invoice(self):
        # Generate the PDF
        pdf_service = PdfService(self.settings)
        file_name = pdf_service.generate_invoice(self.invoice_data)

        # Check that the file was created
        self.assertTrue(os.path.exists(file_name))

        # TODO: Add assertions to check the content of the PDF

        # Clean up the file
        os.remove(file_name)

if __name__ == '__main__':
    unittest.main()
