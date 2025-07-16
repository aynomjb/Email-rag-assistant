import os
import random
from datetime import datetime, timedelta
import zipfile

def generate_dummy_mail(mail_id, senders, recipients, cc_options, bcc_options):
    sender = random.choice(senders)
    to = random.choice(recipients)
    
    # Ensure sender and recipient are not the same if possible
    while to == sender and len(recipients) > 1:
        to = random.choice(recipients)

    subject_prefixes = [
        "Escalation: Urgent Action Required on Project X",
        "RE: Escalation - Critical Issue with System Y",
        "FW: Project Z Delay - Escalation Discussion",
        "Follow-up: Escalation on Performance Degradation",
        "Status Update: Escalated Problem Resolution",
        "Regarding: Escalation of Resource Allocation Issue",
        "Action Plan: Addressing Escalated Customer Complaint",
        "Discussion: Next Steps for Escalated Bug Report",
        "High Priority: Escalation of Security Vulnerability",
        "Urgent Review: Escalation of Budget Overrun"
    ]
    
    # Introduce variety in subjects for replies/forwards
    subject_suffixes = [
        "",
        " - Need your input",
        " - What's the status?",
        " - Please review ASAP",
        " - Further discussion needed",
        " - Action required",
        " - URGENT"
    ]
    
    subject = random.choice(subject_prefixes) + random.choice(subject_suffixes)

    # Use current year for date generation
    current_year = datetime.now().year
    # Generate dates within the last 30 days from current date (July 16, 2025)
    end_date = datetime(current_year, 7, 16)
    start_date = end_date - timedelta(days=30)
    
    time_delta = end_date - start_date
    random_days = random.uniform(0, time_delta.days)
    random_seconds = random.uniform(0, 24 * 3600) # Random seconds within a day
    date = start_date + timedelta(days=random_days, seconds=random_seconds)
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")

    bodies = [
        f"Hi {to.split('@')[0].capitalize()},\n\nI'm writing to follow up on the escalated issue with [specific problem]. We need to define concrete next steps immediately. Can we schedule a call for tomorrow to discuss the action plan?\n\nBest,\n{sender.split('@')[0].capitalize()}",
        f"Team,\n\nThis escalation requires urgent attention. We're seeing critical delays on [project name] and need to re-evaluate our approach. Please provide an update on your respective parts by EOD today.\n\nRegards,\n{sender.split('@')[0].capitalize()}",
        f"Hello {to.split('@')[0].capitalize()},\n\nRegarding the escalation of [issue], I've gathered the initial data. It seems the root cause might be [potential cause]. We should involve [department/person] to get a clearer picture.\n\nThanks,\n{sender.split('@')[0].capitalize()}",
        f"All,\n\nThe escalation on [task] is becoming a major blocker. What resources do we need to unblock this? I'm concerned about the timeline.\n\nThanks,\n{sender.split('@')[0].capitalize()}",
        f"Hi {to.split('@')[0].capitalize()},\n\nI've reviewed the details of the escalated case. It appears we missed [detail]. Let's ensure this doesn't happen again and put a mitigation plan in place.\n\nBest regards,\n{sender.split('@')[0].capitalize()}",
        f"Team,\n\nAn urgent escalation has come in regarding [customer/system]. The impact is [high/critical]. We need to convene an incident response call within the hour. Please confirm availability.\n\nThanks,\n{sender.split('@')[0].capitalize()}",
        f"Hello {to.split('@')[0].capitalize()},\n\nFollowing up on our last discussion about the escalation, I've managed to [action taken]. However, we still need to address [remaining issue].\n\nRegards,\n{sender.split('@')[0].capitalize()}",
        f"Hi all,\n\nThe escalated feedback from [stakeholder] is serious. We need to present a revised plan by [date]. What's our proposed solution?\n\nSincerely,\n{sender.split('@')[0].capitalize()}",
        f"Dear {to.split('@')[0].capitalize()},\n\nI'm forwarding this escalation request from [original sender]. Please provide your insights on how we can resolve this efficiently.\n\nThanks,\n{sender.split('@')[0].capitalize()}",
        f"Team,\n\nJust to reiterate the urgency of this escalation. We are at risk of [negative consequence] if we don't act swiftly. Let's prioritize this above all else.\n\nBest,\n{sender.split('@')[0].capitalize()}"
    ]
    
    body = random.choice(bodies)

    mail_content = f"From: {sender}\nTo: {to}\nSubject: {subject}\nDate: {date_str}"

    # Randomly add CC and BCC
    cc = []
    if random.random() < 0.7:  # 70% chance of having CC
        num_cc = random.randint(1, min(3, len(cc_options)))
        cc = random.sample(cc_options, num_cc)
        # Ensure CC recipients are not already in To or From
        cc = [email for email in cc if email != to and email != sender]
        if cc:
            mail_content += f"\nCc: {', '.join(cc)}"

    bcc = []
    if random.random() < 0.4:  # 40% chance of having BCC
        num_bcc = random.randint(1, min(2, len(bcc_options)))
        bcc = random.sample(bcc_options, num_bcc)
        # Ensure BCC recipients are not already in To, From or CC
        bcc = [email for email in bcc if email != to and email != sender and email not in cc]
        if bcc:
            mail_content += f"\nBcc: {', '.join(bcc)}"

    mail_content += f"\n\n{body}\n"

    filename = f"mail_{mail_id:02d}.txt"
    with open(filename, "w") as f:
        f.write(mail_content)
    return filename

def create_and_zip_mails(num_mails=20):
    senders = [
        "bob@acmecorp.com", "alice@acmecorp.com", "charlie@acmecorp.com",
        "diana@acmecorp.com", "eve@acmecorp.com", "frank@acmecorp.com"
    ]
    recipients = [
        "grace@acmecorp.com", "heidi@acmecorp.com", "ivan@acmecorp.com",
        "judy@acmecorp.com", "kevin@acmecorp.com", "liam@acmecorp.com",
        "maya@acmecorp.com"
    ]
    cc_options = [
        "qa@acmecorp.com", "devops@acmecorp.com", "marketing@acmecorp.com",
        "legal@acmecorp.com", "support@acmecorp.com", "finance@acmecorp.com"
    ]
    bcc_options = [
        "ceo@acmecorp.com", "cto@acmecorp.com", "hr@acmecorp.com"
    ]

    generated_files = []
    print(f"Generating {num_mails} dummy mail files...")
    for i in range(num_mails):
        filename = generate_dummy_mail(i + 1, senders, recipients, cc_options, bcc_options)
        generated_files.append(filename)
        print(f"Created {filename}")

    zip_filename = "escalation_mails.zip"
    print(f"\nZipping all mail files into {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w') as zf:
        for file in generated_files:
            zf.write(file)
            os.remove(file)  # Clean up individual .txt files after zipping
    print("Zipping complete.")
    print(f"All files have been zipped into '{zip_filename}' and individual .txt files have been removed.")

# Run the script
create_and_zip_mails(20)