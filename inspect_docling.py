from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions
from docling.document_converter import DocumentConverter

print("--- PdfPipelineOptions Attributes ---")
try:
    opts = PdfPipelineOptions()
    for attr in dir(opts):
        if not attr.startswith("_"):
            val = getattr(opts, attr)
            print(f"{attr}: {val}")
except Exception as e:
    print(f"Error inspecting PdfPipelineOptions: {e}")

print("\n--- Trying to initialize converter ---")
try:
    converter = DocumentConverter()
    print("Converter initialized successfully.")
    print(f"Converter pipeline options: {converter.format_to_pipeline_options}")
except Exception as e:
    print(f"Error initializing converter: {e}")
