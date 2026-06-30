from datetime import datetime
from typing import Any

from lxml import etree


class CAFParserError(Exception):
    pass


class CAFParser:
    """
    Parses the XML CAF (Código de Autorización de Folios) file provided by the SII.
    Extracts the authorization data and the private key used specifically
    to sign the Timbre Electrónico (TED).
    """

    @staticmethod
    def parse(xml_content: bytes) -> dict[str, Any]:
        try:
            root = etree.fromstring(xml_content)
        except etree.XMLSyntaxError as e:
            raise CAFParserError(f"Archivo XML malformado: {str(e)}") from e

        # Namespaces are usually not present in the CAF downloaded from SII,
        # but we handle it just in case

        # 1. Find the <DA> (Datos de Autorización) block
        da_node = root.find(".//DA")
        if da_node is None:
            raise CAFParserError("No se encontró el nodo <DA> en el archivo CAF. Archivo inválido.")

        # 2. Extract basic info
        try:
            rut_emisor = da_node.find("RE").text.strip()
            razon_social = da_node.find("RS").text.strip()
            dte_type = int(da_node.find("TD").text.strip())

            rng_node = da_node.find("RNG")
            folio_from = int(rng_node.find("D").text.strip())
            folio_to = int(rng_node.find("H").text.strip())

            auth_date_str = da_node.find("FA").text.strip()
            auth_date = datetime.strptime(auth_date_str, "%Y-%m-%d").date()

        except (AttributeError, ValueError) as e:
            raise CAFParserError(
                f"Faltan campos obligatorios en el nodo <DA> o tienen un formato inválido: {str(e)}"
            ) from e

        # 3. Find the Private Key <RSASK>
        rsask_node = root.find(".//RSASK")
        if rsask_node is None or not rsask_node.text:
            raise CAFParserError(
                "No se encontró la Llave Privada <RSASK> en el archivo CAF. "
                "Asegúrate de descargar el archivo completo desde el portal del SII."
            )

        private_key = rsask_node.text.strip()

        # 4. Extract the entire <CAF> block exactly as is, because this block must be injected
        # directly into the <TED> of the DTE later.
        caf_node = root.find(".//CAF")
        if caf_node is None:
            raise CAFParserError("No se encontró el nodo <CAF>.")

        # We store the CAF node as a string to easily inject it into the DTEBuilder later
        caf_xml_string = etree.tostring(caf_node, encoding="unicode", method="xml")

        return {
            "rut_emisor": rut_emisor,
            "razon_social": razon_social,
            "dte_type": dte_type,
            "folio_from": folio_from,
            "folio_to": folio_to,
            "authorization_date": auth_date,
            "private_key": private_key,
            "caf_xml_content": caf_xml_string,
        }
