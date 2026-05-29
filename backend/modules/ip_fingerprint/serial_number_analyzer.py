"""Serial Number Analyzer — pattern matching engine for counterfeit detection."""

import re
import random
from collections import Counter


class SerialNumberAnalyzer:
    """Validates serial numbers and detects counterfeit patterns."""

    def validate_pattern(self, serial: str, genuine_pattern: dict) -> dict:
        """
        Validate a serial number against known genuine patterns.

        Returns analysis dict with format match, checksum, date, facility info.
        """
        fmt = genuine_pattern.get("format", "")
        checksum_algo = genuine_pattern.get("checksum", "luhn")
        year_enc = genuine_pattern.get("yearEncoding", "")
        facility_enc = genuine_pattern.get("facilityEncoding", "")

        format_match = bool(re.match(fmt, serial)) if fmt else False
        checksum_valid = self._verify_checksum(serial, checksum_algo)
        date_encoded = self._extract_date(serial, year_enc)
        facility_code = self._extract_facility(serial, facility_enc)
        sequential = self._detect_sequential(serial)
        future_date = self._check_future_date(date_encoded)

        # Confidence: 1.0 = genuine, 0.0 = fake
        confidence = 1.0
        if not format_match:
            confidence -= 0.4
        if not checksum_valid:
            confidence -= 0.3
        if sequential:
            confidence -= 0.2
        if future_date:
            confidence -= 0.3

        return {
            "serial": serial,
            "formatMatch": format_match,
            "checksumValid": checksum_valid,
            "dateEncoded": date_encoded,
            "facilityCode": facility_code,
            "sequentialAnomaly": sequential,
            "facilityMismatch": False,  # needs listing data to check
            "futureDate": future_date,
            "confidence": round(max(0.0, min(1.0, confidence)), 2),
        }

    def detect_counterfeit_patterns(self, serials: list[str]) -> dict:
        """
        Batch analysis: detect if multiple serials are from a ghost shift batch.

        Ghost shifts produce sequential serials that differ only in last digits.
        """
        if len(serials) < 3:
            return {"batchDetected": False, "batches": [], "analysis": "Insufficient data"}

        # Find common prefixes
        batches = self._find_common_prefixes(serials)

        return {
            "batchDetected": len(batches) > 0,
            "batches": batches,
            "totalSerials": len(serials),
            "uniquePrefixes": len(set(s[:-2] for s in serials if len(s) > 2)),
            "analysis": self._generate_batch_analysis(batches, serials),
        }

    def check_facility_vs_listing(self, serial: str, pattern: dict, claimed_origin: str) -> dict:
        """Check if serial's facility code matches the seller's claimed origin."""
        facility = self._extract_facility(serial, pattern.get("facilityEncoding", ""))

        # Known facility code mappings
        facility_locations = {
            "FH": "Foxconn Shenzhen", "DG": "Dongguan", "SZ": "Shenzhen",
            "GZ": "Guangzhou", "SH": "Shanghai", "FK": "Foxconn Kunshan",
            "US": "United States", "JP": "Japan", "KR": "South Korea",
        }

        actual_location = facility_locations.get(facility, "Unknown")
        mismatch = claimed_origin.lower() not in actual_location.lower() if facility else False

        return {
            "facilityCode": facility,
            "decodedLocation": actual_location,
            "claimedOrigin": claimed_origin,
            "mismatch": mismatch,
            "riskLevel": "high" if mismatch else "low",
        }

    def _verify_checksum(self, serial: str, algo: str) -> bool:
        """Verify serial checksum (simplified for demo)."""
        digits = [int(c) for c in serial if c.isdigit()]
        if not digits:
            return False

        if algo == "luhn" or algo == "luhn_mod10":
            return self._luhn_check(digits)
        elif algo == "mod97":
            return sum(digits) % 97 != 0  # simplified
        elif algo == "mod11":
            return sum(digits) % 11 != 0
        return True

    def _luhn_check(self, digits: list[int]) -> bool:
        """Simplified Luhn checksum verification."""
        if len(digits) < 2:
            return False
        total = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        return total % 10 == 0

    def _extract_date(self, serial: str, encoding: str) -> str:
        """Extract manufacture date from serial."""
        if not encoding or encoding == "unknown":
            return "unknown"
        try:
            parts = encoding.replace("pos", "").split("-")
            start, end = int(parts[0]) - 1, int(parts[1])
            year_digits = serial[start:end]
            if year_digits.isdigit():
                year = int(year_digits)
                if year < 100:
                    year += 2000
                return f"20{year_digits}" if year < 2100 else str(year)
        except (ValueError, IndexError):
            pass
        return "unknown"

    def _extract_facility(self, serial: str, encoding: str) -> str:
        """Extract facility code from serial."""
        if not encoding or encoding == "unknown":
            return ""
        try:
            parts = encoding.replace("pos", "").split("-")
            start, end = int(parts[0]) - 1, int(parts[1])
            return serial[start:end]
        except (ValueError, IndexError):
            return ""

    def _detect_sequential(self, serial: str) -> bool:
        """Check if serial looks like a sequential number (ghost shift indicator)."""
        trailing_digits = ""
        for c in reversed(serial):
            if c.isdigit():
                trailing_digits = c + trailing_digits
            else:
                break
        if len(trailing_digits) >= 3:
            num = int(trailing_digits)
            # Sequential check: ends in small number suggesting batch numbering
            return num < 100 or trailing_digits == trailing_digits[0] * len(trailing_digits)
        return False

    def _check_future_date(self, date_str: str) -> bool:
        """Check if manufacture date is in the future."""
        if date_str == "unknown":
            return False
        try:
            year = int(date_str[:4])
            return year > 2026
        except ValueError:
            return False

    def _find_common_prefixes(self, serials: list[str], min_prefix_len: int = 4) -> list[dict]:
        """Find groups of serials sharing common prefixes (ghost shift batches)."""
        batches = []
        prefix_groups: dict[str, list[str]] = {}

        for serial in serials:
            if len(serial) >= min_prefix_len:
                prefix = serial[:min_prefix_len]
                prefix_groups.setdefault(prefix, []).append(serial)

        for prefix, group in prefix_groups.items():
            if len(group) >= 3:
                # Check if suffixes are sequential
                suffixes = []
                for s in group:
                    suffix = s[min_prefix_len:]
                    if suffix.isdigit():
                        suffixes.append(int(suffix))

                is_sequential = False
                if len(suffixes) >= 3:
                    suffixes.sort()
                    diffs = [suffixes[i + 1] - suffixes[i] for i in range(len(suffixes) - 1)]
                    is_sequential = all(d <= 2 for d in diffs)

                batches.append({
                    "prefix": prefix,
                    "count": len(group),
                    "pattern": "sequential_increment" if is_sequential else "clustered",
                    "serials_sample": group[:5],
                    "verdict": (
                        "Ghost shift batch — sequential numbering indicates single production run"
                        if is_sequential
                        else f"Clustered batch — {len(group)} serials share prefix '{prefix}'"
                    ),
                })

        return batches

    def _generate_batch_analysis(self, batches: list[dict], serials: list[str]) -> str:
        """Generate human-readable batch analysis."""
        if not batches:
            return "No batch patterns detected. Serial numbers appear to have normal distribution."

        total_in_batches = sum(b["count"] for b in batches)
        return (
            f"Detected {len(batches)} suspicious batch(es) covering {total_in_batches} "
            f"of {len(serials)} serials. This pattern is consistent with unauthorized "
            f"mass production from a single facility (ghost shift operation)."
        )
