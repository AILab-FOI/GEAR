import numpy as np


import numpy as np

class PersonalityProfile:
    # Define the facets for each of the five factors
    facets = {
        'Openness': ['Fantasy', 'Aesthetics', 'Feelings', 'Actions', 'Ideas', 'Values'],
        'Conscientiousness': ['Competence', 'Order', 'Dutifulness', 'Achievement striving', 'Self-Discipline', 'Deliberation'],
        'Extraversion': ['Warmth', 'Gregariousness', 'Assertiveness', 'Activity', 'Excitement seeking', 'Positive emotions'],
        'Agreeableness': ['Trust', 'Straightforwardness', 'Altruism', 'Compliance', 'Modesty', 'Tender-mindedness'],
        'Neuroticism': ['Anxiety', 'Angry hostility', 'Depression', 'Self-Consciousness', 'Impulsiveness', 'Vulnerability']
    }

    # Create a mapping from facet names to their indices
    facet_to_index = {}
    for factor, facets_list in facets.items():
        for index, facet in enumerate(facets_list):
            facet_to_index[facet] = index + list(facets.keys()).index(factor) * 6

    def __init__(self, scores: list=None):
        """
        Initialize the personality profile with scores for each facet.

        Args:
            scores (list, optional): A list of scores for each facet. Defaults to None.
        """
        if scores is None:
            scores = np.zeros(30)  # 5 factors * 6 facets each
        else:
            assert len(scores) == 30, "Scores must be a list or array of length 30."
            scores = np.array(scores)

        self.scores = scores

    def get_facet_score(self, facet: str) -> float:
        """
        Get the score for a specific facet using the facet name.

        Args:
            facet (str): The name of the facet.

        Returns:
            float: The score for the facet.
        """
        assert facet in self.facet_to_index, "Facet not found."
        return self.scores[self.facet_to_index.get(facet)]

    def set_facet_score(self, facet: str, score: float):
        """
        Set the score for a specific facet using the facet name.

        Args:
            facet (str): The name of the facet.
            score (float): The score to set for the facet.
        """
        assert -1 <= score <= 1, "Score must be between 0 and 5."
        self.scores[self.facet_to_index.get(facet)] = score

    def get_factor_scores(self, factor: str) -> np.ndarray:
        """
        Get the scores for all facets of a specific factor.

        Args:
            factor (str): The name of the factor.

        Returns:
            np.ndarray: An array of scores for the facets of the factor.
        """
        assert factor in self.facets, "Factor not found."
        start_index = list(self.facets.keys()).index(factor) * 6
        end_index = start_index + 6
        return self.scores[start_index:end_index]

    def set_factor_scores(self, factor: str, scores: list):
        """
        Set the scores for all facets of a specific factor.

        Args:
            factor (str): The name of the factor.
            scores (list): A list of scores for the facets of the factor.
        """
        assert factor in self.facets, "Factor not found."
        assert len(scores) == 6, "Scores must be a list or array of length 6."
        start_index = list(self.facets.keys()).index(factor) * 6
        end_index = start_index + 6
        self.scores[start_index:end_index] = scores

    def get_personality_vector(self) -> np.ndarray:
        """
        Get the personality vector.

        Returns:
            np.ndarray: An array of scores for all facets.
        """
        return self.scores

    def set_personality_vector(self, scores: list):
        """
        Set the personality vector.

        Args:
            scores (list): A list of scores for all facets.
        """
        assert len(scores) == 30, "Scores must be a list or array of length 30."
        self.scores = scores

    def generate_random_personality_vector(self):
        self.scores = np.random.rand(30)

    def __str__(self):
        return str(self.scores)

    def __repr__(self):
        return repr(self.scores)

    def __eq__(self, other):
        if isinstance(other, PersonalityProfile):
            return np.array_equal(self.scores, other.scores)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Personality:
    def __init__(self, age: int=27, gender: float=0, personality_scores: list=None, personality: dict[str, int | float | list] = None):
        """
        Initialize the personality with age, gender, and personality scores.

        Args:
            age (int, optional): The age of the personality. Defaults to 27.
            gender (float, optional): The gender of the personality. Defaults to 0.
            personality_scores (list, optional): A list of scores for all facets. Defaults to None.
        """
        assert 0 <= gender <= 1, "Gender must be between 0 and 1."
        assert age >= 0, "Age must be positive."
        assert personality_scores is None or len(personality_scores) == 30, "Personality scores must be a list or array of length 30."

        self.personality_descriptor = personality or {
            "age": age,
            "gender": gender,
            "personality_profile": PersonalityProfile(personality_scores)
        }

    def get_personality_descriptor(self) -> dict[str, int | float | PersonalityProfile]:
        """
        Get the personality descriptor.

        Returns:
            dict: A dictionary containing the age, gender, and personality profile.
        """
        return self.personality_descriptor

    def set_personality_descriptor(self, personality_descriptor: dict[str, int | float | PersonalityProfile]):
        """
        Set the personality descriptor.

        Args:
            personality_descriptor (dict): A dictionary containing the age, gender, and personality profile.
        """
        assert "age" in personality_descriptor, "Age must be provided."
        assert "gender" in personality_descriptor, "Gender must be provided."
        assert "personality_profile" in personality_descriptor, "Personality profile must be provided."
        self.personality_descriptor = personality_descriptor

    def get_personality_vector(self) -> np.ndarray:
        """
        Get the personality vector.

        Returns:
            np.ndarray: An array of scores for all facets.
        """
        return self.personality_descriptor.get("personality_profile").get_personality_vector()

    def set_personality_vector(self, scores: list):
        """
        Set the personality vector.

        Args:
            scores (list): A list of scores for all facets.
        """
        self.personality_descriptor.get("personality_profile").set_personality_vector(scores)

    def generate_random_personality_vector(self):
        self.personality_descriptor.get("personality_profile").generate_random_personality_vector()

    def __str__(self):
        return str(self.personality_descriptor)

    def __repr__(self):
        return repr(self.personality_descriptor)
