import numpy as np

from utils.personality import PersonalityProfile
from utils.logger import logger

def adjust_proposal_values(initial_proposal, agent=None, techniques=None):
    """
    Adjust proposal values based on gamification techniques.
    
    Args:
        initial_proposal: The initial service proposal
        agent: The agent making the proposal
        techniques: List of gamification techniques to apply
        
    Returns:
        Service: Modified service proposal
    """
    if not agent or not techniques:
        return initial_proposal
        
    proposal = initial_proposal
    context = {"proposal": proposal}

    if hasattr(agent, "provided_services"):
        context["total_services"] = sum(agent.provided_services.values())
    if hasattr(agent, "budget"):
        context["budget"] = agent.budget
    
    for technique in techniques:
        context = technique.apply(agent, context)
        
    return context.get("proposal", initial_proposal)

class GamificationTechnique():
    def __init__(self, name, personality_profile=None, effect_strength=0.5, goal=None, reward_item=None):
        """
        Initialize a gamification technique.
        
        Args:
            name (str): Name of the technique
            personality_profile (PersonalityProfile): Personality profile this technique works best with
            effect_strength (float): Base strength of the effect (0.0-1.0)
            goal (dict): Condition that must be met to earn the reward
                         Format: {"metric": "metric_name", "target": target_value, "comparison": "gt|lt|eq"}
            reward_item (Item): Item to be awarded when goal is achieved
        """
        self.name = name
        if personality_profile is None:
            self.personality_profile = PersonalityProfile()
            self.personality_profile.generate_random_personality_vector()
        else:
            self.personality_profile = personality_profile
        
        self.effect_strength = effect_strength
        self.goal = goal
        self.reward_item = reward_item

        self.achieved_by = set()
        
    def calculate_compatibility(self, agent_personality):
        """
        Calculate compatibility between technique and agent personality.
        
        Args:
            agent_personality: The agent's personality object
            
        Returns:
            float: Compatibility score (0.0-1.0)
        """
        if self.personality_profile is None or not any(agent_personality.get_personality_vector()):
            return 0.0
            
        technique_vector = self.personality_profile.get_personality_vector()
        agent_vector = agent_personality.get_personality_vector()

        distance = np.linalg.norm(technique_vector - agent_vector)
        max_distance = np.sqrt(30)
        compatibility = 1 - (distance / max_distance)
        
        logger.info(f"[{self.name}] Compatibility: {compatibility}")
        return compatibility

    def calculate_reward_compatibility(self, agent, reward_item=None):
        """
        Calculate how compatible a reward is with an agent's personality.
        
        Args:
            agent: The agent to check compatibility with
            reward_item: The reward item (optional)
            
        Returns:
            float: Reward compatibility score (0.0-1.0)
        """
        if not reward_item:
            # Some baseline interest even without rewards
            return 0.3
        
        try:
            personality = agent.personality.personality_descriptor.get("personality profile")
            
            # Achievement orientation (influenced by Conscientiousness - Achievement striving)
            achievement_drive = personality.get_facet_score("Achievement striving")
            
            # Status orientation (influenced by Extraversion - Assertiveness)
            status_orientation = personality.get_facet_score("Assertiveness")
            
            # Novelty seeking (influenced by Openness - Actions)
            novelty_seeking = personality.get_facet_score("Actions")
            
            # achievement_drive = (achievement_drive + 1) / 2
            # status_orientation = (status_orientation + 1) / 2
            # novelty_seeking = (novelty_seeking + 1) / 2
            
            # Base reward compatibility
            reward_compatibility = 0.5
            
            reward_name = reward_item.name.lower()
            
            # Trophy/badge rewards appeal to achievement and status-oriented personalities
            if "trophy" in reward_name or "badge" in reward_name:
                trophy_factor = 0.7 * achievement_drive + 0.3 * status_orientation
                reward_compatibility = 0.6 + (trophy_factor * 0.4)  # 0.6-1.0 range for trophies/badges
                logger.info(f"[{self.name}] Trophy/badge compatibility for {agent.jid}: {reward_compatibility:.2f}")
                
            # Other rewards have a moderate appeal based on novelty seeking
            else:
                other_factor = 0.6 * novelty_seeking + 0.4 * achievement_drive
                reward_compatibility = 0.4 + (other_factor * 0.4)  # 0.4-0.8 range for other rewards
                logger.info(f"[{self.name}] Other reward compatibility for {agent.jid}: {reward_compatibility:.2f}")
                
            return reward_compatibility
            
        except Exception as e:
            logger.warning(f"[{self.name}] Error calculating reward compatibility: {e}")
            # Default moderate compatibility on error
            return 0.5

    def check_goal_achievement(self, agent, metric_value):
        """
        Check if the agent has achieved the goal.
        
        Args:
            agent: The agent to check
            metric_value: Current value of the metric being tracked
            
        Returns:
            bool: True if goal is achieved, False otherwise
        """
        if not self.goal or agent.jid in self.achieved_by:
            return False
            
        target = self.goal.get("target")
        comparison = self.goal.get("comparison", "eq")
        
        achieved = False
        match comparison:
            case "gt":
                achieved = metric_value > target
            case "lt":
                achieved = metric_value < target
            case "eq":
                achieved = metric_value == target
            case "gte":
                achieved = metric_value >= target
            case "lte":
                achieved = metric_value <= target
            case _:
                logger.warning(f"[{self.name}] Unknown comparison operator: {comparison}")
                return False

        if achieved:
            self.achieved_by.add(agent.jid)
            logger.info(f"[{self.name}] Goal achieved by {agent.jid}!")
            
        return achieved

    def award_reward(self, agent):
        """
        Award the reward item to the agent.
        
        Args:
            agent: The agent to award the reward to
            
        Returns:
            bool: True if reward was awarded, False otherwise
        """
        if not self.reward_item or agent.jid not in self.achieved_by:
            return False
            
        try:
            from copy import deepcopy
            reward = deepcopy(self.reward_item)
            
            agent.inventory.add_item(reward)
            logger.info(f"[{self.name}] Awarded {reward.name} to {agent.jid}")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to award reward: {e}")
            return False

    def apply(self, agent, context):
        """
        Apply the technique to modify agent behaviour.
        
        Args:
            agent: The agent to apply the technique to
            context: Context information for the technique
        
        Returns:
            dict: Modified context
        """
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        
        combined_compatibility = (technique_compatibility * 0.7) + (reward_compatibility * 0.3)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")
        
        logger.info(f"[{self.name}] Technique compatibility: {technique_compatibility:.2f}, "
                    f"Reward compatibility: {reward_compatibility:.2f}, "
                    f"Combined: {combined_compatibility:.2f}")
        
        effective_strength = self.effect_strength * combined_compatibility

        if self.goal and "current_value" in context:
            if self.check_goal_achievement(agent, context["current_value"]):
                self.award_reward(agent)

        return context

