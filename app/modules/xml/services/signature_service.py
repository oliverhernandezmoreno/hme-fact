from __future__ import annotations

from typing import Protocol


class XmlSignatureService(Protocol):
    def sign(self, xml_content: str, *, certificate_alias: str) -> str:
        """Future xmlsec-backed XML signature port."""
        raise NotImplementedError


class XmlsecSignatureService:
    def sign(self, xml_content: str, *, certificate_alias: str) -> str:
        # xmlsec integration lives behind this port so builders stay independent
        # from certificate storage and signing policies.
        raise NotImplementedError("XML signature with xmlsec is prepared but not implemented yet")
