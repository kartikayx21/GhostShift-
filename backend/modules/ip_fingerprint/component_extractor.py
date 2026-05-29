"""Component Extractor — extracts product DNA fingerprint vectors."""

import re
import random


class ComponentExtractor:
    """Extracts product DNA: chip IDs, PCB markings, packaging codes, serial patterns."""

    # Known component databases for mock/demo
    KNOWN_COMPONENTS = {
        "apple": {
            "airpods": {
                "chipIds": ["H2", "STM32F103C8T6", "BCM4387"],
                "pcbMarkings": ["APL-1102", "REV-3.2B", "FPC-2026"],
                "packagingCodes": ["MQD83", "MTJV3"],
                "serialPattern": {
                    "format": r"^[A-Z]{4}[0-9]{1}[A-Z]{2}[0-9]{4}$",
                    "checksum": "luhn_mod10",
                    "yearEncoding": "pos5-6",
                    "facilityEncoding": "pos1-2",
                },
            },
            "iphone": {
                "chipIds": ["A17 Pro", "U1 Ultra Wideband", "Qualcomm X70"],
                "pcbMarkings": ["APL-2305", "REV-4.1A"],
                "packagingCodes": ["MU793", "MU7A3"],
                "serialPattern": {
                    "format": r"^[A-Z0-9]{12}$",
                    "checksum": "mod11",
                    "yearEncoding": "pos4-5",
                    "facilityEncoding": "pos1-3",
                },
            },
        },
        "samsung": {
            "galaxy buds": {
                "chipIds": ["QCC3046", "AKM4377", "TI BQ25120"],
                "pcbMarkings": ["SM-R510", "REV-2.0"],
                "packagingCodes": ["SM-R510NZAAXAR"],
                "serialPattern": {
                    "format": r"^RF[A-Z]{2}[0-9]{6}$",
                    "checksum": "mod97",
                    "yearEncoding": "pos5-6",
                    "facilityEncoding": "pos3-4",
                },
            },
        },
        "dyson": {
            "v15": {
                "chipIds": ["Dyson Hyperdymium", "ARM Cortex-M4", "TI DRV8301"],
                "pcbMarkings": ["DYS-V15-R3", "PCBA-2026-01"],
                "packagingCodes": ["SV47-US-V15"],
                "serialPattern": {
                    "format": r"^SV[0-9]{2}-[A-Z]{2}-[0-9]{8}$",
                    "checksum": "crc16",
                    "yearEncoding": "pos6-7",
                    "facilityEncoding": "pos4-5",
                },
            },
        },
    }

    def extract(self, brand: str, product: str, custom_data: dict | None = None) -> dict:
        """
        Extract product DNA fingerprint.

        Args:
            brand: Brand name (e.g., "Apple")
            product: Product name (e.g., "AirPods Pro")
            custom_data: Optional user-provided genuine product details

        Returns:
            Product DNA fingerprint dictionary
        """
        # If user provides custom data, use that
        if custom_data:
            return self._build_fingerprint(custom_data)

        # Otherwise, look up known components
        brand_lower = brand.lower()
        product_lower = product.lower()

        for brand_key, products in self.KNOWN_COMPONENTS.items():
            if brand_key in brand_lower:
                for product_key, components in products.items():
                    if product_key in product_lower:
                        return {
                            "componentSignature": {
                                "chipIds": components["chipIds"],
                                "pcbMarkings": components["pcbMarkings"],
                                "packagingCodes": components["packagingCodes"],
                                "serialPattern": components["serialPattern"],
                            },
                            "visualFingerprint": self._generate_visual_fingerprint(brand, product),
                            "brand": brand,
                            "product": product,
                            "confidence": round(random.uniform(0.85, 0.98), 2),
                        }

        # Generic fallback for unknown products
        return self._generate_generic_fingerprint(brand, product)

    def _build_fingerprint(self, data: dict) -> dict:
        """Build fingerprint from user-provided data."""
        return {
            "componentSignature": {
                "chipIds": data.get("chipIds", []),
                "pcbMarkings": data.get("pcbMarkings", []),
                "packagingCodes": data.get("packagingCodes", []),
                "serialPattern": data.get("serialPattern", {}),
            },
            "visualFingerprint": data.get("visualFingerprint", {}),
            "brand": data.get("brand", "Unknown"),
            "product": data.get("product", "Unknown"),
            "confidence": 1.0,
        }

    def _generate_visual_fingerprint(self, brand: str, product: str) -> dict:
        """Generate visual fingerprint data for a product."""
        return {
            "logoPlacement": {
                "x": random.randint(40, 60),
                "y": random.randint(10, 30),
                "width_percent": round(random.uniform(15, 35), 1),
                "orientation": "center",
            },
            "colorProfile": {
                "primary": "#FFFFFF",
                "secondary": "#E5E5E5",
                "accent": "#333333",
                "pantone_codes": ["PMS Cool Gray 1C", "PMS Black 6C"],
            },
            "fontSignatures": ["SF Pro Display", "SF Pro Text", "Helvetica Neue"],
        }

    def _generate_generic_fingerprint(self, brand: str, product: str) -> dict:
        """Generate a generic fingerprint for unknown products."""
        return {
            "componentSignature": {
                "chipIds": [f"GENERIC-{random.randint(1000, 9999)}"],
                "pcbMarkings": [f"{brand[:3].upper()}-{random.randint(100, 999)}"],
                "packagingCodes": [f"{brand[:2].upper()}{random.randint(100, 999)}"],
                "serialPattern": {
                    "format": r"^[A-Z0-9]{10,14}$",
                    "checksum": "luhn",
                    "yearEncoding": "unknown",
                    "facilityEncoding": "unknown",
                },
            },
            "visualFingerprint": self._generate_visual_fingerprint(brand, product),
            "brand": brand,
            "product": product,
            "confidence": 0.50,
        }
