from pathlib import Path
from datetime import datetime, timedelta
# cryptography is optional for the prototype; this implementation will try to import it,
# and if unavailable, will create minimal placeholder files (not recommended for real use)
try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False

def ensure_local_cert(base_dir: Path):
    cert_file = base_dir / "cert.pem"
    key_file = base_dir / "key.pem"
    if cert_file.exists() and key_file.exists():
        return cert_file, key_file
    if HAS_CRYPTO:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
            key.public_key()
        ).serial_number(x509.random_serial_number()).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False
        ).sign(key, hashes.SHA256())
        cert_file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        key_file.write_bytes(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        return cert_file, key_file
    else:
        # fallback: write minimal insecure cert placeholder (NOT secure; for prototype only)
        cert_file.write_text("""-----BEGIN CERTIFICATE-----\nMIID...placeholder...\n-----END CERTIFICATE-----\n""")
        key_file.write_text("""-----BEGIN RSA PRIVATE KEY-----\nMIIE...placeholder...\n-----END RSA PRIVATE KEY-----\n""")
        return cert_file, key_file
