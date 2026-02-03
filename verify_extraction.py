from docling.document_converter import DocumentConverter
import os

# Path to the test file
file_path = r"c:\projects\python\Ragheed\book generation Dr. Fahed pipeline\v1.0 test extraction\Files_for_testing\دورة تدريب متدربين TOT.docx"
output_dir = "extracted_docs"

os.makedirs(output_dir, exist_ok=True)

print(f"Processing file: {file_path}")

try:
    converter = DocumentConverter()
    result = converter.convert(file_path)
    md_content = result.document.export_to_markdown()
    
    output_file = os.path.join(output_dir, "test_output.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Extraction successful. Saved to {output_file}")
    print(f"Content length: {len(md_content)} characters")
    print("First 500 chars:")
    print(md_content[:500])
    
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
