# Certificate Security

SII Certificates (PFX/P12 format) contain the private key of the authorized signer. They are critical security assets.

In Phase 5, certificates are **no longer** stored in plain binary format.

- **AES-256-GCM Encryption**: Both the PFX binary blob and the password string are encrypted using symmetric AES encryption provided by the `cryptography` library.
- **Metadata Extraction**: When a user uploads a certificate, the backend uses `pkcs12.load_key_and_certificates` to open it in memory, extract the `common_name`, `serial_number`, and `valid_until` expiration dates, and stores them in plaintext columns to allow the UI to display the certificate status without decrypting the private key.
