"""
Confidence & Risk Scoring Agent - Production Implementation

This is the CRITICAL decision-making layer.

Purpose:
- Quantify confidence in the answer (0-100 score)
- Assess legal risk factors (low/medium/high/critical)
- Synthesize signals from all upstream agents
- Provide transparent reasoning for the score

Why this matters:
- Not all answers are equal
- Users need to know what to trust
- System needs to decide when to refuse
- Legal work requires quantified uncertainty

Architecture:
Input signals:
1. Verification result (are citations valid?)
2. Counter-arguments (how strong are objections?)
3. Retrieval quality (how relevant is context?)
4. Answer characteristics (assumptions, caveats, complexity)

Output:
- Confidence score with factor breakdown
- Risk assessment with mitigation suggestions
- Transparent reasoning for explainability

Design decisions:
- Composite scoring (multiple weighted factors)
- Conservative bias (err on side of caution)
- Transparent factors (no black box)
- Domain-tuned thresholds (legal-specific)
"""

from typing import Dict, List, Optional
from loguru import logger

# Handle both relative and absolute imports
try:
    from ..schemas.state import GraphState
    from ..schemas.scoring import ConfidenceScore, RiskAssessment
    from ..schemas.verification import VerificationResult
    from ..schemas.counter import CounterArgument
    from ..schemas.answer import Answer
    from ..schemas.retrieval import RetrievalResult
except ImportError:
    from schemas.state import GraphState
    from schemas.scoring import ConfidenceScore, RiskAssessment
    from schemas.verification import VerificationResult
    from schemas.counter import CounterArgument
    from schemas.answer import Answer
    from schemas.retrieval import RetrievalResult


