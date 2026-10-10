"""
Document processing service for CampusMate AI.
Handles PDF text extraction via PyMuPDF, image validation via Pillow,
and plain text extraction.
"""
import io
import pymupdf  # PyMuPDF
from PIL import Image
from typing import Tuple, Optional

class DocumentService:
    """Service for validating and extracting text or image data from documents."""

    MAX_PAGES = 30  # Limit PDF page parsing for performance and safety

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """
        Extract text from a text-based PDF using PyMuPDF.
        Rejects corrupt PDFs and empty/scanned PDFs with informative messages.
        """
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise ValueError(
                "Unable to read this PDF file. The file may be corrupt or encrypted. "
                "Please upload a valid PDF."
            ) from e

        if doc.page_count == 0:
            doc.close()
            raise ValueError("The uploaded PDF has 0 pages.")

        extracted_text_parts = []
        pages_to_check = min(doc.page_count, DocumentService.MAX_PAGES)

        for page_num in range(pages_to_check):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text and text.strip():
                extracted_text_parts.append(text.strip())

        doc.close()

        delimiter = "\n\n"
        combined_text = delimiter.join(extracted_text_parts).strip()

        # If zero or virtually no text was extracted, it is likely a scanned PDF
        if len(combined_text) < 15:
            raise ValueError(
                "This PDF appears to contain scanned pages or images without readable text. "
                "Please upload the notice directly as an image (PNG/JPG) or paste its text."
            )

        return combined_text

    @staticmethod
    def validate_and_prepare_image(file_bytes: bytes, filename: str) -> Tuple[bytes, str]:
        """
        Validate image data using Pillow and return bytes and MIME type.
        """
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()  # Verify image integrity
            
            # Determine mime type
            img_format = (image.format or "JPEG").lower()
            if img_format == "png":
                mime_type = "image/png"
            elif img_format in ("jpg", "jpeg"):
                mime_type = "image/jpeg"
            elif img_format == "webp":
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"

            return file_bytes, mime_type
        except Exception as e:
            raise ValueError(
                "Invalid or corrupted image file. Please upload a valid PNG, JPG, or WEBP image."
            ) from e

    @staticmethod
    def extract_from_txt(file_bytes: bytes) -> str:
        """
        Extract text from a .txt file.
        """
        try:
            return file_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            try:
                return file_bytes.decode("latin-1").strip()
            except Exception as e:
                raise ValueError("Could not decode plain text file. Please ensure UTF-8 encoding.") from e

document_service = DocumentService()
