# Streamlit App: Ledger – Finance Agent
import streamlit as st
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage

st.title("💰 Ledger – Finance Agent")
st.write("Ledger manages billing, payroll, and Medicaid tracking for Tilo Haven Senior Living.")

# Helper: Email Alert with routing by alert type
def send_email_alert(subject, content, alert_type="general"):
    email_map = {
        "invoice": "billing@tilohaven.com",
        "medicaid": "medicaid@tilohaven.com",
        "payroll": "hr@tilohaven.com",
        "summary": "finance@tilohaven.com",
        "general": "admin@tilohaven.com"
    }
    to_email = email_map.get(alert_type, "admin@tilohaven.com")
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "admin@tilohaven.com"
        msg["To"] = to_email
        msg["Cc"] = "admin@tilohaven.com"
        msg.set_content(content)

        with smtplib.SMTP_SSL("smtppro.zoho.com", 465) as smtp:
            smtp.login("admin@tilohaven.com", "WealthPack1120!!")
            smtp.send_message(msg)
    except Exception as e:
        st.error(f"Failed to send alert email: {e}")

# Resident Invoicing
st.header("📄 Resident Invoicing")
if "invoices" not in st.session_state:
    st.session_state.invoices = []

with st.form("invoice_form"):
    resident_name = st.text_input("Resident Name")
    billing_amount = st.number_input("Billing Amount ($)", min_value=0.0, step=50.0)
    billing_date = st.date_input("Billing Date", datetime.today())
    billing_type = st.selectbox("Billing Type", ["Private Pay", "Medicaid", "Other"])
    invoice_notes = st.text_area("Notes (e.g. Late fees, adjustments, etc.)")
    submit_invoice = st.form_submit_button("Submit Invoice")

if submit_invoice:
    st.session_state.invoices.append({
        "resident": resident_name,
        "amount": billing_amount,
        "date": billing_date,
        "type": billing_type,
        "notes": invoice_notes
    })
    st.success(f"✅ Invoice recorded for {resident_name} on {billing_date}.")

# Invoice Summary & Intelligence
st.subheader("🧾 Invoice Summary")
total_revenue = 0
for invoice in st.session_state.invoices:
    days_old = (datetime.today().date() - invoice['date']).days
    tag = ""
    if days_old > 30:
        tag = "🔴 Overdue"
        if invoice['type'] == "Medicaid":
            tag += " ⚠️ High Risk"
        send_email_alert(
            subject="Overdue Invoice Alert",
            content=f"Resident: {invoice['resident']}\nAmount: ${invoice['amount']}\nDate: {invoice['date']}\nNotes: {invoice['notes']}",
            alert_type="invoice"
        )
    total_revenue += invoice['amount']
    st.write(f"{invoice['date']} – {invoice['resident']} | ${invoice['amount']} | {invoice['type']} | {tag} | Notes: {invoice['notes']}")
if not st.session_state.invoices:
    st.info("No invoices submitted yet.")

# Payroll Section
st.header("🧑‍💼 Payroll Management")
if "payroll" not in st.session_state:
    st.session_state.payroll = []

with st.form("payroll_form"):
    employee_name = st.text_input("Employee Name")
    hours_worked = st.number_input("Hours Worked", min_value=0.0, step=1.0)
    hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=1.0)
    payroll_date = st.date_input("Payroll Date", datetime.today())
    submit_payroll = st.form_submit_button("Submit Payroll Entry")

if submit_payroll:
    gross_pay = hours_worked * hourly_rate
    st.session_state.payroll.append({
        "employee": employee_name,
        "hours": hours_worked,
        "rate": hourly_rate,
        "date": payroll_date,
        "total": gross_pay
    })
    st.success(f"✅ Payroll entry recorded for {employee_name}. Gross Pay: ${gross_pay:.2f}")
    if hours_worked > 80 or gross_pay > 2000:
        st.warning(f"⚠️ Review: {employee_name} worked {hours_worked} hrs or earned > $2,000.")
        send_email_alert(
            subject="Payroll Alert: Overtime or High Pay",
            content=f"Employee: {employee_name}\nHours: {hours_worked}\nGross Pay: ${gross_pay:.2f}",
            alert_type="payroll"
        )

# Payroll Summary
st.subheader("📊 Payroll Summary")
total_payroll = 0
for entry in st.session_state.payroll:
    total_payroll += entry['total']
    st.write(f"{entry['date']} – {entry['employee']} | {entry['hours']} hrs @ ${entry['rate']} = ${entry['total']:.2f}")
if not st.session_state.payroll:
    st.info("No payroll entries submitted yet.")

# Medicaid Claims
st.header("🧾 Medicaid Claim Tracker")
if "medicaid_claims" not in st.session_state:
    st.session_state.medicaid_claims = []

with st.form("medicaid_form"):
    claim_resident = st.text_input("Resident Name (Claim)")
    claim_amount = st.number_input("Claim Amount ($)", min_value=0.0, step=50.0)
    claim_date = st.date_input("Date of Claim", datetime.today())
    claim_status = st.selectbox("Claim Status", ["Submitted", "Pending", "Approved", "Denied"])
    claim_notes = st.text_area("Notes (authorization, errors, etc.)")
    submit_claim = st.form_submit_button("Submit Medicaid Claim")

if submit_claim:
    st.session_state.medicaid_claims.append({
        "resident": claim_resident,
        "amount": claim_amount,
        "date": claim_date,
        "status": claim_status,
        "notes": claim_notes
    })
    st.success(f"✅ Medicaid claim recorded for {claim_resident} – Status: {claim_status}")
    if claim_status == "Denied":
        send_email_alert(
            subject="Medicaid Claim Denied",
            content=f"Resident: {claim_resident}\nAmount: ${claim_amount}\nDate: {claim_date}\nNotes: {claim_notes}",
            alert_type="medicaid"
        )

# Medicaid Summary
st.subheader("📁 Medicaid Claims Summary")
claim_approved = 0
for claim in st.session_state.medicaid_claims:
    if claim['status'] == "Approved":
        claim_approved += 1
    st.write(f"{claim['date']} – {claim['resident']} | ${claim['amount']} | Status: {claim['status']} | Notes: {claim['notes']}")
if not st.session_state.medicaid_claims:
    st.info("No Medicaid claims submitted yet.")

# Financial Summary
st.header("📈 Monthly Financial Snapshot")
claim_total = len(st.session_state.medicaid_claims)
approval_rate = f"{(claim_approved / claim_total * 100):.1f}%" if claim_total > 0 else "N/A"
st.markdown(f"- **Total Revenue This Month:** ${total_revenue:.2f}")
st.markdown(f"- **Total Payroll Paid:** ${total_payroll:.2f}")
st.markdown(f"- **Medicaid Approval Rate:** {approval_rate}")
