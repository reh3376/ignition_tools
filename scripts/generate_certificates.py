#!/usr/bin/env python3
"""
Generate OPC-UA Client Certificates
Standalone certificate generation for secure OPC-UA connections
"""

import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def generate_opcua_certificates():
    """Generate self-signed certificates for OPC-UA client."""

    print("🔐 Generating OPC-UA Client Certificates")
    print("=" * 40)

    # Create certificates directory
    cert_dir = Path.home() / ".ignition" / "opcua" / "certificates"
    cert_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Certificate directory: {cert_dir}")

    try:
        # Generate private key
        print("🔑 Generating private key...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create certificate
        print("📜 Creating certificate...")
        common_name = "IgnitionOPCUA-Client"
        organization = "IGN-Scripts"

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                        x509.DNSName("IgnitionOPCUA-Client"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # Save certificate and private key
        cert_path = cert_dir / f"{common_name}_cert.pem"
        key_path = cert_dir / f"{common_name}_key.pem"

        print("💾 Saving certificate...")
        # Write certificate
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print("💾 Saving private key...")
        # Write private key
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        print("✅ Certificates generated successfully!")
        print(f"   Certificate: {cert_path}")
        print(f"   Private Key: {key_path}")

        return {
            "certificate_path": str(cert_path),
            "private_key_path": str(key_path),
            "common_name": common_name,
            "organization": organization,
        }

    except Exception as e:
        print(f"❌ Certificate generation failed: {e}")
        return None


if __name__ == "__main__":
    result = generate_opcua_certificates()
    if result:
        print("\n🎉 Ready for secure OPC-UA connections!")
    else:
        print("\n❌ Certificate generation failed!")
