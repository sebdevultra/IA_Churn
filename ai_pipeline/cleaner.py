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
    Sanitizador de texto y scrubber de datos sensibles (PII, financieros, técnicos y telemétricos).
    Enmascara información personal y confidencial antes de que sea procesada por
    cualquier modelo de IA (local o cloud).
    """

    def __init__(self):
        # 1. Correos Electrónicos
        self.re_email = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            re.IGNORECASE
        )

        # 2. URLs y Parámetros Web
        self.re_url = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*',
            re.IGNORECASE
        )

        # 3. JWT Tokens y Hashes de Autenticación
        self.re_tokens = re.compile(
            r'\b(?:TOKEN:|Bearer\s+)?(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+)\b|(?:\b0x[0-9A-Fa-f_]+(?:_[A-Za-z0-9_]+)+\b)',
            re.IGNORECASE
        )

        # 4. Tarjetas de Crédito / Débito (13 a 19 dígitos agrupados o continuos)
        self.re_credit_card = re.compile(
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11}|(?:[0-9]{4}[-\s]){3}[0-9]{4}|[0-9]{15,16})\b'
        )

        # 5. Códigos CVC / CVV / PIN
        self.re_cvc = re.compile(
            r'\b(?:CVC|CVV|CCV|PIN|código de seguridad)[\s:#-]*([0-9]{3,4})\b',
            re.IGNORECASE
        )

        # 6. Cuentas Bancarias / IBAN / BIC / SWIFT / CLABE
        self.re_bank_account = re.compile(
            r'\b(?:IBAN[-:\s]*[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}|BIC[-:\s]*[A-Z0-9]{8,11})\b|(?:\b(?:cuenta(?: de ahorros| corriente)?|cta[\s.]?cte|No\. de cuenta)[\s:#.]*(?:No\.?[\s:#.]*)?)([0-9]{8,20})\b',
            re.IGNORECASE
        )

        # 7. Documentos de Identidad Internacionales (Cédula, DNI, NIT, RUT, RFC, CURP, NSS, CPF, RG, SSN, Passport)
        self.re_id_docs = re.compile(
            r'\b(?:PASSPORT|Pasaporte|CURP|RFC|NSS|CPF|RG|SSN|DNI|RUT|NIT|CC|C\.C\.|C[eé]dula(?: de ciudadan[ií]a)?|ID|UID|USER)[\s:#.-]*(?:No\.?[\s:#.-]*)?([A-Za-z0-9.-]{4,25}(?:-[0-9kK])?)\b',
            re.IGNORECASE
        )

        # 8. Direcciones IP y MAC / Puertos
        self.re_network = re.compile(
            r'\b(?:IP:)?(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\b(?:MAC:)?(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b|\bPORT:[0-9]{2,5}\b',
            re.IGNORECASE
        )

        # 9. Coordenadas Geográficas y Telemetría
        self.re_geo = re.compile(
            r'\b(?:LAT|LON|ALT|GEO|LOC_ID)[\s:#.-]*-?[0-9.]+(?:-[A-Z0-9_]+)?\b',
            re.IGNORECASE
        )

        # 10. Teléfonos (formatos internacionales, colombianos y estándar)
        self.re_phone = re.compile(
            r'(?:\+?57[\s.-]?)?(?:\(?\b(?:3[0-9]{2}|60[1-8]|[1-9][0-9]{1,2})\)?[\s.-]?)?[0-9]{3}[\s.-]?[0-9]{4}\b'
        )

        # 11. Secretos, Passwords, API Keys, RSA Keys, Tokens
        self.re_secrets = re.compile(
            r'-----BEGIN[A-Z\s]+PRIVATE KEY-----[^-]+-----END[A-Z\s]+PRIVATE KEY-----|\b(?:password|contrase[nñ]a|clave(?:_dinamica)?|token|api[_-]?key|bearer|secret|pass(?:word)?)[\s:=]+([A-Za-z0-9_\-.~+/=$%#@!]{4,})\b|\b(?:sk_live_[A-Za-z0-9]{6,}|sk_prod_[A-Za-z0-9]{6,}|amzn_[A-Za-z0-9_]{6,}|TempPass[A-Za-z0-9$%#@!]+|Admin[0-9]{4,})\b',
            re.IGNORECASE
        )



        # 12. Nombres Propios tras presentación
        self.re_names = re.compile(
            r'\b(?:mi nombre es|me llamo|atentamente|saludos de(?: parte de)?|Titular:|Soy)[\s:]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,2})\b',
            re.IGNORECASE
        )


        # 13. Direcciones Físicas
        self.re_address = re.compile(
            r'\b(?:Calle|Cll|Carrera|Cra|Cr|Avenida|Av|Diag|Diagonal|Transversal|Tv|Circular|Cq)[\s.]+[0-9A-Za-z\s#º°-]+(?:#[0-9A-Za-z\s-]+)?\b',
            re.IGNORECASE
        )

        # 14. Logs y Tags de Sistema
        self.re_system_tags = re.compile(
            r'\[(?:CRITICAL_FAILURE|SYS_LOG_[0-9]+|ERR_[A-Z0-9_]+|LOG_METADATA:[^\]]+|CRON_JOB_ID:[^\]]+|STACK_TRACE:[^\]]+|ALERT_[A-Z0-9_]+)\]|\bAWS_ARN:[^\s]+|\bDB_QUERY:[^\s]+|\bERROR_CODE:[^\s]+|\bJSON_STRING:\{[^\}]+\}',
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

        normalized = unicodedata.normalize('NFC', text)
        normalized = self.re_control_chars.sub('', normalized)
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

        # 1. URLs
        def repl_url(m):
            breakdown["urls"] = breakdown.get("urls", 0) + 1
            return "[URL_MASKED]"
        current_text = self.re_url.sub(repl_url, current_text)

        # 2. Tokens y Hashes
        def repl_tokens(m):
            breakdown["tokens_hashes"] = breakdown.get("tokens_hashes", 0) + 1
            return "[TOKEN_MASKED]"
        current_text = self.re_tokens.sub(repl_tokens, current_text)

        # 3. Logs y Tags de Sistema
        def repl_logs(m):
            breakdown["system_logs"] = breakdown.get("system_logs", 0) + 1
            return "[LOG_MASKED]"
        current_text = self.re_system_tags.sub(repl_logs, current_text)

        # 4. Secretos y Credenciales
        def repl_secret(m):
            breakdown["secrets"] = breakdown.get("secrets", 0) + 1
            if m.group(1):
                prefix = m.group(0).split(m.group(1))[0]
                return f"{prefix}[SECRET_MASKED]"
            return "[SECRET_MASKED]"
        current_text = self.re_secrets.sub(repl_secret, current_text)


        # 5. CVC / CVV / CCV
        def repl_cvc(m):
            breakdown["cvc"] = breakdown.get("cvc", 0) + 1
            prefix = m.group(0).split(m.group(1))[0]
            return f"{prefix}[CVC_MASKED]"
        current_text = self.re_cvc.sub(repl_cvc, current_text)

        # 6. Tarjetas de Crédito
        def repl_card(m):
            breakdown["credit_cards"] = breakdown.get("credit_cards", 0) + 1
            return "[CARD_NUMBER_MASKED]"
        current_text = self.re_credit_card.sub(repl_card, current_text)

        # 7. Cuentas Bancarias / IBAN / BIC
        def repl_bank(m):
            breakdown["bank_accounts"] = breakdown.get("bank_accounts", 0) + 1
            full_match = m.group(0)
            if m.group(1): # Grupo con número de cuenta
                prefix = full_match.split(m.group(1))[0]
                return f"{prefix}[BANK_ACCOUNT_MASKED]"
            return "[BANK_ACCOUNT_MASKED]"
        current_text = self.re_bank_account.sub(repl_bank, current_text)

        # 8. Documentos de Identidad (Nacionales e Internacionales)
        def repl_id(m):
            breakdown["id_documents"] = breakdown.get("id_documents", 0) + 1
            prefix = m.group(0).split(m.group(1))[0]
            return f"{prefix}[ID_DOC_MASKED]"
        current_text = self.re_id_docs.sub(repl_id, current_text)

        # 9. Correos Electrónicos
        def repl_email(m):
            breakdown["emails"] = breakdown.get("emails", 0) + 1
            return "[EMAIL_MASKED]"
        current_text = self.re_email.sub(repl_email, current_text)

        # 10. Redes (IP, MAC, Puerto)
        def repl_net(m):
            breakdown["network_identifiers"] = breakdown.get("network_identifiers", 0) + 1
            return "[IP_MASKED]"
        current_text = self.re_network.sub(repl_net, current_text)

        # 11. Coordenadas Geográficas
        def repl_geo(m):
            breakdown["telemetry_geo"] = breakdown.get("telemetry_geo", 0) + 1
            return "[GEO_MASKED]"
        current_text = self.re_geo.sub(repl_geo, current_text)

        # 12. Nombres Propios
        def repl_name(m):
            breakdown["names"] = breakdown.get("names", 0) + 1
            prefix = m.group(0).split(m.group(1))[0]
            return f"{prefix}[NAME_MASKED]"
        current_text = self.re_names.sub(repl_name, current_text)

        # 13. Direcciones Físicas
        def repl_address(m):
            breakdown["addresses"] = breakdown.get("addresses", 0) + 1
            return "[ADDRESS_MASKED]"
        current_text = self.re_address.sub(repl_address, current_text)

        # 14. Teléfonos
        def repl_phone(m):
            breakdown["phones"] = breakdown.get("phones", 0) + 1
            return "[PHONE_MASKED]"
        current_text = self.re_phone.sub(repl_phone, current_text)

        # Limpiar tags duplicados contiguos
        current_text = re.sub(r'(\[(?:ID_DOC|TOKEN|IP|GEO|BANK_ACCOUNT|LOG)_MASKED\][\s:-]*){2,}', r'\1', current_text)
        current_text = self.re_multiple_spaces.sub(' ', current_text).strip()

        total_masked = sum(breakdown.values())
        was_modified = total_masked > 0 or current_text != text

        return PIICleanResult(
            original_text=text,
            cleaned_text=current_text,
            pii_breakdown=breakdown,
            total_pii_masked=total_masked,
            was_modified=was_modified
        )
