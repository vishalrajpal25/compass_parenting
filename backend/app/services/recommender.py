"""
Recommendation service with constraint solver.

Uses OR-Tools CP-SAT for optimal activity selection under constraints.
"""
import logging
from datetime import datetime
from typing import Any

from ortools.sat.python import cp_model
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.child import ChildProfile
from app.models.family import Family
from app.models.recommendation import Recommendation
from app.services.scoring import ScoringEngine

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Generate personalized activity recommendations with constraint solving.

    Steps:
    1. Score all candidate activities
    2. Apply constraints (budget, schedule, max activities)
    3. Solve optimization problem (maximize total score)
    4. Generate explanations
    5. Return recommendations in tiers (Primary, Budget-Saver, Stretch)
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize recommendation service.

        Args:
            db: Database session
        """
        self.db = db

    async def generate_recommendations(
        self,
        child_profile_id: int,
        max_activities: int = 3,
    ) -> list[Recommendation]:
        """
        Generate recommendations for a child.

        Args:
            child_profile_id: Child profile ID
            max_activities: Maximum activities to recommend

        Returns:
            List of recommendations ordered by score
        """
        # Get child and family
        result = await self.db.execute(
            select(ChildProfile).where(ChildProfile.id == child_profile_id)
        )
        child = result.scalar_one_or_none()

        if not child:
            raise ValueError(f"Child profile {child_profile_id} not found")

        result = await self.db.execute(
            select(Family).where(Family.id == child.family_id)
        )
        family = result.scalar_one_or_none()

        if not family:
            raise ValueError(f"Family {child.family_id} not found")

        # Get candidate activities
        activities = await self._get_candidate_activities(child)

        if not activities:
            logger.warning(f"No candidate activities found for child {child_profile_id}")
            return []

        # Score all activities
        scoring_engine = ScoringEngine(child, family)
        scored_activities = []

        for activity in activities:
            score, score_breakdown = scoring_engine.calculate_total_score(activity)
            scored_activities.append({
                "activity": activity,
                "score": score,
                "score_breakdown": score_breakdown,
            })

        # Sort by score
        scored_activities.sort(key=lambda x: x["score"], reverse=True)

        # Apply constraints with solver
        selected_activities = self._solve_constraints(
            scored_activities,
            family,
            max_activities,
        )

        # Create recommendations with explanations
        recommendations = []
        for idx, item in enumerate(selected_activities):
            # Determine tier
            if idx == 0:
                tier = "primary"
            elif idx < max_activities:
                tier = "primary"
            else:
                tier = "stretch"

            # Generate explanation
            explanation, why_good_fit, considerations, future_benefits = self._generate_explanation(
                child,
                item["activity"],
                item["score_breakdown"],
            )

            # Create recommendation
            recommendation = Recommendation(
                family_id=family.id,  # Denormalized for efficient tenant isolation
                child_profile_id=child_profile_id,
                activity_id=item["activity"].id,
                total_score=item["score"],
                fit_score=sum(item["score_breakdown"]["fit"].values()),
                practical_score=sum(item["score_breakdown"]["practical"].values()),
                goals_score=sum(item["score_breakdown"]["goals"].values()),
                score_details=item["score_breakdown"],
                tier=tier,
                explanation=explanation,
                why_good_fit=why_good_fit,
                considerations=considerations,
                future_benefits=future_benefits,
                generated_at=datetime.now(),
            )

            self.db.add(recommendation)
            recommendations.append(recommendation)

        await self.db.commit()

        logger.info(
            f"Generated {len(recommendations)} recommendations for child {child_profile_id}"
        )

        return recommendations

    async def _get_candidate_activities(self, child: ChildProfile) -> list[Activity]:
        """
        Get candidate activities for a child.

        Filters by:
        - Age range
        - Active status
        - Has valid start date

        Args:
            child: Child profile

        Returns:
            List of candidate activities
        """
        child_age = child.age

        # Query activities
        query = select(Activity).where(
            Activity.is_active == True
        )

        # Age filter
        query = query.where(
            ((Activity.min_age <= child_age) | (Activity.min_age.is_(None))) &
            ((Activity.max_age >= child_age) | (Activity.max_age.is_(None)))
        )

        # Has start date (or is ongoing)
        query = query.where(
            (Activity.start_date.isnot(None)) | (Activity.rrule.isnot(None))
        )

        # Limit to top 50 for performance
        query = query.limit(50)

        result = await self.db.execute(query)
        activities = result.scalars().all()

        return list(activities)

    def _solve_constraints(
        self,
        scored_activities: list[dict[str, Any]],
        family: Family,
        max_activities: int,
    ) -> list[dict[str, Any]]:
        """
        Apply constraints using OR-Tools CP-SAT solver.

        Constraints:
        - Maximum N activities
        - Budget limit
        - No schedule conflicts (simplified for now)

        Objective:
        - Maximize total score

        Args:
            scored_activities: List of scored activities
            family: Family profile
            max_activities: Maximum activities to select

        Returns:
            List of selected activities
        """
        # For MVP, use simple greedy selection
        # TODO: Implement full CP-SAT solver with schedule conflict detection

        selected = []
        total_cost = 0
        budget_limit = family.budget_monthly if family.budget_monthly else float('inf')

        for item in scored_activities:
            activity = item["activity"]

            # Check budget constraint
            activity_cost = activity.price_cents or 0
            if total_cost + activity_cost > budget_limit * 100:  # budget is in dollars, price in cents
                continue

            # Add activity
            selected.append(item)
            total_cost += activity_cost

            # Stop when we hit max
            if len(selected) >= max_activities:
                break

        return selected

    def _generate_explanation(
        self,
        child: ChildProfile,
        activity: Activity,
        score_breakdown: dict[str, Any],
    ) -> tuple[str, list[str], list[str], list[str]]:
        """
        Generate parent-friendly explanation for recommendation.

        Follows compass-parent-advocate principles:
        - Clear, non-technical language
        - Connect to child's specific traits
        - Explain "why" not just "what"
        - Transparency about tradeoffs
        - Link to future outcomes

        Args:
            child: Child profile
            activity: Recommended activity
            score_breakdown: Detailed scoring

        Returns:
            Tuple of (explanation, why_good_fit, considerations, future_benefits)
        """
        # Main explanation
        explanation = f"We think {activity.name} could be a great fit for {child.name}."

        # Why it's a good fit
        why_good_fit = []

        # Check fit components
        fit_scores = score_breakdown["fit"]

        if fit_scores.get("age_band_match", 0) >= 12:
            why_good_fit.append(f"Perfect age match ({child.age} years old)")

        if fit_scores.get("intensity_match", 0) >= 8:
            intensity = child.temperament.get("intensity_preference", "moderate") if child.temperament else "moderate"
            why_good_fit.append(f"Matches their {intensity}-energy temperament")

        if fit_scores.get("sensory_tolerance", 0) >= 8:
            why_good_fit.append("Comfortable sensory environment")

        if fit_scores.get("team_vs_solo", 0) >= 4:
            social = child.temperament.get("social_preference", "small_group") if child.temperament else "small_group"
            social_friendly = social.replace("_", " ")
            why_good_fit.append(f"Works well with their {social_friendly} preference")

        # Check goals alignment
        goals_scores = score_breakdown["goals"]
        if goals_scores.get("primary_goal", 0) >= 7:
            if child.primary_goal:
                why_good_fit.append(f"Directly supports '{child.primary_goal}' goal")

        # Considerations
        considerations = []

        practical_scores = score_breakdown["practical"]

        if practical_scores.get("commute_time", 0) < 7:
            considerations.append("May require longer travel time")

        if practical_scores.get("schedule_fit", 0) < 7:
            considerations.append("Check schedule compatibility carefully")

        if practical_scores.get("price_vs_budget", 0) < 3:
            considerations.append("Higher cost - consider if it fits your budget")

        if activity.max_participants:
            considerations.append(f"Limited to {activity.max_participants} participants - register early")

        # Future benefits
        future_benefits = []

        if child.primary_goal:
            goal_benefits = {
                "Build Confidence": "Building self-esteem and willingness to try new things",
                "College Prep Skills": "Developing critical thinking and study habits",
                "Physical Fitness": "Establishing healthy exercise routines",
                "Creative Expression": "Developing creative problem-solving skills",
                "Social Skills": "Learning teamwork and communication",
                "STEM Learning": "Building foundation for science and math courses",
                "Language Development": "Strengthening communication and literacy",
                "Cultural Connection": "Connecting with heritage and identity",
                "Emotional Regulation": "Developing coping strategies and resilience",
                "Leadership": "Building confidence to take initiative",
            }

            benefit = goal_benefits.get(child.primary_goal)
            if benefit:
                future_benefits.append(benefit)

        if not future_benefits:
            future_benefits.append("Building skills and experiences for future growth")

        return explanation, why_good_fit, considerations, future_benefits
