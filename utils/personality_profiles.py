from utils.personality import PersonalityProfile

import numpy as np

# Facet order:
# ['Fantasy', 'Aesthetics', 'Feelings', 'Actions', 'Ideas', 'Values',
#  'Competence', 'Order', 'Dutifulness', 'Achievement striving', 'Self-Discipline', 'Deliberation',
#  'Warmth', 'Gregariousness', 'Assertiveness', 'Activity', 'Excitement seeking', 'Positive emotions',
#  'Trust', 'Straightforwardness', 'Altruism', 'Compliance', 'Modesty', 'Tender-mindedness',
#  'Anxiety', 'Angry hostility', 'Depression', 'Self-Consciousness', 'Impulsiveness', 'Vulnerability']

creative_innovator = PersonalityProfile(np.array([
    0.90, 0.85, 0.80, 0.85, 0.90, 0.88,    # Openness
    0.70, 0.60, 0.65, 0.80, 0.70, 0.60,    # Conscientiousness
    0.60, 0.65, 0.70, 0.75, 0.80, 0.70,    # Extraversion
    0.70, 0.65, 0.70, 0.68, 0.60, 0.75,    # Agreeableness
    0.30, 0.25, 0.20, 0.30, 0.40, 0.30     # Neuroticism
]))

reliable_organizer = PersonalityProfile(np.array([
    0.50, 0.45, 0.40, 0.50, 0.45, 0.50,    # Openness
    0.90, 0.85, 0.88, 0.90, 0.92, 0.90,    # Conscientiousness
    0.60, 0.55, 0.50, 0.60, 0.50, 0.55,    # Extraversion
    0.60, 0.55, 0.60, 0.60, 0.50, 0.60,    # Agreeableness
    0.30, 0.20, 0.25, 0.30, 0.30, 0.25     # Neuroticism
]))

social_butterfly = PersonalityProfile(np.array([
    0.70, 0.60, 0.70, 0.75, 0.65, 0.70,    # Openness
    0.60, 0.55, 0.60, 0.65, 0.60, 0.55,    # Conscientiousness
    0.90, 0.90, 0.85, 0.88, 0.90, 0.90,    # Extraversion
    0.85, 0.80, 0.85, 0.80, 0.75, 0.90,    # Agreeableness
    0.40, 0.35, 0.30, 0.40, 0.45, 0.40     # Neuroticism
]))

harmonious_peacemaker = PersonalityProfile(np.array([
    0.80, 0.75, 0.80, 0.80, 0.70, 0.75,    # Openness
    0.65, 0.60, 0.70, 0.60, 0.60, 0.60,    # Conscientiousness
    0.55, 0.60, 0.50, 0.50, 0.45, 0.60,    # Extraversion
    0.90, 0.85, 0.90, 0.88, 0.80, 0.90,    # Agreeableness
    0.20, 0.20, 0.15, 0.25, 0.20, 0.20     # Neuroticism
]))

anxious_introvert = PersonalityProfile(np.array([
    0.40, 0.35, 0.30, 0.40, 0.35, 0.40,    # Openness
    0.45, 0.40, 0.50, 0.45, 0.40, 0.40,    # Conscientiousness
    0.30, 0.25, 0.20, 0.30, 0.20, 0.30,    # Extraversion
    0.50, 0.45, 0.50, 0.50, 0.45, 0.50,    # Agreeableness
    0.90, 0.85, 0.88, 0.90, 0.80, 0.90     # Neuroticism
]))

competitive_pricing = PersonalityProfile(np.array([
    0.30, 0.30, 0.40, 0.50, 0.40, 0.40,    # Openness (modest)
    0.90, 0.60, 0.70, 0.95, 0.80, 0.70,    # Conscientiousness (high drive & competence)
    0.50, 0.60, 0.90, 0.70, 0.85, 0.70,    # Extraversion (assertive, thrill-seeking)
    0.50, 0.50, 0.50, 0.60, 0.40, 0.50,    # Agreeableness (medium)
    0.20, 0.30, 0.20, 0.30, 0.60, 0.30     # Neuroticism (low anxiety, some impulsiveness)
]))

