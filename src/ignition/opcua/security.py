"""OPC-UA Security Management

Handles certificates, encryption, and security policies for OPC-UA connections.
"""

import datetime
import ipaddress
import logging
from pathlib import Path
from typing import Any

from asyncua import Client
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages OPC-UA security including certificates and encryption."""

    def __init__(self, client: Client):
        """Initialize security manager.

        Args:
            client: AsyncUA client instance
        """
        self.client = client
        self.certificates_dir = Path.home() / ".ignition" / "opcua" / "certificates"
        self.certificates_dir.mkdir(parents=True, exist_ok=True)

    async def configure_security(self, **kwargs) -> None:
        """Configure client security settings.

        Args:
            **kwargs: Security configuration options:
                - username: Username for authentication
                - password: Password for authentication
                - certificate: Client certificate path
                - private_key: Private key path
                - security_policy: Security policy name
                - security_mode: Security mode
                - application_uri: Application URI
        """
        try:
            # Username/password authentication
            username = kwargs.get("username")
            password = kwargs.get("password")

            if username and password:
                self.client.set_user(username)
                self.client.set_password(password)
                logger.debug("Configured username/password authentication")

            # Certificate-based authentication
            certificate_path = kwargs.get("certificate")
            private_key_path = kwargs.get("private_key")

            if certificate_path and private_key_path:
                await self._configure_certificates(certificate_path, private_key_path)

            # Security policy and mode
            security_policy = kwargs.get("security_policy")
            security_mode = kwargs.get("security_mode")

            if security_policy:
                security_string = f"{security_policy}"
                if security_mode:
                    security_string += f",{security_mode}"

                self.client.set_security_string(security_string)
                logger.debug("Configured security: %s", security_string)

            # Application URI
            application_uri = kwargs.get("application_uri")
            if application_uri:
                self.client.application_uri = application_uri
                logger.debug("Set application URI: %s", application_uri)

        except Exception as e:
            logger.error("Error configuring security: %s", e)
            raise

    async def _configure_certificates(self, cert_path: str, key_path: str) -> None:
        """Configure client certificates.

        Args:
            cert_path: Path to client certificate
            key_path: Path to private key
        """
        try:
            # Load certificate and private key
            await self.client.load_client_certificate(cert_path)
            await self.client.load_private_key(key_path)

            logger.info("Loaded client certificate: %s", cert_path)

        except Exception as e:
            logger.error("Error loading certificates: %s", e)
            raise

    def generate_self_signed_certificate(
        self,
        common_name: str = "IgnitionOPCUAClient",
        organization: str = "Ignition Tools",
        country: str = "US",
        days_valid: int = 365,
    ) -> tuple[str, str]:
        """Generate a self-signed certificate for OPC-UA client.

        Args:
            common_name: Certificate common name
            organization: Organization name
            country: Country code
            days_valid: Certificate validity period in days

        Returns:
            Tuple of (certificate_path, private_key_path)
        """
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            # Create certificate
            subject = issuer = x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, country),
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
                .not_valid_after(
                    datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)
                )
                .add_extension(
                    x509.SubjectAlternativeName(
                        [
                            x509.DNSName("localhost"),
                            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                        ]
                    ),
                    critical=False,
                )
                .sign(private_key, hashes.SHA256())
            )

            # Save certificate and private key
            cert_path = self.certificates_dir / f"{common_name}_cert.pem"
            key_path = self.certificates_dir / f"{common_name}_key.pem"

            # Write certificate
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            # Write private key
            with open(key_path, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            logger.info("Generated self-signed certificate: %s", cert_path)
            return str(cert_path), str(key_path)

        except Exception as e:
            logger.error("Error generating certificate: %s", e)
            raise

    def validate_certificate(self, cert_path: str) -> dict[str, Any]:
        """Validate and get information about a certificate.

        Args:
            cert_path: Path to certificate file

        Returns:
            Dictionary with certificate information
        """
        try:
            with open(cert_path, "rb") as f:
                cert_data = f.read()

            cert = x509.load_pem_x509_certificate(cert_data)

            # Extract certificate information
            info = {
                "subject": str(cert.subject),
                "issuer": str(cert.issuer),
                "serial_number": str(cert.serial_number),
                "not_valid_before": cert.not_valid_before.isoformat(),
                "not_valid_after": cert.not_valid_after.isoformat(),
                "is_expired": cert.not_valid_after < datetime.datetime.utcnow(),
                "signature_algorithm": cert.signature_algorithm_oid._name,
                "version": cert.version.name,
            }

            # Check for subject alternative names
            try:
                san_ext = cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                sans = [str(name) for name in san_ext.value]
                info["subject_alternative_names"] = sans
            except x509.ExtensionNotFound:
                info["subject_alternative_names"] = []

            return info

        except Exception as e:
            logger.error("Error validating certificate %s: %s", cert_path, e)
            return {"error": str(e)}

    def list_available_certificates(self) -> list[dict[str, Any]]:
        """List all available certificates in the certificates directory.

        Returns:
            List of certificate information
        """
        certificates = []

        try:
            for cert_file in self.certificates_dir.glob("*_cert.pem"):
                cert_info = self.validate_certificate(str(cert_file))
                cert_info["file_path"] = str(cert_file)
                cert_info["file_name"] = cert_file.name

                # Look for corresponding private key
                key_file = cert_file.parent / cert_file.name.replace(
                    "_cert.pem", "_key.pem"
                )
                cert_info["has_private_key"] = key_file.exists()
                if cert_info["has_private_key"]:
                    cert_info["private_key_path"] = str(key_file)

                certificates.append(cert_info)

        except Exception as e:
            logger.error("Error listing certificates: %s", e)

        return certificates

    def get_available_security_policies(self) -> list[str]:
        """Get list of available security policies.

        Returns:
            List of security policy names
        """
        return [
            "None",
            "Basic128Rsa15",
            "Basic256",
            "Basic256Sha256",
            "Aes128_Sha256_RsaOaep",
            "Aes256_Sha256_RsaPss",
        ]

    def get_available_security_modes(self) -> list[str]:
        """Get list of available security modes.

        Returns:
            List of security mode names
        """
        return [
            "None",
            "Sign",
            "SignAndEncrypt",
        ]

    def create_security_configuration(
        self,
        policy: str = "Basic256Sha256",
        mode: str = "SignAndEncrypt",
        generate_cert: bool = True,
    ) -> dict[str, Any]:
        """Create a complete security configuration.

        Args:
            policy: Security policy name
            mode: Security mode
            generate_cert: Whether to generate certificate if not exists

        Returns:
            Complete security configuration
        """
        config = {
            "security_policy": policy,
            "security_mode": mode,
            "application_uri": f"urn:ignition:opcua:client:{datetime.datetime.now().strftime('%Y%m%d')}",
        }

        if policy != "None" and generate_cert:
            # Check for existing certificate
            existing_certs = self.list_available_certificates()

            if existing_certs and not existing_certs[0].get("is_expired", True):
                # Use existing certificate
                cert_info = existing_certs[0]
                config["certificate"] = cert_info["file_path"]
                config["private_key"] = cert_info.get("private_key_path")
                logger.info("Using existing certificate: %s", cert_info["file_name"])
            else:
                # Generate new certificate
                cert_path, key_path = self.generate_self_signed_certificate()
                config["certificate"] = cert_path
                config["private_key"] = key_path
                logger.info("Generated new certificate for security configuration")

        return config

    def export_certificate_info(self, output_path: str) -> None:
        """Export certificate information to a file.

        Args:
            output_path: Path to output file
        """
        try:
            import json

            certificates = self.list_available_certificates()

            with open(output_path, "w") as f:
                json.dump(certificates, f, indent=2, default=str)

            logger.info("Exported certificate info to: %s", output_path)

        except Exception as e:
            logger.error("Error exporting certificate info: %s", e)
            raise