class ConfidenceRiskScorer:
    """
    Scores confidence and assesses risk based on multiple signals.
    
    Scoring methodology:
    1. Compute per-factor scores (0-100 each)
    2. Weight factors by importance
    3. Aggregate to overall confidence (0-100)
    4. Assess risk independently (low/medium/high/critical)
    
    Factor weights (tuned for legal RAG):
    - Citation validity: 35% (most important!)
    - Counter-argument strength: 25%
    - Retrieval quality: 20%
    - Answer characteristics: 20%
    
    Why these weights:
    - Citations are ground truth → highest weight
    - Counter-arguments surface real issues → high weight
    - Retrieval quality affects completeness → medium weight
    - Answer characteristics indicate complexity → medium weight
    """
    
    # Factor weights (must sum to 1.0)
    WEIGHTS = {
        "citation_validity": 0.35,      # 35%
        "counter_strength": 0.25,       # 25%
        "retrieval_quality": 0.20,      # 20%
        "answer_characteristics": 0.20,  # 20%
    }
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 85.0    # >= 85: High confidence
    MEDIUM_CONFIDENCE_THRESHOLD = 60.0  # 60-84: Medium confidence
    # < 60: Low confidence (likely refuse)
    
    def compute_confidence_and_risk(
        self,
        answer: Answer,
        counter_argument: Optional[CounterArgument],
        verification_result: VerificationResult,
        retrieval_result: RetrievalResult,
    ) -> tuple[ConfidenceScore, RiskAssessment]:
        """
        Compute confidence score and risk assessment.
        
        Args:
            answer: The Answer object
            counter_argument: Counter-argument analysis (optional)
            verification_result: Citation verification results
            retrieval_result: Retrieval quality metrics
            
        Returns:
            (ConfidenceScore, RiskAssessment)
            
        Learning insight:
        - Each factor is scored independently (0-100)
        - Factors are weighted by importance
        - Risk is assessed separately (not just inverse of confidence)
        """
        logger.info("Computing confidence and risk scores")
        
        # Compute individual factor scores
        factors = {}
        
        factors["citation_validity"] = self._score_citation_validity(
            verification_result
        )
        
        factors["counter_strength"] = self._score_counter_strength(
            counter_argument
        )
        
        factors["retrieval_quality"] = self._score_retrieval_quality(
            retrieval_result
        )
        
        factors["answer_characteristics"] = self._score_answer_characteristics(
            answer
        )
        
        # Compute weighted overall score
        overall_score = sum(
            factors[key] * self.WEIGHTS[key]
            for key in self.WEIGHTS.keys()
        )
        
        # Generate reasoning
        confidence_reasoning = self._generate_confidence_reasoning(
            overall_score, factors
        )
        
        # Create confidence score object
        confidence = ConfidenceScore(
            overall_score=round(overall_score, 1),
            factors=factors,
            reasoning=confidence_reasoning
        )
        
        # Assess risk (separate from confidence)
        risk = self._assess_risk(
            answer=answer,
            counter_argument=counter_argument,
            verification_result=verification_result,
            confidence_score=overall_score
        )
        
        logger.info(
            f"Confidence: {overall_score:.1f}/100, "
            f"Risk: {risk.overall_risk}"
        )
        
        return confidence, risk
    
    def _score_citation_validity(
        self,
        verification_result: VerificationResult
    ) -> float:
        """
        Score based on citation verification.
        
        Scoring logic:
        - 100: All citations valid
        - 50-99: Proportional to valid citation percentage
        - 0-49: Heavy penalty for invalid citations
        
        Why harsh penalty:
        - Invalid citations = potential hallucination
        - In legal work, one bad citation taints entire answer
        - Fail closed philosophy
        
        Returns:
            Score 0-100
        """
        if verification_result.total_citations == 0:
            # No citations → medium confidence (factual but ungrounded)
            return 60.0
        
        valid_ratio = (
            verification_result.valid_citations / 
            verification_result.total_citations
        )
        
        if valid_ratio == 1.0:
            # All citations valid → perfect score
            return 100.0
        elif valid_ratio >= 0.8:
            # 80-99% valid → moderate penalty
            return 60.0 + (valid_ratio - 0.8) * 200  # 60-100 range
        elif valid_ratio >= 0.5:
            # 50-79% valid → severe penalty (single bad citation is serious!)
            return 20.0 + (valid_ratio - 0.5) * 133  # 20-60 range
        else:
            # <50% valid → critical penalty
            return valid_ratio * 40  # 0-20 range
    
    def _score_counter_strength(
        self,
        counter_argument: Optional[CounterArgument]
    ) -> float:
        """
        Score based on counter-argument strength.
        
        Scoring logic (inverse):
        - Weak counter-args → high confidence
        - Strong counter-args → low confidence
        
        Counter-argument signals:
        - Contradictions (severe impact)
        - Exceptions (moderate impact)
        - Jurisdictional issues (moderate-severe impact)
        - Ambiguities (minor-moderate impact)
        - Missing context (minor impact)
        - Severity rating (minor/moderate/severe)
        
        Why this matters:
        - Counter-agent found legitimate concerns
        - Strong objections reduce confidence
        - Multiple issues compound
        
        Returns:
            Score 0-100 (higher = weaker counter-arguments)
        """
        if counter_argument is None:
            # No counter-argument analysis → assume medium confidence
            return 70.0
        
        # Start with base score
        score = 100.0
        
        # Penalty for contradictions (most severe)
        if counter_argument.contradictions:
            penalty = min(len(counter_argument.contradictions) * 20, 60)
            score -= penalty
            logger.debug(f"Contradictions penalty: -{penalty}")
        
        # Penalty for exceptions
        if counter_argument.exceptions:
            penalty = min(len(counter_argument.exceptions) * 10, 30)
            score -= penalty
            logger.debug(f"Exceptions penalty: -{penalty}")
        
        # Penalty for jurisdictional issues
        if counter_argument.jurisdictional_issues:
            penalty = min(len(counter_argument.jurisdictional_issues) * 15, 40)
            score -= penalty
            logger.debug(f"Jurisdictional issues penalty: -{penalty}")
        
        # Penalty for ambiguities
        if counter_argument.ambiguities:
            penalty = min(len(counter_argument.ambiguities) * 8, 25)
            score -= penalty
            logger.debug(f"Ambiguities penalty: -{penalty}")
        
        # Penalty for missing context
        if counter_argument.missing_context:
            penalty = min(len(counter_argument.missing_context) * 5, 15)
            score -= penalty
            logger.debug(f"Missing context penalty: -{penalty}")
        
        # Apply severity multiplier
        severity_multipliers = {
            "minor": 1.0,
            "moderate": 0.8,  # 20% additional penalty
            "severe": 0.6,    # 40% additional penalty
        }
        multiplier = severity_multipliers.get(counter_argument.severity, 0.8)
        score *= multiplier
        
        # Floor at 0
        score = max(0.0, score)
        
        logger.debug(f"Counter-argument score: {score:.1f}/100")
        return score
    
    def _score_retrieval_quality(
        self,
        retrieval_result: RetrievalResult
    ) -> float:
        """
        Score based on retrieval quality.
        
        Scoring factors:
        - Number of clauses retrieved (more = better context)
        - Similarity scores (higher = more relevant)
        - Coverage (did we get enough context?)
        
        Why this matters:
        - Weak retrieval → incomplete context
        - Low similarity → answer may be speculative
        - Few clauses → limited evidence
        
        Returns:
            Score 0-100
        """
        if not retrieval_result.clauses:
            # No retrieval → cannot answer confidently
            return 0.0
        
        # Factor 1: Number of clauses (more is better, up to a point)
        num_clauses = len(retrieval_result.clauses)
        if num_clauses >= 5:
            quantity_score = 100.0
        elif num_clauses >= 3:
            quantity_score = 80.0
        elif num_clauses >= 2:
            quantity_score = 60.0
        else:
            quantity_score = 40.0
        
        # Factor 2: Average similarity score
        avg_similarity = sum(
            clause.similarity_score for clause in retrieval_result.clauses
        ) / num_clauses
        
        # Convert similarity (0-1) to score (0-100)
        # With boosting for high similarity
        if avg_similarity >= 0.85:
            similarity_score = 90.0 + (avg_similarity - 0.85) * 66.7  # 90-100
        elif avg_similarity >= 0.70:
            similarity_score = 70.0 + (avg_similarity - 0.70) * 133.3  # 70-90
        else:
            similarity_score = avg_similarity * 100  # 0-70
        
        # Weighted combination (70% similarity, 30% quantity)
        overall = similarity_score * 0.7 + quantity_score * 0.3
        
        logger.debug(
            f"Retrieval score: {overall:.1f} "
            f"(similarity: {avg_similarity:.2f}, count: {num_clauses})"
        )
        
        return overall
    
    def _score_answer_characteristics(
        self,
        answer: Answer
    ) -> float:
        """
        Score based on answer characteristics.
        
        Indicators of high-quality answers:
        - Has citations (grounded)
        - Clear reasoning (not vague)
        - Acknowledges assumptions (transparent)
        - Includes caveats (safe)
        
        Indicators of low-quality answers:
        - No citations (ungrounded)
        - Vague reasoning
        - Many assumptions (speculative)
        - No caveats (overconfident)
        
        Returns:
            Score 0-100
        """
        score = 100.0
        
        # Penalty for no citations
        if not answer.citations:
            score -= 30
            logger.debug("No citations penalty: -30")
        
        # Penalty for many assumptions (indicates speculation)
        if len(answer.assumptions) >= 5:
            score -= 20
        elif len(answer.assumptions) >= 3:
            score -= 10
        
        # Bonus for caveats (shows nuance)
        if len(answer.caveats) >= 2:
            score += 10
        elif len(answer.caveats) >= 1:
            score += 5
        
        # Penalty for very short reasoning (indicates shallow analysis)
        if len(answer.reasoning) < 100:
            score -= 15
            logger.debug("Short reasoning penalty: -15")
        
        # Clamp to 0-100
        score = max(0.0, min(100.0, score))
        
        logger.debug(f"Answer characteristics score: {score:.1f}/100")
        return score
    
    def _generate_confidence_reasoning(
        self,
        overall_score: float,
        factors: Dict[str, float]
    ) -> str:
        """
        Generate human-readable reasoning for the confidence score.
        
        Why transparency matters:
        - Users need to understand the score
        - Audit trail for legal work
        - Debugging and tuning
        """
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for factor, score in factors.items():
            if score >= 85:
                strengths.append(f"{factor} is strong ({score:.0f}/100)")
            elif score < 60:
                weaknesses.append(f"{factor} is weak ({score:.0f}/100)")
        
        # Build reasoning
        if overall_score >= self.HIGH_CONFIDENCE_THRESHOLD:
            reasoning = f"High confidence ({overall_score:.1f}/100). "
        elif overall_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            reasoning = f"Medium confidence ({overall_score:.1f}/100). "
        else:
            reasoning = f"Low confidence ({overall_score:.1f}/100). "
        
        if strengths:
            reasoning += "Strengths: " + ", ".join(strengths[:2]) + ". "
        
        if weaknesses:
            reasoning += "Concerns: " + ", ".join(weaknesses[:2]) + ". "
        
        return reasoning.strip()
    
    def _assess_risk(
        self,
        answer: Answer,
        counter_argument: Optional[CounterArgument],
        verification_result: VerificationResult,
        confidence_score: float
    ) -> RiskAssessment:
        """
        Assess legal risk independently of confidence.
        
        Risk factors:
        1. Invalid citations (hallucination risk)
        2. Contradictions (legal inconsistency risk)
        3. Jurisdictional issues (compliance risk)
        4. Low confidence (uncertainty risk)
        5. Many caveats/assumptions (complexity risk)
        
        Risk levels:
        - Low: Safe to answer
        - Medium: Answer with strong disclaimers
        - High: Answer with very strong disclaimers
        - Critical: Should refuse to answer
        
        Why separate from confidence:
        - Confidence = "How sure are we?"
        - Risk = "What could go wrong?"
        - High confidence + High risk = Dangerous combination!
        """
        risk_factors = []
        liability_concerns = []
        mitigation_suggestions = []
        
        # Risk factor 1: Citation validity
        if verification_result.invalid_citations > 0:
            risk_factors.append(
                f"{verification_result.invalid_citations} invalid citation(s) detected"
            )
            liability_concerns.append("Potential hallucination or misattribution")
        
        # Risk factor 2: Counter-argument issues
        if counter_argument:
            if counter_argument.contradictions:
                risk_factors.append(
                    f"{len(counter_argument.contradictions)} contradiction(s) found"
                )
                liability_concerns.append("Conflicting legal principles")
            
            if counter_argument.jurisdictional_issues:
                risk_factors.append(
                    f"{len(counter_argument.jurisdictional_issues)} jurisdictional issue(s)"
                )
                liability_concerns.append("Jurisdiction-specific compliance concerns")
            
            if counter_argument.exceptions:
                risk_factors.append(
                    f"{len(counter_argument.exceptions)} exception(s) identified"
                )
                liability_concerns.append("Answer may not apply in all cases")
        
        # Risk factor 3: Low confidence
        if confidence_score < self.MEDIUM_CONFIDENCE_THRESHOLD:
            risk_factors.append("Low confidence score")
            liability_concerns.append("High uncertainty in analysis")
        
        # Risk factor 4: Many assumptions
        if len(answer.assumptions) >= 4:
            risk_factors.append(f"{len(answer.assumptions)} assumptions made")
            liability_concerns.append("Answer depends on unverified assumptions")
        
        # Determine overall risk level
        critical_flags = sum([
            verification_result.invalid_citations >= 2,
            counter_argument and len(counter_argument.contradictions) >= 2,
            confidence_score < 40,
        ])
        
        high_flags = sum([
            verification_result.invalid_citations >= 1,  # Any invalid citation is high risk
            counter_argument and len(counter_argument.contradictions) >= 1,
            counter_argument and len(counter_argument.jurisdictional_issues) >= 2,
            confidence_score < 65,  # Slightly raised threshold
            len(answer.assumptions) >= 5,
        ])
        
        medium_flags = sum([
            counter_argument and len(counter_argument.exceptions) >= 1,
            counter_argument and len(counter_argument.ambiguities) >= 2,
            confidence_score < 75,
            len(answer.assumptions) >= 3,
        ])
        
        # Risk level decision logic
        # Note: ANY invalid citation automatically elevates risk
        if critical_flags >= 1:
            overall_risk = "critical"
        elif verification_result.invalid_citations >= 1 and confidence_score < 70:
            # Invalid citation + low confidence = high risk
            overall_risk = "high"
            mitigation_suggestions.extend([
                "DO NOT rely on this answer for legal decisions",
                "Consult a qualified attorney immediately",
                "Consider system may be hallucinating"
            ])
        elif high_flags >= 2:
            overall_risk = "high"
            mitigation_suggestions.extend([
                "Consult a qualified attorney before acting",
                "Verify all citations independently",
                "Consider multiple legal opinions"
            ])
        elif medium_flags >= 2 or high_flags >= 1:
            overall_risk = "medium"
            mitigation_suggestions.extend([
                "Consult an attorney for case-specific advice",
                "Review referenced clauses directly",
                "Consider jurisdictional variations"
            ])
        else:
            overall_risk = "low"
            mitigation_suggestions.extend([
                "For general information only, not legal advice",
                "Consult an attorney for specific situations"
            ])
        
        logger.info(f"Risk assessment: {overall_risk} ({len(risk_factors)} factors)")
        
        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            mitigation_suggestions=mitigation_suggestions,
            liability_concerns=liability_concerns
        )


