import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime

# Initialize Faker with Indian locale for realistic corporate names & locations
fake = Faker('en_IN')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generate_synthetic_borrowers(num_records=200):
    sectors = [
        'Electronics & Electricals', 'Hospitality & Services', 'Auto Components',
        'Textiles & Apparel', 'Pharmaceuticals', 'Chemicals', 'Steel & Metals',
        'Infrastructure & Construction', 'IT & Software Services', 'FMCG'
    ]
    
    constitutions = ['Private Limited', 'Public Limited', 'LLP', 'Partnership']
    listings = ['Unlisted', 'Listed']
    facility_types = ['WC + TL + NFB (LC/BG)', 'WC + TL', 'WC + NFB (LC/BG)', 'Working Capital (WC)', 'Term Loan (TL)']
    banking_arrangements = ['Sole Banking', 'Consortium', 'Multiple Banking']
    states = ['Andhra Pradesh', 'Kerala', 'Delhi NCR', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Gujarat', 'Maharashtra']
    ratings = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'B', 'C', 'D']
    rms = ['Rahul Bose', 'Neha Rao', 'Sneha Shah', 'Priya Shah', 'Amit Sharma', 'Rohan Mehta', 'Kavita Singh']

    company_suffixes = ['Pvt Ltd', 'Ltd', 'LLP', 'Enterprises', 'Industries', 'Corporation', 'Logistics']

    data = []

    for i in range(1, num_records + 1):
        borrower_id = f"EWSB-{i:04d}"
        
        # Synthetic Company Name Generation
        company_base = fake.company().split()[0].replace(',', '')
        suffix = random.choice(company_suffixes)
        borrower_name = f"{company_base} {suffix}"
        
        constitution = random.choice(constitutions)
        listing = 'Listed' if constitution == 'Public Limited' and random.random() > 0.6 else 'Unlisted'
        sector = random.choice(sectors)
        state = random.choice(states)
        facility = random.choice(facility_types)
        banking = random.choice(banking_arrangements)
        
        # Sanctioned & Outstanding Limit (in ₹ Cr)
        sanctioned_limit = round(float(np.random.uniform(5.0, 500.0)), 1)
        # Outstanding is generally <= Sanctioned limit
        outstanding = round(float(sanctioned_limit * np.random.uniform(0.3, 0.98)), 1)
        
        rating = random.choice(ratings)
        rm = random.choice(rms)
        assessment_date = "2026-08-31"

        data.append({
            "Borrower ID": borrower_id,
            "Borrower Name": borrower_name,
            "Constitution": constitution,
            "Listing": listing,
            "Sector": sector,
            "State": state,
            "Facility Type": facility,
            "Banking Arrangement": banking,
            "Sanctioned Limit (₹ Cr)": sanctioned_limit,
            "Outstanding (₹ Cr)": outstanding,
            "Internal Rating": rating,
            "Relationship Manager": rm,
            "Assessment Date": assessment_date
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    num_borrowers = 200
    df_synthetic = generate_synthetic_borrowers(num_borrowers)
    
    # Save to Excel
    output_filename = "Synthetic_Borrower_Data_Generated.xlsx"
    df_synthetic.to_excel(output_filename, index=False, sheet_name="Borrower Master")
    print(f"✅ Successfully generated {num_borrowers} synthetic corporate borrowers!")
    print(f"📁 Saved to: {output_filename}")
    print("\nPreview:")
    print(df_synthetic.head())