class CompetitivePricing(GamificationTechnique):
    """Reduces prices for competitive personalities."""
    
    def apply(self, agent, context):
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        combined_compatibility = (technique_compatibility * 0.7) + (reward_compatibility * 0.3)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")
        
        proposal = context.get("proposal")
        
        # Get competitiveness from Assertiveness facet in Extraversion
        if combined_compatibility > 0.6:
            try:
                assertiveness = agent.personality.personality_descriptor.get("personality profile").get_facet_score("Assertiveness")
                competitiveness_factor = max(0.0, assertiveness) * combined_compatibility * self.effect_strength
                
                # Reduce price based on competitiveness
                if hasattr(proposal, "price") and proposal.price is not None:
                    discount = proposal.price * competitiveness_factor
                    proposal.price = max(1, proposal.price - discount)
                    logger.info(f"[{self.name}] Applied price discount of {discount:.2f} for {agent.jid}")
            except:
                pass
            
        context["proposal"] = proposal
        return context

class QualityFocus(GamificationTechnique):
    """Increases service duration for conscientious personalities."""
    
    def apply(self, agent, context):
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        combined_compatibility = (technique_compatibility * 0.7) + (reward_compatibility * 0.3)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")
        
        proposal = context.get("proposal")

        if combined_compatibility > 0.6:
            try:
                # Get quality focus from Dutifulness facet in Conscientiousness
                dutifulness = agent.personality.personality_descriptor.get("personality profile").get_facet_score("Dutifulness")
                quality_factor = max(0.0, dutifulness) * combined_compatibility * self.effect_strength
                
                # Increase duration (better quality takes more time)
                if hasattr(proposal, "duration") and proposal.duration is not None:
                    duration_increase = proposal.duration * quality_factor
                    proposal.duration = proposal.duration + duration_increase
                    logger.info(f"[{self.name}] Increased duration by {duration_increase:.2f} for {agent.jid}")
            except:
                pass
            
        context["proposal"] = proposal
        return context

