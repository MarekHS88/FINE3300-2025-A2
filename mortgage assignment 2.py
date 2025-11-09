# mortgage_schedule.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Mortgage class (expanded)
# ----------------------------
class MortgagePayment:
    """
    Canadian mortgage math:
    - Input rate is nominal compounded semi-annually (the Canadian convention).
    - Convert to EAR, then to the per-period rate for each payment frequency.
    - Payment amount is based on amortization, schedule length is based on term.
    """
    def __init__(self, nominal_rate_pct: float, amort_years: int, term_years: int):
        # store as decimals/ints
        self.nominal_rate = nominal_rate_pct / 100.0
        self.amort_years = int(amort_years)
        self.term_years = int(term_years)

        # Convert quoted semi-annual nominal rate to EAR (effective annual rate)
        self.ear = (1 + (self.nominal_rate / 2.0)) ** 2 - 1

        # Period rates
        self.r_mo = (1 + self.ear) ** (1 / 12) - 1           # monthly (12/yr)
        self.r_sm = (1 + self.ear) ** (1 / 24) - 1           # semi-monthly (24/yr)
        self.r_bw = (1 + self.ear) ** (1 / 26) - 1           # bi-weekly (26/yr)
        self.r_wk = (1 + self.ear) ** (1 / 52) - 1           # weekly (52/yr)

        # Number of payments for amortization horizon
        self.n_mo_amort = self.amort_years * 12
        self.n_sm_amort = self.amort_years * 24
        self.n_bw_amort = self.amort_years * 26
        self.n_wk_amort = self.amort_years * 52

        # Number of payments for the term horizon (how many rows to output)
        self.n_mo_term = self.term_years * 12
        self.n_sm_term = self.term_years * 24
        self.n_bw_term = self.term_years * 26
        self.n_wk_term = self.term_years * 52

    @staticmethod
    def _pmt(P, r, n):
        """Level-payment annuity formula: Payment = P * r / (1 - (1+r)^-n)"""
        if r == 0:
            return P / n
        return P * r / (1 - (1 + r) ** (-n))

    def base_payments(self, principal: float):
        """
        Compute the six periodic payment amounts.
        Rapid plans are defined off the monthly payment (standard Canadian convention):
          - rapid bi-weekly = monthly / 2, applied on a bi-weekly schedule
          - rapid weekly    = monthly / 4, applied on a weekly schedule
        """
        monthly      = MortgagePayment._pmt(principal, self.r_mo, self.n_mo_amort)
        semi_monthly = MortgagePayment._pmt(principal, self.r_sm, self.n_sm_amort)
        bi_weekly    = MortgagePayment._pmt(principal, self.r_bw, self.n_bw_amort)
        weekly       = MortgagePayment._pmt(principal, self.r_wk, self.n_wk_amort)

        rapid_bi_weekly = monthly / 2.0
        rapid_weekly    = monthly / 4.0

        return {
            "Monthly":            (monthly,           self.r_mo, self.n_mo_term),
            "Semi-Monthly":       (semi_monthly,      self.r_sm, self.n_sm_term),
            "Bi-Weekly":          (bi_weekly,         self.r_bw, self.n_bw_term),
            "Weekly":             (weekly,            self.r_wk, self.n_wk_term),
            "Rapid Bi-Weekly":    (rapid_bi_weekly,   self.r_bw, self.n_bw_term),
            "Rapid Weekly":       (rapid_weekly,      self.r_wk, self.n_wk_term),
        }

    @staticmethod
    def _build_schedule_df(principal: float, pay: float, r: float, n_periods: int):
        """
        Build a schedule DataFrame for up to n_periods or until the loan pays off,
        whichever comes first.
        Columns: Period, Starting Balance, Interest, Payment, Ending Balance
        All monetary values rounded to cents in the output.
        """
        periods = []
        start_balances = []
        interests = []
        payments = []
        end_balances = []

        balance = float(principal)

        for t in range(1, n_periods + 1):
            if balance <= 1e-8:
                break  # already paid off

            interest = balance * r
            # Regular payment but cap to avoid negative ending balance on final period
            this_payment = min(pay, balance + interest)
            end_balance = balance + interest - this_payment

            periods.append(t)
            start_balances.append(balance)
            interests.append(interest)
            payments.append(this_payment)
            end_balances.append(end_balance)

            balance = end_balance

        df = pd.DataFrame({
            "Period": periods,
            "Starting Balance": np.round(start_balances, 2),
            "Interest": np.round(interests, 2),
            "Payment": np.round(payments, 2),
            "Ending Balance": np.round(end_balances, 2)
        })
        return df

    def build_all_schedules(self, principal: float):
        """
        Returns a dict of DataFrames for all 6 payment options.
        """
        pays = self.base_payments(principal)
        schedules = {}
        for name, (pmt, rate, n_term) in pays.items():
            schedules[name] = self._build_schedule_df(principal, pmt, rate, n_term)
        return schedules


# ----------------------------
# Script entry point
# ----------------------------
def main():
    # User input
    P = float(input("Enter mortgage principal: "))
    r_pct = float(input("Enter nominal interest rate (%), compounded semi-annually: "))
    amort_years = int(input("Enter amortization period (years): "))
    term_years = int(input("Enter term of mortgage (years): "))

    # Build schedules
    m = MortgagePayment(r_pct, amort_years, term_years)
    schedules = m.build_all_schedules(P)

    # Show payment amounts
    print("\nComputed periodic payments (based on amortization):")
    pays = m.base_payments(P)
    for name, (pmt, _, _) in pays.items():
        print(f"  {name:>18}: ${pmt:,.2f}")

    # Save to one Excel file (multiple sheets)
    excel_name = "mortgage_schedules.xlsx"
    with pd.ExcelWriter(excel_name) as writer:
        for name, df in schedules.items():
            # Worksheet names must be <= 31 chars; these are short enough
            df.to_excel(writer, sheet_name=name, index=False)
    print(f"\nSaved schedules to: {excel_name}")

    # Plot balance decline for all 6 schedules on one chart
    plt.figure(figsize=(10, 6))
    for name, df in schedules.items():
        plt.plot(df["Period"], df["Ending Balance"], label=name)

    plt.title("Loan Balance Decline by Payment Schedule")
    plt.xlabel("Period Number (within term)")
    plt.ylabel("Ending Balance ($)")
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)

    png_name = "loan_balance_decline.png"
    plt.tight_layout()
    plt.savefig(png_name, dpi=200)
    plt.close()
    print(f"Saved plot to: {png_name}")


if __name__ == "__main__":
    main()
# End of mortgage_schedule.py

