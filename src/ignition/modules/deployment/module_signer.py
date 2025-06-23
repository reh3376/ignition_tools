"""Module Signer for digital signing and security validation of Ignition modules.

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Structured logging and progress tracking
- Security-focused implementation
"""

import logging
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class SigningConfig:
    """Configuration for module signing operations."""

    # Certificate and key paths
    certificate_path: str = field(
        default_factory=lambda: os.getenv("MODULE_SIGNING_CERT_PATH", "")
    )
    private_key_path: str = field(
        default_factory=lambda: os.getenv("MODULE_SIGNING_KEY_PATH", "")
    )
    ca_certificate_path: str = field(
        default_factory=lambda: os.getenv("MODULE_CA_CERT_PATH", "")
    )

    # Signing configuration
    hash_algorithm: str = "SHA256"
    signature_format: str = "PKCS7"
    timestamp_server: str = field(
        default_factory=lambda: os.getenv("TIMESTAMP_SERVER_URL", "")
    )

    # Validation settings
    verify_certificate_chain: bool = True
    check_certificate_expiry: bool = True
    require_timestamp: bool = False

    # Output settings
    output_directory: Path = field(default_factory=lambda: Path("signed"))
    temp_directory: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "ignition-signing"
    )

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.temp_directory.mkdir(parents=True, exist_ok=True)


@dataclass
class SigningResult:
    """Result of a module signing operation."""

    success: bool
    signed_file: Path | None = None
    signature_file: Path | None = None
    certificate_info: dict[str, Any] = field(default_factory=dict)
    signature_timestamp: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    signing_info: dict[str, Any] = field(default_factory=dict)


def validate_certificate_path(cert_path: str) -> dict[str, Any]:
    """Validate certificate path following crawl_mcp.py validation patterns."""
    if not cert_path or not isinstance(cert_path, str):
        return {"valid": False, "error": "Certificate path is required"}

    cert_file = Path(cert_path)
    if not cert_file.exists():
        return {"valid": False, "error": f"Certificate not found: {cert_path}"}

    try:
        # Try to load and validate certificate
        with open(cert_file, "rb") as f:
            cert_data = f.read()

        # Try PEM format first
        try:
            cert = x509.load_pem_x509_certificate(cert_data)
        except ValueError:
            # Try DER format
            try:
                cert = x509.load_der_x509_certificate(cert_data)
            except ValueError:
                return {
                    "valid": False,
                    "error": "Invalid certificate format (not PEM or DER)",
                }

        # Check certificate validity
        now = datetime.now()
        if cert.not_valid_after < now:
            return {"valid": False, "error": "Certificate has expired"}

        if cert.not_valid_before > now:
            return {"valid": False, "error": "Certificate is not yet valid"}

        return {"valid": True, "certificate": cert}

    except Exception as e:
        return {"valid": False, "error": f"Certificate validation error: {e!s}"}


def validate_private_key_path(key_path: str) -> dict[str, Any]:
    """Validate private key path following crawl_mcp.py validation patterns."""
    if not key_path or not isinstance(key_path, str):
        return {"valid": False, "error": "Private key path is required"}

    key_file = Path(key_path)
    if not key_file.exists():
        return {"valid": False, "error": f"Private key not found: {key_path}"}

    try:
        # Try to load private key
        with open(key_file, "rb") as f:
            key_data = f.read()

        # Try PEM format first
        try:
            private_key = serialization.load_pem_private_key(key_data, password=None)
        except ValueError:
            # Try DER format
            try:
                private_key = serialization.load_der_private_key(
                    key_data, password=None
                )
            except ValueError:
                return {
                    "valid": False,
                    "error": "Invalid private key format (not PEM or DER)",
                }

        return {"valid": True, "private_key": private_key}

    except Exception as e:
        return {"valid": False, "error": f"Private key validation error: {e!s}"}


