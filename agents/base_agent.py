"""
Base Agentic Agent Class
Implements reasoning, tool use, and collaboration patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from gemini_config import GeminiAgent, get_medical_ontology
import json


class BaseAgent(ABC):
    """Base class for all agentic agents"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.agent = GeminiAgent(system_prompt)
        self.ontology = get_medical_ontology()
        self.reasoning_steps = []
    
    def reason(self, input_text: str) -> Dict[str, Any]:
        """
        Agentic reasoning: Think step-by-step before acting
        """
        reasoning_prompt = f"""You are {self.name}. Analyze the following patient narrative step by step.

Patient narrative: {input_text}

Think through your analysis:
1. What key information do you extract?
2. What patterns or signals do you detect?
3. What is your confidence level?
4. What are potential uncertainties?

Provide your reasoning, then your final analysis."""
        
        response = self.agent.generate(reasoning_prompt, temperature=0.3)
        self.reasoning_steps.append({
            "input": input_text,
            "reasoning": response,
            "agent": self.name
        })
        
        return {
            "reasoning": response,
            "agent": self.name
        }
    
    @abstractmethod
    def execute(self, input_text: str) -> Dict[str, Any]:
        """Execute the agent's primary task"""
        pass
    
    def use_rag(self, query: str, category: str) -> List[str]:
        """
        RAG: Retrieve relevant medical concepts from ontology
        """
        # Ensure query is a string
        if not isinstance(query, str):
            query = str(query) if query else ""
        
        query_lower = query.lower()
        matches = []
        
        if category in self.ontology:
            for key, values in self.ontology[category].items():
                if any(term in query_lower for term in key.split('/')):
                    matches.extend(values)
        
        return matches[:5]  # Return top 5 matches
    
    def collaborate(self, other_agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent collaboration: Incorporate other agents' findings
        """
        collaboration_prompt = f"""As {self.name}, integrate the following findings from other agents:

{json.dumps(other_agent_results, indent=2)}

How do these findings inform or modify your analysis? Provide updated insights."""
        
        return self.agent.generate(collaboration_prompt, temperature=0.3)


