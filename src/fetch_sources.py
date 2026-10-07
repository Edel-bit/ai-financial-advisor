"""Download a curated starter library of free, public-domain financial sources.

    python src/fetch_sources.py          # download everything not already present
    python src/ingest.py                 # then load the new files into the knowledge base

IRS publications are U.S. government works (public domain) and are the
authoritative source for federal tax rules. The irs.gov/pub/irs-pdf/ links
always point at the CURRENT revision, so re-run this each January (with
--refresh) to pick up the new tax year's numbers, then `python src/ingest.py --force`.

Other high-quality sources that must be downloaded by hand are listed in
README.md ("Building the knowledge base").
"""
import argparse
import time
import urllib.request

from config import DATA_DIR

IRS = "https://www.irs.gov/pub/irs-pdf/"

SOURCES = {
    "tax_optimization/irs_publications": {
        "p17.pdf": "Your Federal Income Tax (the master guide for individuals)",
        "p501.pdf": "Dependents, Standard Deduction, and Filing Information",
        "p505.pdf": "Tax Withholding and Estimated Tax",
        "p525.pdf": "Taxable and Nontaxable Income",
        "p526.pdf": "Charitable Contributions",
        "p502.pdf": "Medical and Dental Expenses",
        "p936.pdf": "Home Mortgage Interest Deduction",
        "p523.pdf": "Selling Your Home",
        "p550.pdf": "Investment Income and Expenses (capital gains, dividends)",
        "p590a.pdf": "IRAs - Contributions",
        "p590b.pdf": "IRAs - Distributions (RMDs, early withdrawals)",
        "p575.pdf": "Pension and Annuity Income (401k distributions)",
        "p915.pdf": "Social Security and Equivalent Railroad Retirement Benefits",
        "p969.pdf": "Health Savings Accounts and Other Tax-Favored Health Plans",
        "p970.pdf": "Tax Benefits for Education (529s, AOTC, student loan interest)",
        "p596.pdf": "Earned Income Credit",
        "p4681.pdf": "Canceled Debts, Foreclosures, Repossessions",
    },
    "tax_optimization/self_employed": {
        "p334.pdf": "Tax Guide for Small Business",
        "p587.pdf": "Business Use of Your Home",
        "p463.pdf": "Travel, Gift, and Car Expenses",
        "p560.pdf": "Retirement Plans for Small Business (SEP, SIMPLE, Solo 401k)",
        "p535.pdf": "Business Expenses",
    },
}


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ai-financial-advisor)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError("response was not a PDF")
    dest.write_bytes(data)
    return len(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="re-download files that already exist")
    args = parser.parse_args()

    for folder, files in SOURCES.items():
        out_dir = DATA_DIR / folder
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, title in files.items():
            dest = out_dir / name
            # p17 may already live one folder up from an earlier setup
            if not args.refresh and (dest.exists() or any(DATA_DIR.rglob(name))):
                print(f"  = {name:10s} already present")
                continue
            try:
                size = download(IRS + name, dest)
                print(f"  ✓ {name:10s} {size/1e6:5.1f} MB  {title}")
            except Exception as e:  # IRS occasionally retires or renames a publication
                print(f"  ✗ {name:10s} failed ({e})")
            time.sleep(0.5)  # be polite to irs.gov

    print("\nNext: python src/ingest.py")


if __name__ == "__main__":
    main()
