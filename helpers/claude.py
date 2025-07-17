import re
import os
from datetime import datetime

def parse_gmail_data(gmail_text):
    """Parse Gmail conversation data into individual emails"""
    
    emails = []
    lines = gmail_text.split('\n')
    current_email = []
    email_started = False
    
    for i, line in enumerate(lines):
        # Check if this line starts a new email (sender with email and timestamp)
        if re.match(r'^[^<]+<[^@]+@[^>]+>\s+\w+,\s+\d+\s+\w+,\s+\d+\s+at\s+\d+:\d+', line):
            # If we have a current email, save it
            if current_email and email_started:
                emails.append('\n'.join(current_email))
            
            # Start new email
            current_email = [line]
            email_started = True
        elif email_started:
            current_email.append(line)
    
    # Add the last email
    if current_email and email_started:
        emails.append('\n'.join(current_email))
    
    return emails

def extract_email_info(email_text):
    """Extract structured information from email text"""
    
    lines = email_text.split('\n')
    
    # Extract sender info from first line
    sender_match = re.search(r'^([^<]+)<([^>]+)>', lines[0])
    if not sender_match:
        return None
    
    sender_name = sender_match.group(1).strip()
    sender_email = sender_match.group(2).strip()
    
    # Extract date from first line
    date_match = re.search(r'(\w+,\s+\d+\s+\w+,\s+\d+\s+at\s+\d+:\d+\s*(?:am|pm))', lines[0], re.IGNORECASE)
    date_str = date_match.group(1) if date_match else ""
    
    # Extract To field
    to_field = ""
    for line in lines[1:]:
        if line.startswith('To:'):
            to_field = line.replace('To:', '').strip()
            break
    
    # Extract Cc field
    cc_field = ""
    for line in lines[1:]:
        if line.startswith('Cc:'):
            cc_field = line.replace('Cc:', '').strip()
            break
    
    # Extract Subject
    subject = ""
    for line in lines[1:]:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
            break
    
    # Extract email body - start after headers
    body_lines = []
    header_section = True
    
    for line in lines[1:]:
        if header_section:
            if line.strip() == "" or (not line.startswith(('To:', 'Cc:', 'Subject:', 'Reply to:', 'From:')) and line.strip() != ""):
                header_section = False
                if line.strip():
                    body_lines.append(line)
        else:
            body_lines.append(line)
    
    body = '\n'.join(body_lines).strip()
    
    # Clean up body - remove quoted text markers and excessive newlines
    body = re.sub(r'------ Original Message ------.*$', '', body, flags=re.DOTALL)
    body = re.sub(r'\[Quoted text hidden\].*$', '', body, flags=re.DOTALL)
    body = re.sub(r'\n\s*\n\s*\n', '\n\n', body)
    body = body.strip()
    
    return {
        'sender_name': sender_name,
        'sender_email': sender_email,
        'date': date_str,
        'to': to_field,
        'cc': cc_field,
        'subject': subject,
        'body': body
    }

def format_email_output(email_info):
    """Format email info into the required output format"""
    
    output = f"From: {email_info['sender_email']}\n"
    
    if email_info['to']:
        output += f"To: {email_info['to']}\n"
    
    if email_info['subject']:
        output += f"Subject: {email_info['subject']}\n"
    
    if email_info['date']:
        # Try to convert date to standard format
        try:
            # Parse date like "Wed, 25 Jun, 2025 at 10:38 am"
            date_clean = email_info['date'].replace(',', '').replace(' at ', ' ')
            parsed_date = datetime.strptime(date_clean, '%a %d %b %Y %I:%M %p')
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            output += f"Date: {formatted_date}\n"
        except:
            output += f"Date: {email_info['date']}\n"
    
    if email_info['cc']:
        output += f"Cc: {email_info['cc']}\n"
    
    output += "\n"
    
    if email_info['body']:
        output += email_info['body']
    
    return output

def process_gmail_pdf_data(input_text):
    """Main function to process Gmail PDF data"""
    
    # Create output directory
    output_dir = "parsed_emails"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Parse emails
    raw_emails = parse_gmail_data(input_text)
    
    processed_emails = []
    
    for i, email_text in enumerate(raw_emails):
        email_info = extract_email_info(email_text)
        
        if email_info:
            formatted_email = format_email_output(email_info)
            
            # Generate filename
            filename = f"email_{i+1:03d}.txt"
            
            # Save to file
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_email)
            
            processed_emails.append({
                'filename': filename,
                'sender': email_info['sender_email'],
                'subject': email_info['subject'][:50] + "..." if len(email_info['subject']) > 50 else email_info['subject']
            })
    
    return processed_emails

with open(os.path.join('cleaned', 'mailrajib.txt'), 'r') as f:
    content = f.read()
    process_gmail_pdf_data(content)
