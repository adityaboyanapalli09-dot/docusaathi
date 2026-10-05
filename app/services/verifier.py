from io import BytesIO
from pypdf import PdfReader
import re
import cv2
import numpy as np
import fitz


def verify_document(filename, content_type, file_size, file_contents):

    # User-facing verification values
    detected_file_type = {
        "application/pdf": "PDF",
        "image/jpeg": "JPG",
        "image/png": "PNG",
    }.get(content_type, "Unknown")

    checks = {
        "file_type": detected_file_type,
        "file_size": "passed",
        "pdf_structure": "not_checked",
        "text_content": "not_checked",
        "document_identity": "not_checked",
        "issuer": "not_checked",
        "document_number": "not_checked",
        "digital_signature": "not_checked",
        "qr_code": "not_checked",
        "metadata": "not_checked",
        "internal_consistency": "not_checked",
        "visual_tampering": "not_checked",
        "official_source": "not_checked"
    }

    warnings = []
    extracted_text_length = 0
    extracted_text = ""

    # 1. File type
    if content_type not in [
        "application/pdf",
        "image/jpeg",
        "image/png"
    ]:
        checks["file_type"] = "Unknown"
        warnings.append("Unsupported document format.")

    # 2. File size
    if file_size == 0:
        checks["file_size"] = "failed"
        warnings.append("The uploaded document is empty.")

    # 3. PDF structure + text
    if content_type == "application/pdf":
        try:
            reader = PdfReader(BytesIO(file_contents))
            page_count = len(reader.pages)

            if page_count > 0:
                checks["pdf_structure"] = "passed"

                text_parts = []

                for page in reader.pages:
                    text = page.extract_text() or ""
                    text_parts.append(text)

                extracted_text = "\n".join(text_parts).strip()
                extracted_text_length = len(extracted_text)

                if extracted_text_length > 20:
                    checks["text_content"] = "passed"
                else:
                    checks["text_content"] = "warning"
                    warnings.append(
                        "Very little readable text was found in the PDF."
                    )

            else:
                checks["pdf_structure"] = "failed"
                warnings.append("The PDF contains no pages.")

        except Exception:
            checks["pdf_structure"] = "failed"
            warnings.append("The PDF could not be read correctly.")

    # 4. Document identity checks
    if extracted_text:
        identity_patterns = [
            r"\bnotice\b",
            r"\bapplication\b",
            r"\border\b",
            r"\bcertificate\b",
            r"\bguidelines\b",
            r"\bdepartment\b",
            r"\bgovernment\b",
            r"\bministry\b",
            r"\bletter\b",
            r"\bstatement\b"
        ]

        matches = []

        for pattern in identity_patterns:
            if re.search(pattern, extracted_text, re.IGNORECASE):
                matches.append(pattern)

        if matches:
            # Return the actual document identity instead of the technical
            # value "passed".
            identity_map = {
                r"\bnotice\b": "Notice",
                r"\bapplication\b": "Application",
                r"\border\b": "Order",
                r"\bcertificate\b": "Certificate",
                r"\bguidelines\b": "Guidelines",
                r"\bdepartment\b": "Department document",
                r"\bgovernment\b": "Government document",
                r"\bministry\b": "Ministry document",
                r"\bletter\b": "Letter",
                r"\bstatement\b": "Statement",
            }

            detected_identity = "Official document"
            for pattern in identity_patterns:
                if re.search(pattern, extracted_text, re.IGNORECASE):
                    detected_identity = identity_map.get(pattern, "Official document")
                    break

            checks["document_identity"] = detected_identity
        else:
            checks["document_identity"] = "warning"
            warnings.append(
                "The document does not contain obvious official-document identifiers."
            )

    # 5. Issuer check
    issuer_patterns = [
        r"\bincome tax department\b",
        r"\bministry\b",
        r"\bgovernment of india\b",
        r"\bgovernment of\b",
        r"\bdepartment\b",
        r"\bmunicipal corporation\b",
        r"\breserve bank of india\b",
        r"\bstate government\b"
    ]

    if extracted_text:
        issuer_found = any(
            re.search(pattern, extracted_text, re.IGNORECASE)
            for pattern in issuer_patterns
        )

        if issuer_found:
            issuer_display_names = [
                (r"\bincome tax department\b", "Income Tax Department"),
                (r"\breserve bank of india\b", "Reserve Bank of India"),
                (r"\bgovernment of india\b", "Government of India"),
                (r"\bgovernment of\b", "Government"),
                (r"\bmunicipal corporation\b", "Municipal Corporation"),
                (r"\bstate government\b", "State Government"),
                (r"\bministry\b", "Ministry"),
                (r"\bdepartment\b", "Government Department"),
            ]

            detected_issuer = "Official issuer"
            for pattern, display_name in issuer_display_names:
                if re.search(pattern, extracted_text, re.IGNORECASE):
                    detected_issuer = display_name
                    break

            checks["issuer"] = detected_issuer
        else:
            checks["issuer"] = "warning"
            warnings.append(
                "No recognizable government or official issuer was detected."
            )

    # 6. Document/reference number check
    document_number_patterns = [
        r"\bnotice\s*(number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+",
        r"\bapplication\s*(number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+",
        r"\b(reference|ref\.?)\s*(number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+",
        r"\bregistration\s*(number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+"
    ]

    if extracted_text:
        document_number_found = any(
            re.search(pattern, extracted_text, re.IGNORECASE)
            for pattern in document_number_patterns
        )

        if document_number_found:
            detected_document_number = None

            for pattern in document_number_patterns:
                match = re.search(pattern, extracted_text, re.IGNORECASE)
                if match:
                    full_match = match.group(0)

                    # Extract the value after the colon/hyphen.
                    value_match = re.search(
                        r"[:\-]\s*([A-Z0-9][A-Z0-9\-/]*)\s*$",
                        full_match,
                        re.IGNORECASE
                    )

                    if value_match:
                        detected_document_number = value_match.group(1).strip()
                    else:
                        # Fallback: use the final alphanumeric token.
                        tokens = re.findall(
                            r"[A-Z0-9][A-Z0-9\-/]*",
                            full_match,
                            re.IGNORECASE
                        )
                        if tokens:
                            detected_document_number = tokens[-1]

                    if detected_document_number:
                        break

            checks["document_number"] = (
                detected_document_number
                if detected_document_number
                else "Detected"
            )
        else:
            checks["document_number"] = "warning"
            warnings.append(
                "No recognizable document or reference number was detected."
            )

    # 7. Digital signature check
    if content_type == "application/pdf":
        try:
            reader = PdfReader(BytesIO(file_contents))
            signature_found = False

            for obj in reader.resolved_objects.values():
                obj_text = str(obj)

                if (
                    "/Sig" in obj_text
                    or "/ByteRange" in obj_text
                ):
                    signature_found = True
                    break

            if signature_found:
                checks["digital_signature"] = "present"
            else:
                checks["digital_signature"] = "not_present"

        except Exception:
            checks["digital_signature"] = "not_checked"
    else:
        checks["digital_signature"] = "not_applicable"

    # 8. QR code detection
    qr_detector = cv2.QRCodeDetector()
    qr_found = False

    # 8A. Images embedded inside PDF
    if content_type == "application/pdf":
        try:
            reader = PdfReader(BytesIO(file_contents))

            for page in reader.pages:
                for image in page.images:

                    image_bytes = image.data

                    image_array = np.frombuffer(
                        image_bytes,
                        dtype=np.uint8
                    )

                    image_data = cv2.imdecode(
                        image_array,
                        cv2.IMREAD_COLOR
                    )

                    if image_data is None:
                        continue

                    decoded_text, points, _ = qr_detector.detectAndDecode(
                        image_data
                    )

                    if points is not None:
                        qr_found = True
                        break

                if qr_found:
                    break

        except Exception:
            pass

    # 8B. Render PDF pages and scan whole page
    if content_type == "application/pdf" and not qr_found:
        try:
            pdf_document = fitz.open(
                stream=file_contents,
                filetype="pdf"
            )

            for page in pdf_document:

                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )

                image_array = np.frombuffer(
                    pixmap.samples,
                    dtype=np.uint8
                )

                channels = pixmap.n

                if channels == 4:

                    image_data = image_array.reshape(
                        pixmap.height,
                        pixmap.width,
                        4
                    )

                    image_data = cv2.cvtColor(
                        image_data,
                        cv2.COLOR_RGBA2BGR
                    )

                else:

                    image_data = image_array.reshape(
                        pixmap.height,
                        pixmap.width,
                        channels
                    )

                    image_data = cv2.cvtColor(
                        image_data,
                        cv2.COLOR_RGB2BGR
                    )

                decoded_text, points, _ = qr_detector.detectAndDecode(
                    image_data
                )

                if points is not None:
                    qr_found = True
                    break

        except Exception:
            pass

    # 8C. Direct image upload
    if content_type in [
        "image/jpeg",
        "image/png"
    ] and not qr_found:

        try:

            image_array = np.frombuffer(
                file_contents,
                dtype=np.uint8
            )

            image_data = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image_data is not None:

                decoded_text, points, _ = qr_detector.detectAndDecode(
                    image_data
                )

                if points is not None:
                    qr_found = True

        except Exception:
            pass

    if qr_found:
        checks["qr_code"] = "detected"
    else:
        checks["qr_code"] = "not_present"

    # 9. PDF metadata check
    if content_type == "application/pdf":

        try:

            reader = PdfReader(BytesIO(file_contents))
            metadata = reader.metadata

            if metadata:

                metadata_values = [
                    metadata.get("/Author"),
                    metadata.get("/Creator"),
                    metadata.get("/Producer"),
                    metadata.get("/CreationDate"),
                    metadata.get("/ModDate")
                ]

                meaningful_metadata = [
                    value for value in metadata_values
                    if value and str(value).strip()
                ]

                if meaningful_metadata:
                    checks["metadata"] = "present"
                else:
                    checks["metadata"] = "warning"

                    warnings.append(
                        "The PDF contains little or no useful metadata."
                    )

            else:

                checks["metadata"] = "warning"

                warnings.append(
                    "The PDF does not contain metadata."
                )

        except Exception:

            checks["metadata"] = "not_checked"

    else:

        checks["metadata"] = "not_applicable"

    # 10. Internal consistency checks
    consistency_warnings = []

    if extracted_text:

        # 10A. Check dates
        date_patterns = [
            r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
            r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b"
        ]

        dates_found = []

        for pattern in date_patterns:
            matches = re.findall(
                pattern,
                extracted_text,
                re.IGNORECASE
            )

            for match in matches:
                if isinstance(match, tuple):
                    dates_found.append(" ".join(match))
                else:
                    dates_found.append(match)

        # Remove duplicates
        dates_found = list(dict.fromkeys(dates_found))

        # 10B. Check amounts
        amount_patterns = [
            r"(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d{1,2})?",
            r"\b\d[\d,]*\s*(?:rupees|Rs\.?)\b"
        ]

        amounts_found = []

        for pattern in amount_patterns:
            matches = re.findall(
                pattern,
                extracted_text,
                re.IGNORECASE
            )

            amounts_found.extend(matches)

        amounts_found = list(dict.fromkeys(amounts_found))

        # 10C. Check document/reference numbers
        reference_patterns = [
            r"\bnotice\s*(?:number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+",
            r"\bapplication\s*(?:number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+",
            r"\b(reference|ref\.?)\s*(?:number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+",
            r"\bregistration\s*(?:number|no\.?)\s*[:\-]?\s*[A-Z0-9\-\/]+"
        ]

        references_found = []

        for pattern in reference_patterns:
            matches = re.findall(
                pattern,
                extracted_text,
                re.IGNORECASE
            )

            for match in matches:
                if isinstance(match, tuple):
                    references_found.append(" ".join(match))
                else:
                    references_found.append(match)

        references_found = list(dict.fromkeys(references_found))

        # 10D. Detect repeated conflicting amounts
        normalized_amounts = []

        for amount in amounts_found:
            numbers = re.sub(r"[^\d]", "", amount)

            if numbers:
                normalized_amounts.append(numbers)

        unique_amounts = list(dict.fromkeys(normalized_amounts))

        if len(unique_amounts) > 1:
            consistency_warnings.append(
                "Multiple different monetary amounts were detected."
            )

        # 10E. Detect repeated conflicting reference numbers
        if len(references_found) > 1:
            normalized_references = [
                re.sub(
                    r"\s+",
                    " ",
                    reference.lower()
                ).strip()
                for reference in references_found
            ]

            if len(set(normalized_references)) > 1:
                consistency_warnings.append(
                    "Multiple different document or reference numbers were detected."
                )

        # 10F. Basic date sanity check
        if len(dates_found) > 1:

            years = []

            for date in dates_found:

                year_match = re.search(
                    r"\b(19|20)\d{2}\b",
                    date
                )

                if year_match:
                    years.append(
                        int(year_match.group(0))
                    )

            if years:

                min_year = min(years)
                max_year = max(years)

                if max_year - min_year > 10:
                    consistency_warnings.append(
                        "The document contains dates spanning an unusually large time period."
                    )

        if consistency_warnings:

            checks["internal_consistency"] = "warning"
            warnings.extend(consistency_warnings)

        else:

            checks["internal_consistency"] = "passed"

    else:

        checks["internal_consistency"] = "not_checked"    

    # 11. Visual tampering check
    if content_type == "application/pdf":

        try:
            pdf_document = fitz.open(
                stream=file_contents,
                filetype="pdf"
            )

            visual_warning = False

            for page in pdf_document:

                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(1.5, 1.5)
                )

                image_array = np.frombuffer(
                    pixmap.samples,
                    dtype=np.uint8
                )

                channels = pixmap.n

                if channels == 4:

                    image_data = image_array.reshape(
                        pixmap.height,
                        pixmap.width,
                        4
                    )

                    image_data = cv2.cvtColor(
                        image_data,
                        cv2.COLOR_RGBA2GRAY
                    )

                else:

                    image_data = image_array.reshape(
                        pixmap.height,
                        pixmap.width,
                        channels
                    )

                    if channels == 3:
                        image_data = cv2.cvtColor(
                            image_data,
                            cv2.COLOR_RGB2GRAY
                        )

                # Look for unusually strong local edges.
                edges = cv2.Canny(
                    image_data,
                    100,
                    200
                )

                edge_ratio = (
                    np.count_nonzero(edges)
                    / edges.size
                )

                # Extremely unusual edge density can indicate
                # overlays, pasted regions, or image artifacts.
                if edge_ratio > 0.35:
                    visual_warning = True
                    break

            pdf_document.close()

            if visual_warning:
                checks["visual_tampering"] = "warning"

                warnings.append(
                    "The document contains unusual visual patterns that may require manual review."
                )

            else:
                checks["visual_tampering"] = "no_obvious_issue"

        except Exception:

            checks["visual_tampering"] = "not_checked"

    elif content_type in [
        "image/jpeg",
        "image/png"
    ]:

        try:

            image_array = np.frombuffer(
                file_contents,
                dtype=np.uint8
            )

            image_data = cv2.imdecode(
                image_array,
                cv2.IMREAD_GRAYSCALE
            )

            if image_data is not None:

                edges = cv2.Canny(
                    image_data,
                    100,
                    200
                )

                edge_ratio = (
                    np.count_nonzero(edges)
                    / edges.size
                )

                if edge_ratio > 0.35:

                    checks["visual_tampering"] = "warning"

                    warnings.append(
                        "The image contains unusual visual patterns that may require manual review."
                    )

                else:

                    checks["visual_tampering"] = "no_obvious_issue"

            else:

                checks["visual_tampering"] = "not_checked"

        except Exception:

            checks["visual_tampering"] = "not_checked"

    else:

        checks["visual_tampering"] = "not_applicable"  

    # 12. Official-source cross-check
    if extracted_text:

        official_source_found = False
        suspicious_source_found = False

        # Find URLs written inside the document
        url_pattern = r"https?://[^\s<>\"]+|www\.[^\s<>\"]+"

        urls_found = re.findall(
            url_pattern,
            extracted_text,
            re.IGNORECASE
        )

        for url in urls_found:

            url_lower = url.lower()

            # Official Indian government domains
            if (
                ".gov.in" in url_lower
                or ".nic.in" in url_lower
            ):
                official_source_found = True

            # Common suspicious/non-government domains
            elif (
                ".com" in url_lower
                or ".net" in url_lower
                or ".org" in url_lower
            ):
                suspicious_source_found = True

        if official_source_found and not suspicious_source_found:

            checks["official_source"] = "official_domain_found"

        elif suspicious_source_found and not official_source_found:

            checks["official_source"] = "non_official_domain"

            warnings.append(
                "The document contains a web address that is not a recognized Indian government domain."
            )

        elif official_source_found and suspicious_source_found:

            checks["official_source"] = "mixed_domains"

            warnings.append(
                "The document contains both official and non-government web addresses."
            )

        else:

            checks["official_source"] = "not_found"

    else:

        checks["official_source"] = "not_checked"      

    # 13. Final status
    if (
        checks["file_size"] == "failed"
        or checks["pdf_structure"] == "failed"
        or checks["file_type"] == "Unknown"
    ):

        status = "suspicious"

    else:

        status = "uncertain"

    return {
        "status": status,
        "checks": checks,
        "text_length": extracted_text_length,
        "warnings": warnings
    }