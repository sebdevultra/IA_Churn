"""
Módulo de Limpieza, Normalización y Anonimización de Datos Sensibles (PII Scrubber).
Garantiza el cumplimiento normativo (Habeas Data, GDPR) y optimiza el consumo de tokens.
"""

import re
import unicodedata
from typing import Dict
from .schemas import PIICleanResult


class TextCleanerAndPIIScrubber:
    """
    Sanitizador de texto y scrubber de datos sensibles (PII y datos financieros).
    Enmascara información personal y confidencial antes de que sea procesada por
    cualquier modelo de IA (local o cloud).
    """

    def __init__(self):
        # 1. Correos Electrónicos
        self.re_email = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            re.IGNORECASE
        )

        # 2. Tarjetas de Crédito / Débito (13 a 19 dígitos agrupados o continuos)
        self.re_credit_card = re.compile(
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11}|(?:[0-9]{4}[-\s]){3}[0-9]{4}|[0-9]{15,16})\b'
        )

        # 3. Códigos CVC / CVV / PIN
        self.re_cvc = re.compile(
            r'\b(?:CVC|CVV|PIN|código de seguridad)[\s:]*([0-9]{3,4})\b',
            re.IGNORECASE
        )

        # 4. Cuentas Bancarias / IBAN / CLABE
        self.re_bank_account = re.compile(
            r'\b(?:IBAN[\s:]*[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}|(?:cuenta(?: de ahorros| corriente)?|cta[\s.]?cte|No\. de cuenta)[\s:#.]*(?:No\.?[\s:#.]*)?[0-9]{8,20})\b',
            re.IGNORECASE
        )

        # 5. Documentos de Identidad (Cédula, DNI, NIT, Pasaporte, SSN)
        self.re_id_docs = re.compile(
            r'\b(?:CC|C\.C\.|C[eé]dula(?: de ciudadan[ií]a)?|DNI|NIT|RUT|Pasaporte|Passport|SSN)[\s:#.-]*(?:No\.?[\s:#.-]*)?([0-9]{6,12}(?:-[0-9kK])?|[0-9]{3}-[0-9]{2}-[0-9]{4})\b',
            re.IGNORECASE
        )

        # 6. Teléfonos (formatos internacionales, colombianos y estándar: +57, 3XX XXX XXXX, fijos 601, etc.)
        self.re_phone = re.compile(
            r'(?:\+?57[\s.-]?)?(?:\(?\b(?:3[0-9]{2}|60[1-8]|[1-9][0-9]{1,2})\)?[\s.-]?)?[0-9]{3}[\s.-]?[0-9]{4}\b'
        )

        # 7. Direcciones IP (IPv4)
        self.re_ip_address = re.compile(
            r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        )

        # 8. Secretos, Passwords, API Keys y Bearer Tokens
        self.re_secrets = re.compile(
            r'\b(?:password|contrase[nñ]a|clave|token|api[_-]?key|bearer|secret)[\s:=]+([A-Za-z0-9_\-.~+/=]{6,})\b',
            re.IGNORECASE
        )

        # 9. Direcciones Físicas (Nomenclatura urbana: Calle, Cra, Carrera, Av, etc.)
        self.re_address = re.compile(
            r'\b(?:Calle|Cll|Carrera|Cra|Cr|Avenida|Av|Diag|Diagonal|Transversal|Tv|Circular|Cq)[\s.]+[0-9A-Za-z\s#º°-]+(?:#[0-9A-Za-z\s-]+)?\b',
            re.IGNORECASE
        )

        # 10. Nombres Propios tras presentación ("Mi nombre es Juan Pérez", "Me llamo Carlos Gómez")
        self.re_names = re.compile(
            r'\b(?:mi nombre es|me llamo|atentamente|saludos de(?: parte de)?)[\s:]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,2})\b',
            re.IGNORECASE
        )

        # Limpieza de caracteres de control
        self.re_control_chars = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')
        self.re_multiple_spaces = re.compile(r'[ \t]+')
        self.re_multiple_newlines = re.compile(r'\n{3,}')

    def normalize_text(self, text: str) -> str:
        """
        Normaliza codificación unicode, remueve caracteres no imprimibles
        y reduce espacios en blanco excesivos.
        """
        if not text:
            return ""

        # Normalización Unicode
        normalized = unicodedata.normalize('NFC', text)

        # Remover caracteres de control invisibles
        normalized = self.re_control_chars.sub('', normalized)

        # Limpiar espacios repetidos y saltos excesivos
        normalized = self.re_multiple_spaces.sub(' ', normalized)
        normalized = self.re_multiple_newlines.sub('\n\n', normalized)

        return normalized.strip()

    def scrub_pii(self, text: str) -> PIICleanResult:
        """
        Ejecuta el enmascaramiento exhaustivo de todas las entidades de datos sensibles.
        Retorna el objeto PIICleanResult con el texto saneado y la auditoría de sustituciones.
        """
        if not text or not text.strip():
            return PIICleanResult(
                original_text=text if text is not None else "",
                cleaned_text="",
                pii_breakdown={},
                total_pii_masked=0,
                was_modified=False
            )

        original_clean = self.normalize_text(text)
        current_text = original_clean
        breakdown: Dict[str, int] = {}

        # 1. Secretos y Credenciales
        def repl_secret(m):
            breakdown["secrets"] = breakdown.get("secrets", 0) + 1
            prefix = m.group(0).split(m.group(1))[0]
            return f"{prefix}[SECRET_MASKED]"
        current_text = self.re_secrets.sub(repl_secret, current_text)

        # 2. CVC / CVV
        def repl_cvc(m):
            breakdown["cvc"] = breakdown.get("cvc", 0) + 1
            prefix = m.group(0).split(m.group(1))[0]
            return f"{prefix}[CVC_MASKED]"
        current_text = self.re_cvc.sub(repl_cvc, current_text)

        # 3. Tarjetas de Crédito
        def repl_card(m):
            breakdown["credit_cards"] = breakdown.get("credit_cards", 0) + 1
            return "[CARD_NUMBER_MASKED]"
        current_text = self.re_credit_card.sub(repl_card, current_text)

        # 4. Cuentas Bancarias (antes de Documentos y Teléfonos)
        def repl_bank(m):
            breakdown["bank_accounts"] = breakdown.get("bank_accounts", 0) + 1
            return "[BANK_ACCOUNT_MASKED]"
        current_text = self.re_bank_account.sub(repl_bank, current_text)

        # 5. Documentos de Identidad (antes de Teléfonos)
        def repl_id(m):
            breakdown["id_documents"] = breakdown.get("id_documents", 0) + 1
            return "[ID_DOC_MASKED]"
        current_text = self.re_id_docs.sub(repl_id, current_text)

        # 6. Correos Electrónicos
        def repl_email(m):
            breakdown["emails"] = breakdown.get("emails", 0) + 1
            return "[EMAIL_MASKED]"
        current_text = self.re_email.sub(repl_email, current_text)

        # 7. Direcciones IP
        def repl_ip(m):
            breakdown["ip_addresses"] = breakdown.get("ip_addresses", 0) + 1
            return "[IP_MASKED]"
        current_text = self.re_ip_address.sub(repl_ip, current_text)

        # 8. Nombres Propios Explícitos
        def repl_name(m):
            breakdown["names"] = breakdown.get("names", 0) + 1
            prefix = m.group(0).split(m.group(1))[0]
            return f"{prefix}[NAME_MASKED]"
        current_text = self.re_names.sub(repl_name, current_text)

        # 9. Direcciones Físicas
        def repl_address(m):
            breakdown["addresses"] = breakdown.get("addresses", 0) + 1
            return "[ADDRESS_MASKED]"
        current_text = self.re_address.sub(repl_address, current_text)

        # 10. Teléfonos
        def repl_phone(m):
            breakdown["phones"] = breakdown.get("phones", 0) + 1
            return "[PHONE_MASKED]"
        current_text = self.re_phone.sub(repl_phone, current_text)

        total_masked = sum(breakdown.values())
        was_modified = total_masked > 0 or current_text != text

        return PIICleanResult(
            original_text=text,
            cleaned_text=current_text,
            pii_breakdown=breakdown,
            total_pii_masked=total_masked,
            was_modified=was_modified
        )
