"""Serial Validator — genuine vs counterfeit serial validation for forensics."""

from modules.ip_fingerprint.serial_number_analyzer import SerialNumberAnalyzer


class SerialValidator:
    """Wraps SerialNumberAnalyzer with forensics-specific validation."""

    def __init__(self):
        self.analyzer = SerialNumberAnalyzer()

    def validate(self, serial: str, scenario_data: dict) -> dict:
        """Validate a serial against scenario data."""
        pattern = scenario_data.get("serial_analysis", {})
        genuine_pattern = {
            "format": pattern.get("genuine_pattern", ""),
            "checksum": pattern.get("checksum_algorithm", "luhn"),
            "yearEncoding": pattern.get("year_encoding", ""),
            "facilityEncoding": pattern.get("facility_encoding", ""),
        }

        result = self.analyzer.validate_pattern(serial, genuine_pattern)

        # Add batch analysis from scenario
        batches = pattern.get("counterfeit_batches", [])
        matching_batch = None
        for batch in batches:
            if serial.startswith(batch.get("prefix", "")):
                matching_batch = batch
                break

        result["batch_match"] = matching_batch
        result["in_counterfeit_batch"] = matching_batch is not None

        return result

    def validate_batch(self, serials: list[str], scenario_data: dict) -> dict:
        """Validate a batch of serials."""
        results = [self.validate(s, scenario_data) for s in serials]
        batch_analysis = self.analyzer.detect_counterfeit_patterns(serials)

        return {
            "individual_results": results,
            "batch_analysis": batch_analysis,
            "total_serials": len(serials),
            "suspicious_serials": sum(1 for r in results if r["confidence"] < 0.5),
            "in_known_batches": sum(1 for r in results if r["in_counterfeit_batch"]),
        }
