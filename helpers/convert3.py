import fitz # PyMuPDF library
import os
import re

def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a single PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        text_content = ""
        for page in doc:
            text_content += page.get_text()
        doc.close()
        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return None

def split_email_thread(full_text):
    """
    Splits a continuous email thread text into individual email messages based on common patterns.
    It prioritizes 'From: ... Subject: ... Date:' headers for new emails.
    It also looks for "Original Message" as a separator.
    """
    # Pattern to find the start of a new email based on From, To/Cc, Subject, and Date lines
    # This pattern is more robust for identifying new email blocks within a thread.
    # It specifically looks for a "From:" line followed by other header-like lines (To, Cc, Subject, Date)
    # and then a newline before the body.
    # The 'flags=re.IGNORECASE | re.DOTALL' makes the search case-insensitive and '.' match newlines.

    # Strong pattern for a new email block, often seen at the start of a new reply
    email_block_pattern = re.compile(
        r"^(From:.*?)(?=(?:^From:|\nSubject:|\nDate:|\nOriginal Message|\n--- PAGE \d+ ---|\Z))",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    # Secondary pattern to split by "Original Message" if the above doesn't catch everything
    original_message_pattern = re.compile(r"^\s*Original Message\s*$", re.MULTILINE | re.IGNORECASE)

    # First, try to split by the strong email block pattern
    email_segments = []
    last_end = 0
    for match in email_block_pattern.finditer(full_text):
        start = match.start()
        if start > last_end:
            # Add the text before this match as a segment if it's not empty
            segment = full_text[last_end:start].strip()
            if segment:
                email_segments.append(segment)
        email_segments.append(match.group(1).strip()) # Add the matched block
        last_end = match.end(1)

    if last_end < len(full_text):
        # Add any remaining text as the last segment
        remaining_segment = full_text[last_end:].strip()
        if remaining_segment:
            email_segments.append(remaining_segment)

    # Now, refine segments further by "Original Message" or page breaks if they contain multiple messages
    final_segments = []
    for segment in email_segments:
        # Split by "Original Message" within the current segment
        sub_segments = original_message_pattern.split(segment)
        for sub_segment in sub_segments:
            # Further split by page numbers introduced by PDF extraction tools
            page_split_segments = re.split(r"^\s*---\s*PAGE\s*\d+\s*---\s*$", sub_segment, flags=re.MULTILINE)
            for final_sub_segment in page_split_segments:
                cleaned_segment = final_sub_segment.strip()
                if cleaned_segment:
                    final_segments.append(cleaned_segment)

    # Filter out empty or very short segments that might be just artifacts
    return [s for s in final_segments if len(s) > 50] # Minimum length to consider a valid email segment


def convert_single_pdf_to_multiple_txt_by_reply(pdf_path, output_directory):
    """
    Converts a single PDF containing an email thread into multiple text files,
    one for each detected email reply.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    full_text = extract_text_from_pdf(pdf_path)

    if full_text:
        email_messages = split_email_thread(full_text)

        if not email_messages:
            print(f"No distinct email messages found in '{pdf_path}'. Saving as single text file.")
            with open(os.path.join(output_directory, f"{base_filename}_full.txt"), "w", encoding="utf-8") as f:
                f.write(full_text)
            return

        for i, msg in enumerate(email_messages):
            # Attempt to extract a simple subject for filename if available in the segment
            subject_match = re.search(r"^Subject:\s*(.*)", msg, re.MULTILINE | re.IGNORECASE)
            subject_for_filename = ""
            if subject_match:
                # Sanitize subject for filename (remove invalid characters and shorten)
                subject_for_filename = subject_match.group(1).strip()
                subject_for_filename = re.sub(r'[\\/:*?"<>|]', '_', subject_for_filename) # Replace invalid chars
                subject_for_filename = subject_for_filename[:50].strip() # Truncate for brevity
                if subject_for_filename:
                    subject_for_filename = f"_{subject_for_filename}"

            txt_filename = f"{base_filename}_part_{i+1}{subject_for_filename}.txt"
            output_filepath = os.path.join(output_directory, txt_filename)

            try:
                with open(output_filepath, "w", encoding="utf-8") as f:
                    f.write(msg)
                print(f"Saved part {i+1} of '{base_filename}' to '{txt_filename}'")
            except Exception as e:
                print(f"Error writing segment {i+1} for '{base_filename}': {e}")
    else:
        print(f"Could not extract text from '{pdf_path}'. Skipping.")


# --- Configuration ---
# Set this to the path of your single PDF file
single_pdf_file_path = "mailpdfs/mailrajib.pdf" # This should be the full path to your mailrajib.pdf file
# Set this to the directory where you want to save the individual text files
output_texts_folder = "extracted_emails"

if __name__ == "__main__":
    convert_single_pdf_to_multiple_txt_by_reply(single_pdf_file_path, output_texts_folder)
    print("Email reply splitting process completed.")