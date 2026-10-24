
import tempfile
import os

from langchain_community.document_loaders import PyMuPDFLoader


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Load a PDF using LangChain's PyMuPDFLoader."""

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        loader = PyMuPDFLoader(temp_path)
        documents = loader.load()

        full_text = "\n\n".join(
            f"Page {doc.metadata.get('page', 0) + 1}\n"
            f"{doc.page_content}"
            for doc in documents
            if doc.page_content.strip()
        ).strip()

        if len(full_text) < 30:
            raise ValueError(
                "PDF se sufficient text extract nahi hua. "
                "Scanned PDF ke liye OCR required ho sakta hai."
            )

        return full_text

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "PDF read nahi hui. Please valid PDF upload karo."
        ) from exc

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
