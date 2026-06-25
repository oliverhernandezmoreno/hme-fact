import base64
from typing import Tuple

import xmlsec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
from lxml import etree


class SIISigner:
    """
    Handles XML-DSig and TED RSA-SHA1 signing for Chilean SII format using `xmlsec` and `cryptography`.
    """

    @staticmethod
    def extract_pem_from_pfx(pfx_data: bytes, password: str) -> Tuple[bytes, bytes]:
        """
        Extracts private key and certificate in PEM format from a PFX/P12 binary file.
        """
        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            pfx_data, password.encode("utf-8")
        )
        if not private_key or not certificate:
            raise ValueError("Invalid PFX data: Missing private key or certificate")

        private_key_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
        cert_pem = certificate.public_bytes(Encoding.PEM)

        return private_key_pem, cert_pem

    @staticmethod
    def sign_ted(dd_node_str: str, private_key_pem: bytes) -> str:
        """
        Signs the <DD> (Datos del Documento) string for the Timbre Electrónico (TED)
        using RSA-SHA1 and returns the base64 encoded signature.
        """
        key = xmlsec.Key.from_memory(private_key_pem, xmlsec.KeyFormat.PEM, None)
        
        # SII requires RSA-SHA1 for the TED signature
        # We use cryptography directly here for the raw string signing
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        priv_key = load_pem_private_key(private_key_pem, password=None)
        
        signature = priv_key.sign(
            dd_node_str.encode('ISO-8859-1'), # SII uses ISO-8859-1 for TED hash
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def sign_xml_dsig(
        xml_element: etree._Element,
        private_key_pem: bytes,
        cert_pem: bytes,
        reference_uri: str = ""
    ) -> etree._Element:
        """
        Applies XML-DSig to an lxml Element using the provided private key and certificate.
        Automatically injects the <Signature> node required by SII.
        """
        # Create Signature Template
        signature_node = xmlsec.template.create(
            xml_element,
            xmlsec.Transform.EXCL_C14N,
            xmlsec.Transform.RSA_SHA1,
        )
        
        # Append signature to the end of the element
        xml_element.append(signature_node)

        # Add Reference
        ref = xmlsec.template.add_reference(
            signature_node,
            xmlsec.Transform.SHA1,
            uri=reference_uri
        )
        
        # SII Requires ENVELOPED transform
        xmlsec.template.add_transform(ref, xmlsec.Transform.ENVELOPED)

        # Add KeyInfo & X509Data
        key_info = xmlsec.template.ensure_key_info(signature_node)
        xmlsec.template.add_x509_data(key_info)
        xmlsec.template.add_key_value(key_info)

        # Create Signature Context
        ctx = xmlsec.SignatureContext()
        
        # Load keys into Context
        key = xmlsec.Key.from_memory(private_key_pem, xmlsec.KeyFormat.PEM, None)
        key.load_cert_from_memory(cert_pem, xmlsec.KeyFormat.PEM)
        ctx.key = key

        # Perform the actual signature
        ctx.sign(signature_node)
        
        return xml_element
