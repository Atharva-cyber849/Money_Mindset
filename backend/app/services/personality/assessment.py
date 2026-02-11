"""
Financial Personality Assessment Engine
Identifies user money psychology through quiz + behavioral analysis
"""
from typing import Dict, List, Optional
from datetime import datetime


class FinancialPersonalityAssessment:
    """Assess user financial personality and behavior patterns"""
    
    # Core personality dimensions (0-10 scale)
    DIMENSIONS = {
        'risk_tolerance': {
            'low': (0, 3),
            'medium': (3, 7),
            'high': (7, 10)
        },
        'time_horizon': {
            'short_term': (0, 3),
            'balanced': (3, 7),
            'long_term': (7, 10)
        },
        'spending_trigger': {
            'emotional': (0, 3),
            'mixed': (3, 7),
            'rational': (7, 10)
        },
        'mindset': {
            'scarcity': (0, 3),
            'neutral': (3, 7),
            'abundance': (7, 10)
        },
        'decision_style': {
            'impulsive': (0, 3),
            'balanced': (3, 7),
            'analytical': (7, 10)
        },
        'stress_response': {
            'panic': (0, 3),
            'moderate': (3, 7),
            'calm': (7, 10)
        }
    }
    
    # Personality archetypes based on dimension combinations
    ARCHETYPES = {
        'cautious_planner': {
            'description': 'Values security, plans meticulously, avoids risk',
            'strengths': ['Disciplined saving', 'Risk awareness', 'Long-term planning'],
            'challenges': ['May miss opportunities', 'Analysis paralysis', 'Overly conservative'],
            'learning_focus': ['Calculated risk-taking', 'Opportunity cost', 'Growth mindset']
        },
        'optimistic_risk_taker': {
            'description': 'Confident, seeks growth, embraces uncertainty',
            'strengths': ['Seizes opportunities', 'Growth-oriented', 'Resilient'],
            'challenges': ['May overestimate abilities', 'Underestimates risk', 'Impulsive'],
            'learning_focus': ['Risk management', 'Diversification', 'Patience']
        },
        'balanced_builder': {
            'description': 'Pragmatic, balanced approach, steady progress',
            'strengths': ['Consistent execution', 'Realistic goals', 'Adaptable'],
            'challenges': ['May lack conviction', 'Slower growth', 'Indecisive at times'],
            'learning_focus': ['Building conviction', 'Accelerated growth', 'Decision confidence']
        },
        'anxious_avoider': {
            'description': 'Stressed by finances, avoids decisions, reactive',
            'strengths': ['Aware of concerns', 'Cautious', 'Can learn quickly'],
            'challenges': ['Procrastination', 'Emotional decisions', 'Short-term focus'],
            'learning_focus': ['Stress management', 'Action over avoidance', 'Long-term thinking']
        }
    }
    
    # Quiz questions mapped to dimensions
    QUIZ_QUESTIONS = [
        {
            'id': 'q1',
            'question': 'You receive an unexpected $5,000. What do you do first?',
            'options': [
                {'text': 'Put it all in savings immediately', 'scores': {'risk_tolerance': 2, 'decision_style': 8, 'stress_response': 8}},
                {'text': 'Research investment opportunities', 'scores': {'risk_tolerance': 7, 'decision_style': 9, 'time_horizon': 8}},
                {'text': 'Treat myself, then save the rest', 'scores': {'risk_tolerance': 5, 'spending_trigger': 4, 'decision_style': 5}},
                {'text': 'Feel anxious about what to do', 'scores': {'stress_response': 2, 'decision_style': 3, 'risk_tolerance': 3}}
            ]
        },
        {
            'id': 'q2',
            'question': 'The stock market drops 20% and your portfolio is down $10,000. You:',
            'options': [
                {'text': 'Panic and sell everything', 'scores': {'stress_response': 1, 'risk_tolerance': 2, 'time_horizon': 2}},
                {'text': 'Feel worried but hold steady', 'scores': {'stress_response': 5, 'risk_tolerance': 6, 'decision_style': 6}},
                {'text': 'See buying opportunity, invest more', 'scores': {'stress_response': 9, 'risk_tolerance': 9, 'time_horizon': 9}},
                {'text': 'Check it obsessively but do nothing', 'scores': {'stress_response': 3, 'risk_tolerance': 5, 'decision_style': 4}}
            ]
        },
        {
            'id': 'q3',
            'question': 'What best describes your financial planning timeframe?',
            'options': [
                {'text': 'I focus on this month/week', 'scores': {'time_horizon': 2, 'decision_style': 3, 'mindset': 3}},
                {'text': 'I plan 1-2 years ahead', 'scores': {'time_horizon': 5, 'decision_style': 6, 'mindset': 5}},
                {'text': 'I think about 5-10 years out', 'scores': {'time_horizon': 8, 'decision_style': 8, 'mindset': 7}},
                {'text': 'I plan for decades ahead', 'scores': {'time_horizon': 10, 'decision_style': 9, 'mindset': 8}}
            ]
        },
        {
            'id': 'q4',
            'question': 'You see your friend buy something expensive. You:',
            'options': [
                {'text': 'Feel pressure to keep up', 'scores': {'spending_trigger': 2, 'mindset': 3, 'decision_style': 3}},
                {'text': 'Feel happy for them, unaffected', 'scores': {'spending_trigger': 8, 'mindset': 7, 'decision_style': 7}},
                {'text': 'Wonder if I should buy something too', 'scores': {'spending_trigger': 4, 'mindset': 4, 'decision_style': 4}},
                {'text': 'Feel relieved I saved my money', 'scores': {'spending_trigger': 9, 'mindset': 6, 'decision_style': 8}}
            ]
        },
        {
            'id': 'q5',
            'question': 'You have a bad day at work. What happens to your spending?',
            'options': [
                {'text': 'I spend to feel better (retail therapy)', 'scores': {'spending_trigger': 1, 'stress_response': 3, 'decision_style': 2}},
                {'text': 'No change in spending', 'scores': {'spending_trigger': 9, 'stress_response': 7, 'decision_style': 8}},
                {'text': 'I might splurge a little', 'scores': {'spending_trigger': 4, 'stress_response': 5, 'decision_style': 4}},
                {'text': 'I actually spend less when stressed', 'scores': {'spending_trigger': 7, 'stress_response': 6, 'mindset': 6}}
            ]
        },
        {
            'id': 'q6',
            'question': 'How do you feel about taking financial risks for higher returns?',
            'options': [
                {'text': 'Very uncomfortable, prefer safety', 'scores': {'risk_tolerance': 2, 'stress_response': 4, 'time_horizon': 4}},
                {'text': 'Somewhat open if returns justify risk', 'scores': {'risk_tolerance': 6, 'stress_response': 6, 'decision_style': 7}},
                {'text': 'Excited by high-risk opportunities', 'scores': {'risk_tolerance': 9, 'stress_response': 8, 'mindset': 7}},
                {'text': 'Avoid thinking about it', 'scores': {'risk_tolerance': 3, 'stress_response': 2, 'decision_style': 2}}
            ]
        },
        {
            'id': 'q7',
            'question': 'When making a major financial decision, you:',
            'options': [
                {'text': 'Research extensively, take weeks', 'scores': {'decision_style': 9, 'risk_tolerance': 5, 'stress_response': 6}},
                {'text': 'Go with gut feeling quickly', 'scores': {'decision_style': 2, 'risk_tolerance': 7, 'stress_response': 7}},
                {'text': 'Balance research with intuition', 'scores': {'decision_style': 7, 'risk_tolerance': 6, 'stress_response': 6}},
                {'text': 'Delay/avoid the decision', 'scores': {'decision_style': 3, 'risk_tolerance': 3, 'stress_response': 2}}
            ]
        },
        {
            'id': 'q8',
            'question': 'What phrase resonates most with you?',
            'options': [
                {'text': 'A bird in the hand is worth two in the bush', 'scores': {'risk_tolerance': 3, 'mindset': 4, 'time_horizon': 4}},
                {'text': 'Fortune favors the bold', 'scores': {'risk_tolerance': 9, 'mindset': 8, 'time_horizon': 7}},
                {'text': 'Slow and steady wins the race', 'scores': {'risk_tolerance': 5, 'mindset': 6, 'time_horizon': 8}},
                {'text': 'Money is the root of all evil', 'scores': {'mindset': 2, 'risk_tolerance': 3, 'stress_response': 3}}
            ]
        },
        {
            'id': 'q9',
            'question': 'You compare your savings to a friend who has more. You feel:',
            'options': [
                {'text': 'Motivated to do better', 'scores': {'mindset': 7, 'stress_response': 7, 'decision_style': 6}},
                {'text': 'Inadequate and discouraged', 'scores': {'mindset': 2, 'stress_response': 3, 'decision_style': 4}},
                {'text': 'Happy for them, focused on my path', 'scores': {'mindset': 9, 'stress_response': 8, 'decision_style': 8}},
                {'text': 'Curious about their strategy', 'scores': {'mindset': 6, 'decision_style': 8, 'time_horizon': 6}}
            ]
        },
        {
            'id': 'q10',
            'question': 'If you could only choose one financial goal, it would be:',
            'options': [
                {'text': 'Never worry about money', 'scores': {'risk_tolerance': 4, 'mindset': 5, 'time_horizon': 6}},
                {'text': 'Build significant wealth', 'scores': {'risk_tolerance': 7, 'mindset': 7, 'time_horizon': 9}},
                {'text': 'Enjoy life today', 'scores': {'risk_tolerance': 5, 'mindset': 6, 'time_horizon': 3}},
                {'text': 'Have enough for emergencies', 'scores': {'risk_tolerance': 3, 'mindset': 4, 'time_horizon': 5}}
            ]
        },
        {
            'id': 'q11',
            'question': 'When you think about retirement (or any long-term goal):',
            'options': [
                {'text': 'It feels too far away to worry about', 'scores': {'time_horizon': 2, 'decision_style': 3, 'mindset': 4}},
                {'text': 'I have a detailed plan already', 'scores': {'time_horizon': 9, 'decision_style': 9, 'risk_tolerance': 6}},
                {'text': 'I know I should plan but haven\'t', 'scores': {'time_horizon': 4, 'decision_style': 4, 'stress_response': 4}},
                {'text': 'I\'m actively working toward it', 'scores': {'time_horizon': 8, 'decision_style': 8, 'mindset': 7}}
            ]
        },
        {
            'id': 'q12',
            'question': 'You just learned about a "hot" investment opportunity. You:',
            'options': [
                {'text': 'Jump in quickly before missing out', 'scores': {'risk_tolerance': 8, 'decision_style': 2, 'stress_response': 6}},
                {'text': 'Research thoroughly first', 'scores': {'risk_tolerance': 6, 'decision_style': 9, 'stress_response': 7}},
                {'text': 'Feel skeptical, probably ignore it', 'scores': {'risk_tolerance': 3, 'decision_style': 6, 'stress_response': 5}},
                {'text': 'Ask friends what they think', 'scores': {'risk_tolerance': 5, 'decision_style': 4, 'stress_response': 5}}
            ]
        }
    ]
    
    def calculate_dimension_scores(self, responses: List[Dict]) -> Dict[str, float]:
        """
        Calculate scores for each personality dimension based on quiz responses
        
        Args:
            responses: List of {question_id, selected_option_index}
            
        Returns:
            Dict of dimension names to scores (0-10 scale)
        """
        dimension_totals = {dim: [] for dim in self.DIMENSIONS.keys()}
        
        for response in responses:
            question_id = response['question_id']
            option_index = response['selected_option']
            
            # Find the question and selected option
            question = next((q for q in self.QUIZ_QUESTIONS if q['id'] == question_id), None)
            if not question or option_index >= len(question['options']):
                continue
                
            option = question['options'][option_index]
            scores = option.get('scores', {})
            
            # Add scores to dimensions
            for dimension, score in scores.items():
                if dimension in dimension_totals:
                    dimension_totals[dimension].append(score)
        
        # Average the scores for each dimension
        dimension_scores = {}
        for dimension, scores in dimension_totals.items():
            if scores:
                dimension_scores[dimension] = round(sum(scores) / len(scores), 2)
            else:
                dimension_scores[dimension] = 5.0  # Default neutral
                
        return dimension_scores
    
    def determine_archetype(self, dimension_scores: Dict[str, float]) -> str:
        """
        Determine personality archetype based on dimension scores
        
        Logic:
        - Cautious Planner: Low risk (0-4), high planning (7-10), calm stress response
        - Optimistic Risk-Taker: High risk (7-10), confident mindset, high time horizon
        - Balanced Builder: Most scores in middle range (4-7)
        - Anxious Avoider: Low stress response (0-4), short time horizon, emotional triggers
        """
        risk = dimension_scores.get('risk_tolerance', 5)
        time = dimension_scores.get('time_horizon', 5)
        stress = dimension_scores.get('stress_response', 5)
        mindset = dimension_scores.get('mindset', 5)
        decision = dimension_scores.get('decision_style', 5)
        
        # Anxious Avoider: High stress, avoidant behavior
        if stress <= 4 and decision <= 4 and time <= 4:
            return 'anxious_avoider'
        
        # Cautious Planner: Low risk, high analytical, calm
        if risk <= 4 and decision >= 7 and stress >= 6:
            return 'cautious_planner'
        
        # Optimistic Risk-Taker: High risk, abundance mindset, long-term
        if risk >= 7 and mindset >= 6 and time >= 6:
            return 'optimistic_risk_taker'
        
        # Balanced Builder: Everything in middle range
        middle_scores = sum(1 for s in dimension_scores.values() if 4 <= s <= 7)
        if middle_scores >= 4:
            return 'balanced_builder'
        
        # Default to balanced if unclear
        return 'balanced_builder'
    
    def generate_insights(self, archetype: str, dimension_scores: Dict[str, float]) -> Dict:
        """Generate personalized insights based on personality"""
        archetype_info = self.ARCHETYPES.get(archetype, self.ARCHETYPES['balanced_builder'])
        
        # Identify strongest and weakest dimensions
        strongest = max(dimension_scores.items(), key=lambda x: x[1])
        weakest = min(dimension_scores.items(), key=lambda x: x[1])
        
        return {
            'archetype': archetype,
            'archetype_name': archetype.replace('_', ' ').title(),
            'description': archetype_info['description'],
            'strengths': archetype_info['strengths'],
            'challenges': archetype_info['challenges'],
            'learning_focus': archetype_info['learning_focus'],
            'strongest_dimension': {
                'name': strongest[0].replace('_', ' ').title(),
                'score': strongest[1]
            },
            'weakest_dimension': {
                'name': weakest[0].replace('_', ' ').title(),
                'score': weakest[1]
            },
            'dimension_scores': dimension_scores
        }
    
    def assess_personality(self, responses: List[Dict]) -> Dict:
        """
        Complete personality assessment
        
        Args:
            responses: List of quiz responses
            
        Returns:
            Complete personality profile with insights
        """
        # Calculate dimension scores
        dimension_scores = self.calculate_dimension_scores(responses)
        
        # Determine archetype
        archetype = self.determine_archetype(dimension_scores)
        
        # Generate insights
        insights = self.generate_insights(archetype, dimension_scores)
        
        # Add confidence score (based on response consistency)
        confidence = self._calculate_confidence(dimension_scores)
        insights['confidence_score'] = confidence
        
        return insights
    
    def _calculate_confidence(self, dimension_scores: Dict[str, float]) -> float:
        """
        Calculate how confident we are in the assessment
        Based on score variance (consistent scores = high confidence)
        """
        scores = list(dimension_scores.values())
        if not scores:
            return 0.5
            
        # Calculate variance
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        
        # High variance = low confidence (inconsistent responses)
        # Normalize to 0-1 scale
        confidence = max(0.3, min(1.0, 1.0 - (variance / 25)))
        return round(confidence, 2)
    
    def get_quiz_questions(self) -> List[Dict]:
        """Get all quiz questions for frontend"""
        return [
            {
                'id': q['id'],
                'question': q['question'],
                'options': [opt['text'] for opt in q['options']]
            }
            for q in self.QUIZ_QUESTIONS
        ]


# Singleton instance
personality_assessment_service = FinancialPersonalityAssessment()