def score_confidence_node(state: GraphState) -> GraphState:
    """
    LangGraph node for confidence and risk scoring.
    
    State inputs:
    - answer: Answer object
    - counter_arguments: Counter-argument analysis
    - verification_result: Citation verification
    - retrieval_result: Retrieval quality
    
    State outputs:
    - confidence: ConfidenceScore
    - risk: RiskAssessment
    
    Why this is a separate node:
    - Modular (can swap scoring algorithms)
    - Testable in isolation
    - Clear decision point for downstream logic
    """
    query_id = state.get("query_id")
    answer = state.get("answer")
    counter_argument = state.get("counter_arguments")
    verification_result = state.get("verification_result")
    retrieval_result = state.get("retrieval_result")
    
    logger.info(f"[Scorer] Computing confidence and risk: {query_id}")
    
    # Handle edge cases
    if not answer:
        logger.error("No answer to score")
        return {
            **state,
            "confidence": ConfidenceScore(
                overall_score=0.0,
                factors={},
                reasoning="No answer generated"
            ),
            "risk": RiskAssessment(
                overall_risk="critical",
                risk_factors=["No answer available"],
                mitigation_suggestions=["System error - do not proceed"],
                liability_concerns=["Cannot provide legal analysis"]
            )
        }
    
    # Initialize scorer
    scorer = ConfidenceRiskScorer()
    
    # Compute scores
    confidence, risk = scorer.compute_confidence_and_risk(
        answer=answer,
        counter_argument=counter_argument,
        verification_result=verification_result,
        retrieval_result=retrieval_result
    )
    
    # Log results
    logger.success(
        f"[Scorer] Confidence: {confidence.overall_score:.1f}/100, "
        f"Risk: {risk.overall_risk} for {query_id}"
    )
    
    return {
        **state,
        "confidence": confidence,
        "risk": risk,
    }
