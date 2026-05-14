from __future__ import annotations

from enum import StrEnum


class SiiXmlNamespaces(StrEnum):
    DTE = "http://www.sii.cl/SiiDte"
    DSIG = "http://www.w3.org/2000/09/xmldsig#"


class XmlBuildMode(StrEnum):
    UNSIGNED = "unsigned"
    SIGNED_READY = "signed_ready"
