# src/utils/csv_manager.py
import csv
import os
import re
from .database import SessionLocal
from .helpers import log_action
from src.models import CustomerCompany, Product, Inventory

class CsvManager:
    def __init__(self, companies_tab, inventory_tab, audit_log_tab):
        self.companies_tab = companies_tab
        self.inventory_tab = inventory_tab
        self.audit_log_tab = audit_log_tab

    def handle_import_csv(self, file_name):
        try:
            with SessionLocal() as db_session:
                companies_cache = {c.name: c for c in db_session.query(CustomerCompany).all()}

                with open(file_name, mode='r', encoding='utf-8-sig') as infile:
                    reader = csv.DictReader(infile)
                    for row in reader:
                        company_name = row.get('CompanyName', '').strip()
                        if not company_name:
                            continue

                        company = companies_cache.get(company_name)
                        if not company:
                            state_raw = row.get('State', '').strip()
                            state_name, state_code = self._parse_state(state_raw)

                            company = CustomerCompany(
                                name=company_name, address=row.get('Address', '').strip(),
                                state=state_name, state_code=state_code,
                                gstin=row.get('GSTIN', '').strip()
                            )
                            db_session.add(company)
                            db_session.flush()
                            companies_cache[company_name] = company

                        product_name = row.get('ProductName', '').strip()
                        if product_name:
                            price_str = row.get('Price', '0').strip()
                            price = float(price_str) if price_str else 0.0
                            new_product = Product(name=product_name, price=price, company_id=company.id)
                            new_inventory = Inventory(stock_quantity=0, product=new_product)
                            db_session.add(new_product)
                            db_session.add(new_inventory)

                log_action(db_session, "IMPORT", "System", None, f"Imported data from CSV file: {os.path.basename(file_name)}.")
                db_session.commit()

            self.companies_tab.load_companies()
            self.inventory_tab.load_inventory_data()
            self.audit_log_tab.load_logs()
            return True, "Data imported successfully!"
        except Exception as e:
            return False, f"An error occurred during import:\n{e}"

    def handle_export_csv(self, file_name):
        try:
            with SessionLocal() as db_session:
                companies = db_session.query(CustomerCompany).order_by(CustomerCompany.name).all()
                with open(file_name, mode='w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(['CompanyName', 'CompanyID', 'Address', 'State', 'GSTIN', 'ProductID', 'ProductName', 'Price'])

                    for company in companies:
                        state_formatted = f"{company.state} (Code: {company.state_code})"
                        if not company.products:
                            writer.writerow([company.name, company.id, company.address, state_formatted, company.gstin, '', '', ''])
                        else:
                            for product in sorted(company.products, key=lambda p: p.name):
                                writer.writerow([company.name, company.id, company.address, state_formatted, company.gstin, product.id, product.name, product.price])

                log_action(db_session, "EXPORT", "System", None, f"Exported data to CSV file: {os.path.basename(file_name)}.")
                db_session.commit()

            self.audit_log_tab.load_logs()
            return True, "Data exported successfully!"
        except Exception as e:
            return False, f"An error occurred during export:\n{e}"

    def _parse_state(self, state_raw):
        match = re.search(r"(.+?)\s*\(Code:\s*(\d+)\)", state_raw)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return state_raw, ""