class RiskTaking(GamificationTechnique):
    """Varies prices based on openness to risk."""
    
    def apply(self, agent, context):
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        combined_compatibility = (technique_compatibility * 0.7) + (reward_compatibility * 0.3)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")

        proposal = context.get("proposal")

        if combined_compatibility > 0.6:
            try:
                # Get risk-taking from Excitement seeking facet in Extraversion
                excitement_seeking = agent.personality.personality_descriptor.get("personality profile").get_facet_score("Excitement seeking")
                risk_factor = excitement_seeking * combined_compatibility * self.effect_strength
                
                # Apply random price variation based on risk tolerance
                if hasattr(proposal, "price") and proposal.price is not None:
                    import random
                    variation = (random.random() * 2 - 1) * risk_factor * proposal.price * 0.2
                    proposal.price = max(1, proposal.price + variation)
                    logger.info(f"[{self.name}] Applied price variation of {variation:.2f} for {agent.jid}")
            except:
                pass

        context["proposal"] = proposal
        return context

# Gamification techniques with rewards

class ServiceMilestone(GamificationTechnique):
    """Rewards agents for completing a certain number of services."""
    
    def apply(self, agent, context):
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        combined_compatibility = (technique_compatibility * 0.7) + (reward_compatibility * 0.3)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")

        proposal = context.get("proposal")
        
        if hasattr(agent, "provided_services") and combined_compatibility > 0.6:
            total_services = sum(agent.provided_services.values())
            
            # Add current value to context for goal checking
            context["current_value"] = total_services
            
            if self.check_goal_achievement(agent, total_services):
                self.award_reward(agent)
                
                # Celebration effect - temporary price reduction
                if hasattr(proposal, "price") and proposal.price is not None:
                    proposal.price = max(1, proposal.price * 0.9)  # 10% discount
                    logger.info(f"[{self.name}] Celebration discount applied by {agent.jid}")
        
        context["proposal"] = proposal
        return context

class PriceOptimizer(GamificationTechnique):
    """Rewards agents for maintaining competitive pricing."""
    
    def apply(self, agent, context):
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        combined_compatibility = (technique_compatibility * 0.6) + (reward_compatibility * 0.4)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")

        proposal = context.get("proposal")
        
        if hasattr(proposal, "price") and proposal.price is not None and combined_compatibility > 0.6:
            context["current_value"] = proposal.price
            
            if self.check_goal_achievement(agent, proposal.price):
                self.award_reward(agent)
                
                # Apply a small efficiency bonus to duration
                if hasattr(proposal, "duration") and proposal.duration is not None:
                    efficiency_bonus = 0.1 * combined_compatibility * self.effect_strength
                    proposal.duration = max(1, proposal.duration * (1 - efficiency_bonus))
                    logger.info(f"[{self.name}] Efficiency bonus applied by {agent.jid}")
        
        context["proposal"] = proposal
        return context

class QualityAchievement(GamificationTechnique):
    """Rewards agents for maintaining high quality standards."""
    
    def apply(self, agent, context):
        technique_compatibility = self.calculate_compatibility(agent.personality)
        reward_compatibility = self.calculate_reward_compatibility(agent, self.reward_item)
        combined_compatibility = (technique_compatibility * 0.6) + (reward_compatibility * 0.4)
        logger.info(f"[{self.name}] Combined compatibility: {combined_compatibility:.2f}")

        proposal = context.get("proposal")

        if combined_compatibility > 0.6:
            try:
                # Get quality focus from Dutifulness facet in Conscientiousness
                dutifulness = agent.personality.personality_descriptor.get("personality profile").get_facet_score("Dutifulness")
                quality_factor = max(0.0, dutifulness) * combined_compatibility * self.effect_strength
                
                context["current_value"] = quality_factor
                
                if self.check_goal_achievement(agent, quality_factor):
                    self.award_reward(agent)
                    
                    # Apply a premium pricing bonus
                    if hasattr(proposal, "price") and proposal.price is not None:
                        premium = 0.15 * combined_compatibility  # 15% premium at max compatibility
                        proposal.price = proposal.price * (1 + premium)
                        logger.info(f"[{self.name}] Quality premium applied by {agent.jid}")
            except:
                pass
            
        context["proposal"] = proposal
        return context
