# core/synthesizer.py
"""
SkinAnalysisSynthesizer
-----------------------
Merges GPT-4o + Gemini results using:
- Confidence-based conflict resolution
- Concern selection (primary / secondary / tertiary)
- Removal of concern duplicates from remaining metrics
- Weighted numeric merging
- Final output ordering (Option B)

This module is clean, modular, and production-grade.
"""

STATUS_SUCCESS = "SYNTHESIS_SUCCESS"
ERR_DATA_STRUCTURE = 1001
ERR_PROCESSING_FAILED = 1003


class SkinAnalysisSynthesizer:
    """
    Main synthesizer class.
    Takes merged LLM response:
        { "details": { "gpt4o": {...}, "gemini": {...} } }
    and produces final harmonized output.
    """

    def __init__(self, data: dict):
        # Raw data from API
        self.data = data

        # Model aliases
        self.model_a_name = "gpt4o"
        self.model_b_name = "gemini"

        # Model data dicts
        self.model_a = {}
        self.model_b = {}

        # Confidences
        self.conf_a = 0
        self.conf_b = 0

        # Winner model (higher confidence)
        self.higher_conf_model = {}
        self.lower_conf_model = {}
        self.higher_conf_name = ""

        # Results
        self.final_result = {}
        self.resolved_concerns = []

        # Keys not used in weighted merges
        self.ignore_keys = ["overall_confidence"]

    # --------------------------
    # INITIAL SETUP
    # --------------------------
    def _setup(self):
        """
        Validate input, load model dicts, and determine which model
        has higher overall confidence.
        """
        if not self.data or "details" not in self.data:
            raise ValueError(ERR_DATA_STRUCTURE, "Missing 'details' structure")

        details = self.data["details"]
        self.model_a = details.get(self.model_a_name, {})
        self.model_b = details.get(self.model_b_name, {})

        # Confidence
        self.conf_a = self._safe_conf(self.model_a)
        self.conf_b = self._safe_conf(self.model_b)

        # Select higher confidence model
        if self.conf_a >= self.conf_b:
            self.higher_conf_model = self.model_a
            self.lower_conf_model = self.model_b
            self.higher_conf_name = self.model_a_name
        else:
            self.higher_conf_model = self.model_b
            self.lower_conf_model = self.model_a
            self.higher_conf_name = self.model_b_name

    def _safe_conf(self, m):
        """Safely extract overall_confidence as int."""
        c = m.get("overall_confidence", 0)
        return int(c) if isinstance(c, (int, float)) else 0

    # --------------------------
    # CONCERN EXTRACTION
    # --------------------------
    def _extract_and_resolve_concerns(self):
        """
        Extract primary, secondary, tertiary from both models.
        If both models report the same concern:
            → pick the one from higher confidence model.
        Keep top 3 based on severity.
        """
        slots = ["primary", "secondary", "tertiary"]
        combined = {}      # concern_name → severity
        source_info = {}   # concern_name → { model, conf }

        for name, m, conf in [
            (self.model_a_name, self.model_a, self.conf_a),
            (self.model_b_name, self.model_b, self.conf_b),
        ]:
            for slot in slots:
                c = m.get(f"{slot}_concern", "")
                s = m.get(f"{slot}_concern_severity", 0)

                if not c or not s:
                    continue

                if c in combined:
                    # Same concern from both models → choose by confidence
                    if conf > source_info[c]["conf"]:
                        combined[c] = s
                        source_info[c] = {"model": name, "conf": conf}
                else:
                    combined[c] = s
                    source_info[c] = {"model": name, "conf": conf}

        # Sort by severity descending
        lst = [(sev, con, source_info[con]) for con, sev in combined.items()]
        lst.sort(key=lambda x: x[0], reverse=True)

        # Keep top 3
        self.resolved_concerns = lst[:3]

    def _assign_sorted_concerns(self):
        """
        Assign the resolved concerns into:
        - primary_concern
        - secondary_concern
        - tertiary_concern
        """
        ck = ["primary_concern", "secondary_concern", "tertiary_concern"]
        sk = ["primary_concern_severity", "secondary_concern_severity", "tertiary_concern_severity"]

        for i in range(3):
            if i < len(self.resolved_concerns):
                sev, con, _ = self.resolved_concerns[i]
                self.final_result[ck[i]] = con
                self.final_result[sk[i]] = sev
            else:
                self.final_result[ck[i]] = ""
                self.final_result[sk[i]] = 0

    # --------------------------
    # MAIN MERGE ENGINE
    # --------------------------
    def synthesize(self):
        """
        Merge both models:
        - Resolve numeric conflicts (weighted average)
        - Resolve string conflicts (confidence)
        - Extract priorities
        - Remove duplicate concerns from metric section
        - Apply final Option-B ordering
        """
        try:
            self._setup()
            a, b = self.model_a, self.model_b

            # ---------- 1. MERGE GENERAL ATTRIBUTES ----------
            all_keys = set(a.keys()) | set(b.keys())
            concern_keys = {
                "primary_concern", "primary_concern_severity",
                "secondary_concern", "secondary_concern_severity",
                "tertiary_concern", "tertiary_concern_severity",
                "overall_confidence"
            }

            for key in all_keys:
                if key in concern_keys:
                    continue

                va = a.get(key)
                vb = b.get(key)

                # Same value
                if va == vb:
                    self.final_result[key] = va
                    continue

                # Only one model has value
                if va is None:
                    self.final_result[key] = vb
                    continue
                if vb is None:
                    self.final_result[key] = va
                    continue

                # String conflict → higher confidence
                if isinstance(va, str) and isinstance(vb, str):
                    self.final_result[key] = self.higher_conf_model.get(key)
                    continue

                # Numeric conflict → weighted average
                if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                    if self.conf_a + self.conf_b == 0:
                        self.final_result[key] = int((va + vb) / 2)
                    else:
                        weighted = (va * self.conf_a + vb * self.conf_b) / (self.conf_a + self.conf_b)
                        self.final_result[key] = int(round(weighted))
                    continue

            # ---------- 2. PRIORITY CONCERNS ----------
            self._extract_and_resolve_concerns()
            self._assign_sorted_concerns()

            # ---------- 3. REMOVE DUPLICATED METRICS ----------
            chosen = {
                self.final_result.get("primary_concern", ""),
                self.final_result.get("secondary_concern", ""),
                self.final_result.get("tertiary_concern", "")
            }

            metric_keys = [
                "oiliness", "pores", "dehydration", "texture", "elasticity",
                "firmness", "wrinkles", "spots", "redness", "uneven_skintone",
                "dark_circles", "acne"
            ]

            cleaned = {}
            for k in metric_keys:
                if k in chosen:
                    continue
                cleaned[k] = self.final_result.get(k, a.get(k, b.get(k)))

            # purge old
            for k in metric_keys:
                self.final_result.pop(k, None)

            self.final_result.update(cleaned)

            # ---------- 4. FINAL OUTPUT ORDERING (Option B) ----------
            order = [
                "perceived_skin_age", "skin_type", "skin_type_score",
                "primary_concern", "primary_concern_severity",
                "secondary_concern", "secondary_concern_severity",
                "tertiary_concern", "tertiary_concern_severity",
            ] + metric_keys

            ordered = {}
            for k in order:
                if k in self.final_result:
                    ordered[k] = self.final_result[k]

            # append leftovers
            for k, v in self.final_result.items():
                if k not in ordered:
                    ordered[k] = v

            return {"data": ordered}

        except ValueError as e:
            code, msg = e.args
            return {"status": "error", "code": code, "message": msg}
        except Exception as e:
            return {
                "status": "error",
                "code": ERR_PROCESSING_FAILED,
                "message": str(e)
            }


