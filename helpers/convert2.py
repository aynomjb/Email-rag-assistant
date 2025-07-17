import fitz  # PyMuPDF library
import os

def convert_pdfs_to_txt(pdf_directory, output_directory):
    """
    Converts all PDF files in a given directory to text files.

    Args:
        pdf_directory (str): The path to the directory containing PDF files.
        output_directory (str): The path to the directory where
                                the text files will be saved.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    for filename in os.listdir(pdf_directory):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(output_directory, txt_filename)

            try:
                doc = fitz.open(pdf_path)
                text_content = ""
                for page in doc:
                    text_content += page.get_text() + "\n" # Extract text and add a newline for separation
                doc.close()

                with open(txt_path, "w", encoding="utf-8") as text_file:
                    text_file.write(text_content)
                print(f"Converted '{filename}' to '{txt_filename}'")
            except Exception as e:
                print(f"Error converting '{filename}': {e}")

# --- Configuration ---
# Replace 'path/to/your/pdfs' with the actual path to your PDF files
pdf_input_folder = "path/to/your/pdfs" 
# Replace 'path/to/your/output_texts' with where you want to save the text files
text_output_folder = "path/to/your/output_texts"

if __name__ == "__main__":
    convert_pdfs_to_txt("mailpdfs", "cleaned")
    print("PDF to TXT conversion process completed.")