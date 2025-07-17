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
            text_content += page.get_text() # No extra newline between pages as parsing will handle breaks
        doc.close()
        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return None

def split_email_thread_by_replies(full_text):
    """
    Splits a continuous email thread text into individual email messages.
    Prioritizes splitting by '------ Original Message ------' and then by new email headers.
    """
    # Normalize newline characters for consistent splitting
    full_text = full_text.replace('\r\n', '\n').replace('\r', '\n')

    # Define a clear separator pattern that includes "------ Original Message ------"
    # and also a robust pattern for new email headers (From:, To:, Subject:, Date:)
    # The idea is to split by "Original Message" first, and then within those chunks,
    # identify individual emails by their headers.

    # Pattern for the "Original Message" separator and similar variations
    # This acts as a strong delimiter for older parts of the conversation.
    # original_message_separator_pattern = re.compile(
    #     r"^-+\s*Original Message\s*-+\s*\n|^\s*From\s+\"?[^\n]+?\"\s+<[^\n]+?>\s*\nDate\s+[^\n]+\nSubject\s+[^\n]+",
    #     re.MULTILINE | re.IGNORECASE
    # )

#     original_message_separator_pattern = re.compile(
#     r"^-+\s*Original Message\s*-+\s*\n|"      # Matches "------ Original Message ------"
#     r"^-+\s*Forwarded message\s*-+\s*\n|"     # Matches "---------- Forwarded message ----------"
#     r"^\s*From\s+\"?[^\n]+?\"\s+<[^\n]+?>\s*\nDate\s+[^\n]+\nSubject\s+[^\n]+", # Matches new email headers
#     re.MULTILINE | re.IGNORECASE
# )

    original_message_separator_pattern = re.compile(
        r"^-+\s*Original Message\s*-+\s*\n|"      # Matches "------ Original Message ------"
        r"^-+\s*Forwarded message\s*-+\s*\n|"     # Matches "---------- Forwarded message ----------"
        r"^\s*From\s+\"?[^\n]+?\"\s*<[^\n]+?>?\s*\n(?:Date|Sent):\s*[^\n]+\nSubject:\s*[^\n]+", # Matches new email headers
        re.MULTILINE | re.IGNORECASE
    )

    # Split the main text by the strong "Original Message" separators
    # This will give us chunks, where each chunk should ideally be a single email or a series of quoted emails.
    raw_segments = original_message_separator_pattern.split(full_text)

    # Process each raw segment to extract individual emails within them
    email_messages = []
    for i, segment in enumerate(raw_segments):
        segment = segment.strip()
        if not segment:
            continue

        # For the first segment (most recent email), it will likely start with headers.
        # For subsequent segments (older emails), they might also start with headers
        # if the "Original Message" pattern was just a generic one.

        # Regex to find standard email headers
        # This will capture "From:", "To:", "Cc:", "Subject:", "Date:" lines.
        # We need to be careful not to split within a legitimate header block.
        header_pattern = re.compile(
            r"^(From:|To:|Cc:|Subject:|Date:|Reply to:)\s*.*$",
            re.MULTILINE | re.IGNORECASE
        )

        # Find the first set of headers in this segment.
        # This assumes the latest email in a segment will start with its own headers.
        header_start_match = re.search(r"^(From:.*?\n(?:To:.*?\n)?(?:Cc:.*?\n)?(?:Reply to:.*?\n)?Subject:.*?\nDate:.*?\n)", segment, re.MULTILINE | re.IGNORECASE | re.DOTALL)


        if header_start_match:
            # If we found a clear header block, consider the part before it as part of the previous email
            # (which would be handled by a previous segment or filtered out if it's junk).
            # The actual content of this email starts from the matched headers.
            # We want to ensure we capture the headers along with their body.
            current_email_body_start_index = header_start_match.start()
            # Find where the header block ends and the actual body begins (first blank line after headers)
            body_start_match = re.search(r"^\s*$", segment[current_email_body_start_index:], re.MULTILINE)

            if body_start_match:
                # The headers and the body of this specific email
                full_email_segment_start_index = current_email_body_start_index
                full_email_segment_end_index = body_start_match.start() + current_email_body_start_index
                # The actual email block to be saved
                email_content_with_headers = segment[full_email_segment_start_index:] # Take from headers till end of segment

                email_messages.append(email_content_with_headers.strip())

        else:
            # If no clear headers, but it's not empty, just add the whole segment.
            # This might happen for the very first (most recent) email if the header pattern wasn't perfect,
            # or for very short quoted blocks.
            email_messages.append(segment.strip())


    # Filter out empty or very short segments that might be just artifacts
    return [s for s in email_messages if len(s) > 50] # Minimum length to consider a valid email segment

def convert_pdf_to_multiple_txt_by_reply_refined(pdf_path, output_directory):
    """
    Converts a single PDF containing an email thread into multiple text files,
    one for each detected email reply, with a refined splitting strategy.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    full_text = extract_text_from_pdf(pdf_path)

    if full_text:
        email_messages = split_email_thread_by_replies(full_text)

        if not email_messages:
            print(f"No distinct email messages found in '{pdf_path}' based on reply patterns. Saving as single text file.")
            with open(os.path.join(output_directory, f"{base_filename}_full.txt"), "w", encoding="utf-8") as f:
                f.write(full_text)
            return

        for i, msg in enumerate(email_messages):
            # Attempt to extract a simple subject for filename if available in the segment
            subject_match = re.search(r"^Subject:\s*(.*)", msg, re.MULTILINE | re.IGNORECASE)
            subject_for_filename = ""
            if subject_match:
                subject_for_filename = subject_match.group(1).strip()
                # Sanitize subject for filename (remove invalid characters and shorten)
                subject_for_filename = re.sub(r'[\\/:*?"<>|]', '_', subject_for_filename)
                subject_for_filename = subject_for_filename[:60].strip() # Truncate for brevity
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
single_pdf_file_path = "mailpdfs/mailrajib.pdf" # Replace with the actual path to your mailrajib.pdf file
# Set this to the directory where you want to save the individual text files
output_texts_folder = "extracted_email_replies"

if __name__ == "__main__":
    convert_pdf_to_multiple_txt_by_reply_refined(single_pdf_file_path, output_texts_folder)
    print("Email reply splitting process completed.")