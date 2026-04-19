"""
Seed the database with default users and bank rates.
Run once on first startup — safe to run multiple times (idempotent).
"""
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.core.config import get_settings
from app.models.user import User, Rate, UserRole, LoanType

settings = get_settings()


DEFAULT_RATES = [
    dict(bank_id="anz",   name="ANZ",                abbr="ANZ", color="#005B99", text_color="#fff", bank_type="Major Bank",    loan_type=LoanType.variable, min_rate=5.89, max_rate=7.99, comp_rate=6.21, has_offset=True,  has_redraw=True,  annual_fees=395),
    dict(bank_id="cba",   name="Commonwealth Bank",  abbr="CBA", color="#FFC72C", text_color="#111", bank_type="Major Bank",    loan_type=LoanType.variable, min_rate=5.99, max_rate=8.14, comp_rate=6.28, has_offset=True,  has_redraw=True,  annual_fees=395),
    dict(bank_id="wbc",   name="Westpac",            abbr="WBC", color="#D5002B", text_color="#fff", bank_type="Major Bank",    loan_type=LoanType.variable, min_rate=6.09, max_rate=8.24, comp_rate=6.35, has_offset=False, has_redraw=True,  annual_fees=395),
    dict(bank_id="nab",   name="NAB",                abbr="NAB", color="#CC0000", text_color="#fff", bank_type="Major Bank",    loan_type=LoanType.variable, min_rate=5.94, max_rate=8.09, comp_rate=6.26, has_offset=True,  has_redraw=True,  annual_fees=395),
    dict(bank_id="mqb",   name="Macquarie Bank",     abbr="MQB", color="#4B2C8A", text_color="#fff", bank_type="Online Lender", loan_type=LoanType.variable, min_rate=5.74, max_rate=7.49, comp_rate=5.99, has_offset=True,  has_redraw=True,  annual_fees=248),
    dict(bank_id="ing",   name="ING",                abbr="ING", color="#FF6200", text_color="#fff", bank_type="Online Lender", loan_type=LoanType.variable, min_rate=5.79, max_rate=7.39, comp_rate=6.04, has_offset=False, has_redraw=True,  annual_fees=0  ),
    dict(bank_id="ath",   name="Athena",             abbr="ATH", color="#00A693", text_color="#fff", bank_type="Online Lender", loan_type=LoanType.variable, min_rate=5.69, max_rate=7.19, comp_rate=5.79, has_offset=False, has_redraw=True,  annual_fees=0  ),
    dict(bank_id="sun",   name="Suncorp",            abbr="SUN", color="#E4B400", text_color="#111", bank_type="Regional Bank", loan_type=LoanType.variable, min_rate=6.14, max_rate=8.29, comp_rate=6.44, has_offset=True,  has_redraw=True,  annual_fees=375),
    dict(bank_id="boq",   name="Bank of Queensland", abbr="BOQ", color="#E02020", text_color="#fff", bank_type="Regional Bank", loan_type=LoanType.variable, min_rate=6.19, max_rate=8.34, comp_rate=6.50, has_offset=False, has_redraw=True,  annual_fees=350),
    dict(bank_id="ben",   name="Bendigo Bank",       abbr="BEN", color="#E87722", text_color="#fff", bank_type="Regional Bank", loan_type=LoanType.variable, min_rate=6.09, max_rate=8.09, comp_rate=6.38, has_offset=False, has_redraw=True,  annual_fees=350),
    dict(bank_id="cba_f", name="CBA Fixed 2yr",      abbr="CBA", color="#FFC72C", text_color="#111", bank_type="Fixed Rate",    loan_type=LoanType.fixed,    min_rate=6.29, max_rate=7.99, comp_rate=7.12, has_offset=False, has_redraw=False, annual_fees=395),
    dict(bank_id="anz_f", name="ANZ Fixed 3yr",      abbr="ANZ", color="#005B99", text_color="#fff", bank_type="Fixed Rate",    loan_type=LoanType.fixed,    min_rate=6.09, max_rate=7.79, comp_rate=6.98, has_offset=False, has_redraw=False, annual_fees=395),
    dict(bank_id="mqb_f", name="Macquarie Fixed",    abbr="MQB", color="#4B2C8A", text_color="#fff", bank_type="Fixed Rate",    loan_type=LoanType.fixed,    min_rate=5.99, max_rate=7.49, comp_rate=6.64, has_offset=False, has_redraw=False, annual_fees=248),
]


def _upsert_user(db: Session, email: str, password: str, full_name: str, role: UserRole):
    """Create user if missing, or sync password from env vars on every startup."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        # Always re-hash from current env var so Render dashboard
        # password changes take effect immediately on next deploy
        user.hashed_pw = hash_password(password)
        print(f"  ✓ Synced password for: {email}")
    else:
        db.add(User(
            email=email,
            full_name=full_name,
            hashed_pw=hash_password(password),
            role=role,
        ))
        print(f"  ✓ Created {role.value} user: {email}")


def seed_database(db: Session):
    """Seed default users and rates. Passwords are re-synced every startup."""

    # ── USERS ──────────────────────────────────────────────────
    _upsert_user(db, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD,
                 "Admin", UserRole.admin)
    _upsert_user(db, settings.BROKER_EMAIL, settings.BROKER_PASSWORD,
                 "Mortgage Broker", UserRole.broker)

    # ── RATES ──────────────────────────────────────────────────
    for r in DEFAULT_RATES:
        if not db.query(Rate).filter(Rate.bank_id == r["bank_id"]).first():
            db.add(Rate(**r))
            print(f"  ✓ Added rate: {r['name']}")

    db.commit()
    print("  ✓ Database seeded successfully")