quality_focus = PersonalityProfile(np.array([
    0.50, 0.50, 0.50, 0.50, 0.50, 0.50,    # Openness (neutral)
    0.95, 0.90, 0.90, 0.95, 0.90, 0.85,    # Conscientiousness (very high on all facets)
    0.40, 0.40, 0.40, 0.40, 0.40, 0.40,    # Extraversion (low–moderate)
    0.60, 0.60, 0.60, 0.60, 0.60, 0.60,    # Agreeableness (moderate)
    0.30, 0.30, 0.30, 0.30, 0.30, 0.30     # Neuroticism (low)
]))

risk_taking = PersonalityProfile(np.array([
    0.90, 0.85, 0.80, 0.90, 0.90, 0.80,    # Openness (very high—seeking new, bold ideas)
    0.40, 0.40, 0.40, 0.40, 0.40, 0.40,    # Conscientiousness (lower deliberation)
    0.70, 0.70, 0.70, 0.80, 0.95, 0.80,    # Extraversion (high excitement seeking & activity)
    0.40, 0.40, 0.40, 0.40, 0.40, 0.40,    # Agreeableness (moderate)
    0.50, 0.40, 0.40, 0.40, 0.85, 0.60     # Neuroticism (impulsive, some vulnerability)
]))

service_milestone = PersonalityProfile(np.array([
    0.50, 0.45, 0.55, 0.65, 0.50, 0.55,    # Openness (moderately open to new methods)
    0.85, 0.80, 0.75, 0.95, 0.90, 0.80,    # Conscientiousness (driven, disciplined, achievement-oriented)
    0.70, 0.65, 0.60, 0.70, 0.65, 0.75,    # Extraversion (activity, positive emotions, moderate assertiveness)
    0.75, 0.70, 0.65, 0.70, 0.60, 0.70,    # Agreeableness (compliant, altruistic, trustworthy)
    0.25, 0.20, 0.20, 0.30, 0.30, 0.25     # Neuroticism (emotionally stable)
]))

price_optimizer = PersonalityProfile(np.array([
    0.40, 0.35, 0.40, 0.50, 0.45, 0.45,    # Openness (practical rather than highly imaginative)
    0.90, 0.85, 0.80, 0.90, 0.85, 0.85,    # Conscientiousness (orderly, disciplined, deliberative)
    0.55, 0.50, 0.60, 0.60, 0.55, 0.60,    # Extraversion (moderate activity & positive affect)
    0.65, 0.60, 0.60, 0.65, 0.55, 0.60,    # Agreeableness (fair, straightforward, compliant)
    0.30, 0.25, 0.25, 0.35, 0.35, 0.30     # Neuroticism (low anxiety, low impulsiveness)
]))

quality_achievement = PersonalityProfile(np.array([
    0.60, 0.60, 0.65, 0.55, 0.60, 0.65,    # Openness (values excellence, thoughtful approaches)
    0.95, 0.90, 0.92, 0.90, 0.88, 0.90,    # Conscientiousness (extremely high competence & dutifulness)
    0.45, 0.40, 0.45, 0.50, 0.45, 0.50,    # Extraversion (prefers steady, reliable interactions)
    0.70, 0.65, 0.70, 0.75, 0.60, 0.70,    # Agreeableness (trusting, compliant, tender-minded)
    0.20, 0.20, 0.15, 0.25, 0.20, 0.20     # Neuroticism (calm, low vulnerability)
]))

# Anti-gamification personality profile - designed to be opposite to gamification techniques
anti_gamification = PersonalityProfile(np.array([
    # Openness (opposite of risk_taking and creative profiles)
    0.10, 0.15, 0.20, 0.10, 0.10, 0.20,    
    # Conscientiousness (opposite of quality_focus and achievement profiles)
    0.05, 0.10, 0.10, 0.05, 0.10, 0.15,    
    # Extraversion (opposite of competitive and social profiles)
    0.30, 0.30, 0.10, 0.20, 0.05, 0.20,    
    # Agreeableness (moderate values won't strongly affect cosine similarity)
    0.40, 0.40, 0.40, 0.40, 0.90, 0.40,    
    # Neuroticism (high values opposite to most gamification profiles)
    0.90, 0.90, 0.90, 0.90, 0.90, 0.90     
]))