# ------------------------------------------------------------
# SINGLE MODEL FALLBACK
# ------------------------------------------------------------
# def finalize_from_single_model(model: dict) -> dict:
#     """
#     Used when only GPT or only Gemini responded.
#     Removes duplicates from metrics and applies Option-B ordering.
#     """
#     m = dict(model)

#     chosen = {
#         m.get("primary_concern", ""),
#         m.get("secondary_concern", ""),
#         m.get("tertiary_concern", "")
#     }

#     metrics = [
#         "oiliness", "pores", "dehydration", "texture", "elasticity",
#         "firmness", "wrinkles", "spots", "redness", "uneven_skintone",
#         "dark_circles", "acne"
#     ]

#     out = {}

#     # Order Part 1
#     for k in ["perceived_skin_age", "skin_type", "skin_type_score"]:
#         if k in m:
#             out[k] = m[k]

#     # Order Part 2
#     for k in [
#         "primary_concern", "primary_concern_severity",
#         "secondary_concern", "secondary_concern_severity",
#         "tertiary_concern", "tertiary_concern_severity",
#     ]:
#         if k in m:
#             out[k] = m[k]

#     # Remaining metrics
#     for k in metrics:
#         if k in chosen:
#             continue
#         if k in m:
#             out[k] = m[k]

#     print("Finalized single model output:", out)
#     return {"data": out}


def finalize_from_single_model(model: dict) -> dict:
    """
    Convert raw model output into structured format:
    {"key": {"value": X, "url": "..."}}
    with ordering.
    """

    # Default URL for all fields (change if needed)
    DEFAULT_URL = "https://cdn.pixabay.com/photo/2021/06/11/12/26/woman-6328478_960_720.jpg"

    # Which keys need URLs?
    keys_with_url = {
        "primary_concern",
        "secondary_concern",
        "tertiary_concern",
        "oiliness",
        "pores",
        "dehydration",
        "texture",
        "elasticity",
        "firmness",
        "wrinkles",
        "spots",
        "redness",
        "uneven_skintone",
        "dark_circles",
        "acne"
    }

    # Wrap raw values into desired format
    def wrap(key, value):
        if key in keys_with_url:
            return {"value": value, "url": DEFAULT_URL}
        return {"value": value}

    m = {k: wrap(k, v) for k, v in model.items()}

    chosen = {
        model.get("primary_concern", ""),
        model.get("secondary_concern", ""),
        model.get("tertiary_concern", "")
    }

    metrics = [
        "oiliness", "pores", "dehydration", "texture", "elasticity",
        "firmness", "wrinkles", "spots", "redness", "uneven_skintone",
        "dark_circles", "acne"
    ]

    out = {}

    # Order Part 1
    for k in ["perceived_skin_age", "skin_type", "skin_type_score"]:
        if k in m:
            out[k] = m[k]

    # Order Part 2
    for k in [
        "primary_concern", "primary_concern_severity",
        "secondary_concern", "secondary_concern_severity",
        "tertiary_concern", "tertiary_concern_severity",
    ]:
        if k in m:
            out[k] = m[k]

    # Remaining metrics
    for k in metrics:
        if k in chosen:
            continue
        if k in m:
            out[k] = m[k]

    return {"data": out}


# Public interface
def run_analysis(data: dict):
    return SkinAnalysisSynthesizer(data).synthesize()
