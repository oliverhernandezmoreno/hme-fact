from datetime import datetime

from lxml import etree


class DTEBuilder:
    """
    Builds the DTE XML Structure according to SII formatting rules.
    """

    @staticmethod
    def _create_element(
        parent: etree._Element, tag: str, text: str | int | float = None
    ) -> etree._Element:
        element = etree.SubElement(parent, tag)
        if text is not None:
            element.text = str(text)
        return element

    @staticmethod
    def build_dte_xml(dte_data: dict, timbre_firma: str = None) -> etree._Element:
        """
        Builds the base XML tree for a standard DTE (Factura o Boleta).
        """
        nsmap = {None: "http://www.sii.cl/SiiDte"}

        root = etree.Element("DTE", version="1.0", nsmap=nsmap)
        documento = etree.SubElement(root, "Documento", ID=f"DOC_{dte_data['folio']}")

        # 1. Encabezado
        encabezado = etree.SubElement(documento, "Encabezado")

        id_doc = etree.SubElement(encabezado, "IdDoc")
        DTEBuilder._create_element(id_doc, "TipoDTE", dte_data["dte_type"])
        DTEBuilder._create_element(id_doc, "Folio", dte_data["folio"])
        DTEBuilder._create_element(id_doc, "FchEmis", dte_data["issue_date"])

        # Emisor
        emisor = etree.SubElement(encabezado, "Emisor")
        DTEBuilder._create_element(emisor, "RUTEmisor", dte_data["emisor"]["rut"])
        DTEBuilder._create_element(emisor, "RznSoc", dte_data["emisor"]["legal_name"])
        DTEBuilder._create_element(emisor, "GiroEmis", dte_data["emisor"]["giro"])
        DTEBuilder._create_element(emisor, "Acteco", dte_data["emisor"]["acteco"])
        DTEBuilder._create_element(emisor, "DirOrigen", dte_data["emisor"]["address"])
        DTEBuilder._create_element(emisor, "CmnaOrigen", dte_data["emisor"]["comuna"])

        # Receptor
        receptor = etree.SubElement(encabezado, "Receptor")
        DTEBuilder._create_element(receptor, "RUTRecep", dte_data["receptor"]["rut"])
        DTEBuilder._create_element(receptor, "RznSocRecep", dte_data["receptor"]["legal_name"])
        DTEBuilder._create_element(receptor, "GiroRecep", dte_data["receptor"]["giro"])
        DTEBuilder._create_element(receptor, "DirRecep", dte_data["receptor"]["address"])
        DTEBuilder._create_element(receptor, "CmnaRecep", dte_data["receptor"]["comuna"])

        # Totales
        totales = etree.SubElement(encabezado, "Totales")
        DTEBuilder._create_element(totales, "MntNeto", dte_data["totales"]["neto"])
        if dte_data["totales"].get("exento"):
            DTEBuilder._create_element(totales, "MntExe", dte_data["totales"]["exento"])
        DTEBuilder._create_element(totales, "TasaIVA", 19)
        DTEBuilder._create_element(totales, "IVA", dte_data["totales"]["iva"])
        DTEBuilder._create_element(totales, "MntTotal", dte_data["totales"]["total"])

        # 2. Detalles (Items)
        for i, item in enumerate(dte_data["items"], start=1):
            detalle = etree.SubElement(documento, "Detalle")
            DTEBuilder._create_element(detalle, "NroLinDet", i)
            if item.get("tax_exempt"):
                DTEBuilder._create_element(detalle, "IndExe", 1)
            DTEBuilder._create_element(detalle, "NmbItem", item["name"])
            DTEBuilder._create_element(detalle, "QtyItem", item["quantity"])
            DTEBuilder._create_element(detalle, "PrcItem", item["unit_price"])
            DTEBuilder._create_element(detalle, "MontoItem", item["total_amount"])

        # 3. Referencias (Opcional, e.g. Nota de Credito)
        if dte_data.get("referencias"):
            for i, ref in enumerate(dte_data["referencias"], start=1):
                referencia = etree.SubElement(documento, "Referencia")
                DTEBuilder._create_element(referencia, "NroLinRef", i)
                DTEBuilder._create_element(referencia, "TpoDocRef", ref["dte_type"])
                DTEBuilder._create_element(referencia, "FolioRef", ref["folio"])
                DTEBuilder._create_element(referencia, "FchRef", ref["date"])
                DTEBuilder._create_element(referencia, "CodRef", ref["code"])
                DTEBuilder._create_element(referencia, "RazonRef", ref["reason"])

        # 4. Timbre (TED)
        if timbre_firma:
            ted = etree.SubElement(documento, "TED", version="1.0")
            # DD represents Datos del Documento (what gets hashed)
            dd = etree.SubElement(ted, "DD")
            DTEBuilder._create_element(dd, "RE", dte_data["emisor"]["rut"])
            DTEBuilder._create_element(dd, "TD", dte_data["dte_type"])
            DTEBuilder._create_element(dd, "F", dte_data["folio"])
            DTEBuilder._create_element(dd, "FE", dte_data["issue_date"])
            DTEBuilder._create_element(dd, "RR", dte_data["receptor"]["rut"])
            DTEBuilder._create_element(dd, "RSR", dte_data["receptor"]["legal_name"][:40])
            DTEBuilder._create_element(dd, "MNT", dte_data["totales"]["total"])

            # The CAF part
            if "caf_xml" in dte_data:
                # Append raw CAF XML element into DD (extract CAF if embedded in AUTORIZACION)
                caf_element = etree.fromstring(dte_data["caf_xml"])
                if caf_element.tag == "AUTORIZACION":
                    caf_node = caf_element.find("CAF")
                    if caf_node is not None:
                        dd.append(caf_node)
                    else:
                        dd.append(caf_element)
                else:
                    dd.append(caf_element)

            DTEBuilder._create_element(dd, "TSTED", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

            # The signature of the DD node goes here
            frma = etree.SubElement(ted, "FRMA", algoritmo="SHA1withRSA")
            frma.text = timbre_firma

        return root
