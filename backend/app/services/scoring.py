"""
Scoring algorithm for activity recommendations.

Formula: total_score = fit_score (50%) + practical_score (30%) + goals_score (20%)
"""
import logging
from datetime import date, datetime
from typing import Any, Optional

from app.models.activity import Activity
from app.models.child import ChildProfile
from app.models.family import Family

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Recommendation scoring engine.

    Implements the three-component scoring system:
    1. Fit Score (50%): Age, temperament, prerequisites
    2. Practical Score (30%): Commute, schedule, budget
    3. Goals Score (20%): Alignment with child's goals
    """

    def __init__(self, child_profile: ChildProfile, family: Family):
        """
        Initialize scoring engine.

        Args:
            child_profile: Child profile to score for
            family: Family profile with budget and location
        """
        self.child = child_profile
        self.family = family

    def calculate_total_score(
        self,
        activity: Activity,
    ) -> tuple[float, dict[str, Any]]:
        """
        Calculate total recommendation score for an activity.

        Args:
            activity: Activity to score

        Returns:
            Tuple of (total_score, score_breakdown)
        """
        # Calculate component scores
        fit_score, fit_details = self.calculate_fit_score(activity)
        practical_score, practical_details = self.calculate_practical_score(activity)
        goals_score, goals_details = self.calculate_goals_score(activity)

        # Weighted total (0-100 scale)
        total_score = (
            fit_score * 0.50 +
            practical_score * 0.30 +
            goals_score * 0.20
        )

        score_breakdown = {
            "fit": fit_details,
            "practical": practical_details,
            "goals": goals_details,
        }

        return total_score, score_breakdown

    def calculate_fit_score(self, activity: Activity) -> tuple[float, dict[str, float]]:
        """
        Calculate fit score (50% of total).

        Components:
        - Age band match (15%)
        - Intensity match (10%)
        - Sensory tolerance (10%)
        - Team vs solo (5%)
        - Prerequisites (5%)
        - Neurodiversity flags (5%)

        Args:
            activity: Activity to score

        Returns:
            Tuple of (fit_score, fit_details)
        """
        details = {}

        # Age band match (15 points max)
        details["age_band_match"] = self._score_age_match(activity)

        # Intensity match (10 points max)
        details["intensity_match"] = self._score_intensity_match(activity)

        # Sensory tolerance (10 points max)
        details["sensory_tolerance"] = self._score_sensory_match(activity)

        # Team vs solo preference (5 points max)
        details["team_vs_solo"] = self._score_social_preference(activity)

        # Prerequisites (5 points max - binary)
        details["prerequisites"] = self._score_prerequisites(activity)

        # Neurodiversity considerations (5 points max)
        details["neurodiversity"] = self._score_neurodiversity(activity)

        # Total fit score (sum of components, max 50)
        fit_score = sum(details.values())

        return fit_score, details

    def calculate_practical_score(self, activity: Activity) -> tuple[float, dict[str, float]]:
        """
        Calculate practical score (30% of total).

        Components:
        - Commute time (10%)
        - Schedule fit (10%)
        - Price vs budget (5%)
        - Scholarship bonus (2.5%)
        - Transit accessibility (2.5%)

        Args:
            activity: Activity to score

        Returns:
            Tuple of (practical_score, practical_details)
        """
        details = {}

        # Commute time (10 points max)
        details["commute_time"] = self._score_commute(activity)

        # Schedule fit (10 points max)
        details["schedule_fit"] = self._score_schedule(activity)

        # Price vs budget (5 points max)
        details["price_vs_budget"] = self._score_price(activity)

        # Scholarship bonus (2.5 points)
        details["scholarship_bonus"] = 2.5 if activity.has_scholarship else 0.0

        # Transit accessibility (2.5 points)
        details["transit_accessible"] = self._score_transit(activity)

        # Total practical score (max 30)
        practical_score = sum(details.values())

        return practical_score, details

    def calculate_goals_score(self, activity: Activity) -> tuple[float, dict[str, float]]:
        """
        Calculate goals alignment score (20% of total).

        Components:
        - Primary goal (10%)
        - Secondary goal (6%)
        - Tertiary goal (4%)

        Args:
            activity: Activity to score

        Returns:
            Tuple of (goals_score, goals_details)
        """
        details = {}

        # Primary goal (10 points max)
        details["primary_goal"] = self._score_goal_alignment(
            activity,
            self.child.primary_goal,
            max_points=10.0,
        )

        # Secondary goal (6 points max)
        details["secondary_goal"] = self._score_goal_alignment(
            activity,
            self.child.secondary_goal,
            max_points=6.0,
        )

        # Tertiary goal (4 points max)
        details["tertiary_goal"] = self._score_goal_alignment(
            activity,
            self.child.tertiary_goal,
            max_points=4.0,
        )

        # Total goals score (max 20)
        goals_score = sum(details.values())

        return goals_score, details

    # Helper methods for component scoring

    def _score_age_match(self, activity: Activity) -> float:
        """Score age band match (0-15 points)."""
        child_age = self.child.age

        # Perfect match: age is within activity's range
        if activity.min_age and activity.max_age:
            if activity.min_age <= child_age <= activity.max_age:
                return 15.0
            # Close match (±1 year)
            elif (activity.min_age - 1 <= child_age <= activity.max_age + 1):
                return 10.0
            else:
                return 0.0

        # No age restrictions
        if not activity.min_age and not activity.max_age:
            return 12.0

        # Partial match
        if activity.min_age and child_age >= activity.min_age:
            return 10.0
        if activity.max_age and child_age <= activity.max_age:
            return 10.0

        return 5.0

    def _score_intensity_match(self, activity: Activity) -> float:
        """Score intensity level match (0-10 points)."""
        if not self.child.temperament:
            return 5.0  # Neutral if no temperament data

        child_intensity = self.child.temperament.get("intensity_preference", "moderate")
        activity_intensity = activity.attributes.get("intensity_level", "moderate") if activity.attributes else "moderate"

        # Perfect match
        if child_intensity == activity_intensity:
            return 10.0

        # Adjacent match (e.g., moderate child with low or high activity)
        intensity_order = ["low", "moderate", "high"]
        try:
            child_idx = intensity_order.index(child_intensity)
            activity_idx = intensity_order.index(activity_intensity)
            diff = abs(child_idx - activity_idx)

            if diff == 1:
                return 6.0
            else:
                return 2.0
        except ValueError:
            return 5.0

    def _score_sensory_match(self, activity: Activity) -> float:
        """Score sensory load match (0-10 points)."""
        if not self.child.temperament:
            return 5.0

        child_sensitivity = self.child.temperament.get("sensory_sensitivity", "medium")
        activity_sensory = activity.attributes.get("sensory_load", "medium") if activity.attributes else "medium"

        # High sensitivity child needs low sensory load
        if child_sensitivity == "high" and activity_sensory == "low":
            return 10.0
        elif child_sensitivity == "high" and activity_sensory == "medium":
            return 6.0
        elif child_sensitivity == "high" and activity_sensory == "high":
            return 2.0

        # Medium sensitivity is flexible
        if child_sensitivity == "medium":
            return 8.0

        # Low sensitivity is fine with anything
        if child_sensitivity == "low":
            return 10.0

        return 5.0

    def _score_social_preference(self, activity: Activity) -> float:
        """Score social environment match (0-5 points)."""
        if not self.child.temperament:
            return 2.5

        child_pref = self.child.temperament.get("social_preference", "small_group")
        activity_type = activity.attributes.get("team_vs_solo", "small_group") if activity.attributes else "small_group"

        if child_pref == activity_type:
            return 5.0
        else:
            return 2.0

    def _score_prerequisites(self, activity: Activity) -> float:
        """Score prerequisites (0 or 5 points - binary)."""
        # TODO: Implement prerequisite checking
        # For now, assume no prerequisites or child meets them
        return 5.0

    def _score_neurodiversity(self, activity: Activity) -> float:
        """Score neurodiversity considerations (0-5 points)."""
        if not self.child.constraints:
            return 5.0

        neurodiversity_notes = self.child.constraints.get("neurodiversity_notes", "")

        # If child has neurodiversity notes, prefer neurodiversity-friendly activities
        if neurodiversity_notes:
            is_neuro_friendly = activity.attributes.get("neurodiversity_friendly", False) if activity.attributes else False
            if is_neuro_friendly:
                return 5.0
            else:
                return 2.0

        return 5.0

    def _score_commute(self, activity: Activity) -> float:
        """Score commute time (0-10 points)."""
        # TODO: Implement actual distance/time calculation using PostGIS
        # For now, assume reasonable commute
        return 8.0

    def _score_schedule(self, activity: Activity) -> float:
        """Score schedule compatibility (0-10 points)."""
        # TODO: Implement schedule window matching
        # For now, assume good schedule fit
        return 8.0

    def _score_price(self, activity: Activity) -> float:
        """Score price vs budget (0-5 points)."""
        if not activity.price_cents or not self.family.budget_monthly:
            return 3.0  # Neutral if no price/budget data

        # Assume typical activity runs for 4 weeks/month
        monthly_cost = activity.price_cents * 4 / 100  # Convert to dollars

        if monthly_cost <= self.family.budget_monthly * 0.3:  # <30% of budget
            return 5.0
        elif monthly_cost <= self.family.budget_monthly * 0.5:  # <50% of budget
            return 3.0
        elif monthly_cost <= self.family.budget_monthly:  # Within budget
            return 2.0
        else:  # Over budget
            return 0.0

    def _score_transit(self, activity: Activity) -> float:
        """Score transit accessibility (0-2.5 points)."""
        # TODO: Check venue transit accessibility
        return 2.0

    def _score_goal_alignment(self, activity: Activity, goal: Optional[str], max_points: float) -> float:
        """
        Score how well activity aligns with a specific goal.

        Args:
            activity: Activity to score
            goal: Goal to check alignment for
            max_points: Maximum points for this goal level

        Returns:
            Score (0 to max_points)
        """
        if not goal:
            return 0.0

        # TODO: Implement proper goal-to-activity-type mapping
        # For now, use simple heuristics

        activity_type = activity.activity_type or ""

        # Simple goal mapping (to be replaced with proper taxonomy)
        goal_mappings = {
            "Build Confidence": ["arts", "music", "theatre", "martial_arts"],
            "College Prep Skills": ["stem", "academic", "robotics", "coding"],
            "Physical Fitness": ["sports", "swimming", "dance", "martial_arts"],
            "Creative Expression": ["arts", "music", "theatre", "crafts"],
            "Social Skills": ["team_sports", "scouts", "group_activities"],
            "STEM Learning": ["stem", "robotics", "coding", "science"],
            "Language Development": ["language", "reading", "debate", "theatre"],
            "Cultural Connection": ["cultural", "language", "music", "dance"],
            "Emotional Regulation": ["mindfulness", "yoga", "martial_arts", "nature"],
            "Leadership": ["scouts", "team_captain", "student_government"],
        }

        aligned_types = goal_mappings.get(goal, [])

        # Check if activity type matches goal
        for aligned_type in aligned_types:
            if aligned_type in activity_type.lower():
                return max_points

        # Partial match
        return max_points * 0.3
