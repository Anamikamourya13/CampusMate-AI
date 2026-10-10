"""
Document processing service for CampusMate AI.
Handles text-based and scanned PDF extraction via PyMuPDF, image validation via Pillow,
and plain text extraction.
"""
import io
import pymupdf
from PIL import Image
from typing import Tuple, Optional, List, Union

class DocumentService:
    """Service for validating and extracting text or image data from documents."""

    MAX_PAGES = 30  # Limit PDF page parsing for performance and safety
    MAX_SCANNED_PAGES = 5  # Max pages to render for scanned PDFs

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> Tuple[str, Optional[str], Optional[List[Tuple[bytes, str]]]]:
        """
        Process a PDF file.
        1. If text layer exists, extracts text.
        2. If it is a scanned document (zero or minimal text), automatically renders
           the pages to high-resolution PNG images so Gemini Vision can analyze them.
        Returns:
            ("text", text_string, None) or ("scanned_images", None, [(png_bytes, "image/png"), ...])
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

        delimiter = "\n\n"
        combined_text = delimiter.join(extracted_text_parts).strip()

        # If sufficient readable text was found, return text-based payload
        if len(combined_text) >= 15:
            doc.close()
            return "text", combined_text, None

        # Scanned PDF detected: Render pages as high-resolution PNGs for Gemini Vision
        rendered_images: List[Tuple[bytes, str]] = []
        pages_to_render = min(doc.page_count, DocumentService.MAX_SCANNED_PAGES)

        for page_num in range(pages_to_render):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            if img_bytes:
                rendered_images.append((img_bytes, "image/png"))

        doc.close()

        if not rendered_images:
            raise ValueError(
                "This PDF appears to be empty and contains no readable text or images."
            )

        return "scanned_images", None, rendered_images

    @staticmethod
    def validate_and_prepare_image(file_bytes: bytes, filename: str) -> Tuple[bytes, str]:
        """
        Validate image data using Pillow and return bytes and MIME type.
        """
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()  # Verify image integrity
            
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
