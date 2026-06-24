# PDF Generation

We support multiple renderers depending on the user's need for customization vs precision.

1. **xhtml2pdf Renderer**: Our default. Compiles `jinja2` HTML/CSS templates into PDFs. Very flexible for styling custom logos, colors, and tabular data.
2. **ReportLab Renderer**: A fallback structured layout engine built using Platypus Flowables. Excellent for strictly rigid tabular structures.

## Timbre Electrónico (TED)
The PDF generator extracts the `<TED>` XML segment from the Signed DTE XML payload. It then encodes this exact string into a PDF417 matrix barcode using `pdf417gen`, outputs it as a Base64 PNG image, and injects it into the rendering template.
