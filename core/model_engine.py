"""
LLM Model Engine
Handles all interactions with Large Language Models (OpenAI or Azure OpenAI).
Supports both simple and comprehensive reconciliation prompts.
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI, AzureOpenAI
import config


class ModelEngine:
    """Manages LLM API calls and prompt engineering."""

    def __init__(self):
        self.skip_llm = config.SKIP_LLM
        self.client = None
        if not self.skip_llm:
            # Initialize OpenAI client - support both Azure and standard OpenAI
            if config.USE_AZURE and config.AZURE_ENDPOINT:
                # Azure OpenAI configuration
                self.client = AzureOpenAI(
                    api_key=config.LLM_API_KEY,
                    azure_endpoint=config.AZURE_ENDPOINT,
                    api_version="2024-02-15-preview"
                )
            else:
                # Standard OpenAI configuration
                base_url = config.LLM_ENDPOINT
                if '/chat/completions' in base_url:
                    base_url = base_url.rsplit('/chat/completions', 1)[0]
                self.client = OpenAI(
                    api_key=config.LLM_API_KEY,
                    base_url=base_url
                )
        else:
            # Provide clear notice in logs when skipping
            print("[ModelEngine] SKIP_LLM=True - using stubbed responses for reconciliation.")

        self.model = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS

        # Load prompt templates
        self.simple_prompt_template = self._load_prompt("simple_prompt.txt")
        self.comprehensive_prompt_template = self._load_prompt("comprehensive_prompt.txt")
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from prompts directory."""
        prompt_path = os.path.join("prompts", filename)
        
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def reconcile_simple(
        self,
        baseline_meds: List[str],
        reference_meds: List[str],
        baseline_label: str = "Inpatient on Admission",
        reference_label: str = "Outpatient Home Meds"
    ) -> str:
        """
        Perform simple daily reconciliation.
        
        Args:
            baseline_meds: Current medication list (the "now")
            reference_meds: Previous medication list (the "then")
            baseline_label: Label for baseline list
            reference_label: Label for reference list
        
        Returns:
            LLM-generated reconciliation output
        """
        # Format medication lists
        baseline_str = self._format_med_list(baseline_meds)
        reference_str = self._format_med_list(reference_meds)
        
        # Build prompt from template
        prompt = self.simple_prompt_template.replace("{{baseline_label}}", baseline_label)
        prompt = prompt.replace("{{reference_label}}", reference_label)
        prompt = prompt.replace("{{baseline_meds}}", baseline_str)
        prompt = prompt.replace("{{reference_meds}}", reference_str)
        
        # Call LLM
        response = self._call_llm(prompt)
        return response
    
    def reconcile_comprehensive(
        self,
        baseline_meds: List[str],
        reference_meds: List[str],
        patient_context: Optional[Dict] = None,
        baseline_label: str = "Inpatient on Admission",
        reference_label: str = "Outpatient Home Meds"
    ) -> str:
        """
        Perform comprehensive admission/discharge reconciliation.
        
        Args:
            baseline_meds: Current medication list
            reference_meds: Previous medication list
            patient_context: Optional dict with demographics, allergies, labs, etc.
            baseline_label: Label for baseline list
            reference_label: Label for reference list
        
        Returns:
            LLM-generated comprehensive reconciliation
        """
        # Format medication lists
        baseline_str = self._format_med_list(baseline_meds)
        reference_str = self._format_med_list(reference_meds)
        
        # Format patient context
        context_str = self._format_patient_context(patient_context) if patient_context else "No additional context provided."
        
        # Build prompt from template
        prompt = self.comprehensive_prompt_template.replace("{{baseline_label}}", baseline_label)
        prompt = prompt.replace("{{reference_label}}", reference_label)
        prompt = prompt.replace("{{baseline_meds}}", baseline_str)
        prompt = prompt.replace("{{reference_meds}}", reference_str)
        prompt = prompt.replace("{{patient_context}}", context_str)
        prompt = prompt.replace("{{additional_context}}", context_str)
        
        # Call LLM
        response = self._call_llm(prompt)
        return response
    
    def _format_med_list(self, meds: List[str]) -> str:
        """Format medication list with numbering and total count."""
        if not meds:
            return "(Empty list)\n# Total Medications: 0"
        
        formatted = "\n".join([f"{i+1}. {med}" for i, med in enumerate(meds)])
        formatted += f"\n\n# Total Medications: {len(meds)}"
        return formatted
    
    def _format_patient_context(self, context: Dict) -> str:
        """Format patient context dictionary into readable string."""
        lines = []
        
        if "demographics" in context:
            demo = context["demographics"]
            lines.append(f"**Demographics:** Age {demo.get('age', 'unknown')}, {demo.get('sex', 'unknown')}")
        
        if "allergies" in context:
            allergies = context["allergies"]
            if allergies:
                lines.append(f"**Allergies:** {', '.join(allergies)}")
            else:
                lines.append("**Allergies:** NKDA")
        
        if "labs" in context:
            labs = context["labs"]
            lab_str = ", ".join([f"{k.upper()}: {v}" for k, v in labs.items()])
            lines.append(f"**Labs:** {lab_str}")
        
        if "problems" in context:
            problems = context["problems"]
            lines.append(f"**Problem List:** {', '.join(problems)}")
        
        return "\n".join(lines) if lines else "No additional context provided."
    
    def _call_llm(self, prompt: str) -> str:
        """
        Make API call to LLM.
        
        Args:
            prompt: Formatted prompt string
        
        Returns:
            LLM response text
        """
        if self.skip_llm:
            # Return deterministic stub for testing environments
            return (
                "{\n  \"matched\": [],\n  \"discrepancies\": [],\n  \"additions\": [],\n  \"discontinuations\": [],\n  \"ambiguities\": [],\n  \"summary\": {\n    \"total_prior_meds\": 0,\n    \"total_current_meds\": 0,\n    \"matched_count\": 0,\n    \"discrepancy_count\": 0,\n    \"addition_count\": 0,\n    \"discontinuation_count\": 0,\n    \"ambiguity_count\": 0,\n    \"clinical_notes\": \"LLM skipped (stub response).\"\n  }\n}"
            )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a clinical pharmacist expert in medication reconciliation. "
                                   "You are precise, evidence-based, and never guess or hallucinate information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {str(e)}")
    
    def generate(self, prompt: str, system_message: str = None) -> str:
        """
        Generic method to generate text from a prompt.
        Used by the reconciliation engine for custom prompts.
        
        Args:
            prompt: The prompt text
            system_message: Optional custom system message
        
        Returns:
            LLM response text
        """
        if system_message is None:
            system_message = ("You are a clinical pharmacist expert in medication reconciliation. "
                            "You are precise, evidence-based, and never guess or hallucinate information.")
        
        if self.skip_llm:
            return "LLM skipped (stub response)."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {str(e)}")
    
    def validate_no_hallucination(self, response: str, input_meds: List[str]) -> bool:
        """
        Simple validation check: ensure response doesn't mention medications
        not in the input lists.
        
        Args:
            response: LLM response text
            input_meds: Combined list of all input medications
        
        Returns:
            True if no obvious hallucinations detected
        """
        # This is a simplified check - in production, you'd want more sophisticated validation
        response_lower = response.lower()
        
        # Check if "none" is properly used for empty categories
        if "new medications" in response_lower and "none" not in response_lower:
            # Could be hallucination if there are actually no new meds
            pass
        
        return True  # Placeholder - implement more sophisticated checks as needed