class ModuleSigner:
    """Comprehensive module signer for Ignition modules."""

    def __init__(self, config: SigningConfig) -> None:
        """Initialize module signer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.console = console

    def validate_environment(self) -> dict[str, bool]:
        """Validate signing environment following crawl_mcp.py patterns."""
        validation_results = {
            "certificate_exists": bool(
                self.config.certificate_path
                and Path(self.config.certificate_path).exists()
            ),
            "private_key_exists": bool(
                self.config.private_key_path
                and Path(self.config.private_key_path).exists()
            ),
            "certificate_valid": False,
            "private_key_valid": False,
            "output_directory_writable": self._check_directory_writable(
                self.config.output_directory
            ),
            "temp_directory_writable": self._check_directory_writable(
                self.config.temp_directory
            ),
        }

        # Validate certificate if it exists
        if validation_results["certificate_exists"]:
            cert_validation = validate_certificate_path(self.config.certificate_path)
            validation_results["certificate_valid"] = cert_validation["valid"]

        # Validate private key if it exists
        if validation_results["private_key_exists"]:
            key_validation = validate_private_key_path(self.config.private_key_path)
            validation_results["private_key_valid"] = key_validation["valid"]

        return validation_results

    def sign_module(self, module_file: Path) -> SigningResult:
        """Sign a module file with digital signature."""
        result = SigningResult(
            success=False,
            signed_file=None,
            signature_file=None,
            certificate_info={},
            errors=[],
            warnings=[],
        )

        # Validate inputs
        if not module_file.exists():
            result.errors.append(f"Module file not found: {module_file}")
            return result

        if module_file.suffix.lower() != ".modl":
            result.errors.append(f"Invalid module file extension: {module_file.suffix}")
            return result

        # Validate environment
        env_validation = self.validate_environment()
        missing_requirements = [k for k, v in env_validation.items() if not v]
        if missing_requirements:
            result.warnings.extend(
                [f"Missing requirement: {req}" for req in missing_requirements]
            )

            # Check for critical missing requirements
            critical_missing = [
                req
                for req in missing_requirements
                if req in ["certificate_valid", "private_key_valid"]
            ]
            if critical_missing:
                result.errors.extend(
                    [f"Critical requirement missing: {req}" for req in critical_missing]
                )
                return result

        try:
            self.console.print(f"🔐 Signing module: {module_file.name}")

            # Load certificate and private key
            cert_validation = validate_certificate_path(self.config.certificate_path)
            key_validation = validate_private_key_path(self.config.private_key_path)

            if not cert_validation["valid"]:
                result.errors.append(
                    f"Certificate validation failed: {cert_validation['error']}"
                )
                return result

            if not key_validation["valid"]:
                result.errors.append(
                    f"Private key validation failed: {key_validation['error']}"
                )
                return result

            certificate = cert_validation["certificate"]
            private_key = key_validation["private_key"]

            # Create signed module file
            signed_filename = f"{module_file.stem}-signed{module_file.suffix}"
            signed_file = self.config.output_directory / signed_filename

            # Create module signature
            signature_result = self._create_module_signature(
                module_file, certificate, private_key
            )
            if not signature_result["success"]:
                result.errors.extend(signature_result["errors"])
                return result

            # Copy module file to signed location
            import shutil

            shutil.copy2(module_file, signed_file)

            # Save signature file
            signature_filename = f"{module_file.stem}-signature.sig"
            signature_file = self.config.output_directory / signature_filename

            with open(signature_file, "wb") as f:
                f.write(signature_result["signature"])

            # Extract certificate information
            cert_info = self._extract_certificate_info(certificate)

            result.success = True
            result.signed_file = signed_file
            result.signature_file = signature_file
            result.certificate_info = cert_info
            result.signature_timestamp = datetime.now().isoformat()
            result.signing_info = {
                "hash_algorithm": self.config.hash_algorithm,
                "signature_format": self.config.signature_format,
                "signer_version": "1.0.0",
            }

            self.console.print(f"✅ Successfully signed module: {signed_file}")

        except Exception as e:
            result.errors.append(f"Signing error: {e!s}")

        return result

    def verify_module_signature(
        self, signed_file: Path, signature_file: Path
    ) -> dict[str, Any]:
        """Verify a module signature.

        Args:
            signed_file: Path to the signed module file
            signature_file: Path to the signature file

        Returns:
            Dictionary with verification results
        """
        try:
            # Load certificate
            cert_validation = validate_certificate_path(self.config.certificate_path)
            if not cert_validation["valid"]:
                return {
                    "valid": False,
                    "error": f"Certificate validation failed: {cert_validation['error']}",
                }

            certificate = cert_validation["certificate"]

            # Read module file and signature
            with open(signed_file, "rb") as f:
                module_data = f.read()

            with open(signature_file, "rb") as f:
                signature_data = f.read()

            # Verify signature
            public_key = certificate.public_key()

            try:
                public_key.verify(
                    signature_data,
                    module_data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH,
                    ),
                    hashes.SHA256(),
                )

                return {
                    "valid": True,
                    "certificate_info": self._extract_certificate_info(certificate),
                    "verified_at": datetime.now().isoformat(),
                }

            except Exception as verify_error:
                return {
                    "valid": False,
                    "error": f"Signature verification failed: {verify_error!s}",
                }

        except Exception as e:
            return {"valid": False, "error": f"Verification error: {e!s}"}

    def sign_multiple_modules(self, module_files: list[Path]) -> list[SigningResult]:
        """Sign multiple modules in batch.

        Args:
            module_files: List of module files to sign

        Returns:
            List of signing results
        """
        results = []

        self.console.print(f"🔐 Signing {len(module_files)} modules...")

        for module_file in module_files:
            self.console.print(f"\n📝 Signing {module_file.name}...")
            result = self.sign_module(module_file)
            results.append(result)

            if result.success:
                self.console.print(f"✅ {module_file.name} signed successfully")
            else:
                self.console.print(f"❌ {module_file.name} signing failed")
                for error in result.errors:
                    self.console.print(f"   Error: {error}")

        return results

    def _check_directory_writable(self, directory: Path) -> bool:
        """Check if directory is writable."""
        try:
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception:
            return False

    def _create_module_signature(
        self,
        module_file: Path,
        certificate: x509.Certificate,
        private_key: rsa.RSAPrivateKey,
    ) -> dict[str, Any]:
        """Create digital signature for module file."""
        try:
            # Read module file
            with open(module_file, "rb") as f:
                module_data = f.read()

            # Create signature
            signature = private_key.sign(
                module_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return {"success": True, "signature": signature, "errors": []}

        except Exception as e:
            return {
                "success": False,
                "signature": None,
                "errors": [f"Signature creation error: {e!s}"],
            }

    def _extract_certificate_info(
        self, certificate: x509.Certificate
    ) -> dict[str, Any]:
        """Extract information from certificate."""
        try:
            subject = certificate.subject
            issuer = certificate.issuer

            return {
                "subject": str(subject),
                "issuer": str(issuer),
                "serial_number": str(certificate.serial_number),
                "not_valid_before": certificate.not_valid_before.isoformat(),
                "not_valid_after": certificate.not_valid_after.isoformat(),
                "signature_algorithm": certificate.signature_algorithm_oid._name,
                "public_key_algorithm": type(certificate.public_key()).__name__,
            }
        except Exception as e:
            return {"error": f"Certificate info extraction error: {e!s}"}
