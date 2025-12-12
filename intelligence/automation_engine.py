"""
Automation Engine
Executes automated actions based on detected patterns
"""
import jdatetime
from typing import List, Dict, Optional, Any
from database import DatabaseManager
from intelligence.pattern_detector import PatternDetector


class AutomationEngine:
    """Executes automated actions based on patterns"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
        self.pattern_detector = PatternDetector(db_path)
    
    def create_automation_rule(
        self,
        rule_name: str,
        rule_type: str,
        pattern: Dict[str, Any],
        action: Dict[str, Any],
        enabled: bool = True
    ) -> int:
        """
        Create an automation rule
        
        Args:
            rule_name: Name of the rule
            rule_type: Type of rule ('recurring_event', 'recurring_task', 'template')
            pattern: Pattern definition
            action: Action to take
            enabled: Whether rule is enabled
            
        Returns:
            Rule ID (stored in user_preferences table)
        """
        import json
        
        rule_data = {
            'name': rule_name,
            'type': rule_type,
            'pattern': pattern,
            'action': action,
            'enabled': enabled
        }
        
        # Store in user_preferences table
        from intelligence.learning_engine import LearningEngine
        learning_engine = LearningEngine(self.db_path)
        
        learning_engine.learn_preference(
            'automation_rule',
            rule_name,
            json.dumps(rule_data, ensure_ascii=False),
            confidence=1.0
        )
        
        return hash(rule_name)  # Simple ID generation
    
    def get_automation_rules(
        self,
        enabled_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all automation rules
        
        Args:
            enabled_only: Return only enabled rules
            
        Returns:
            List of automation rules
        """
        from intelligence.learning_engine import LearningEngine
        import json
        
        learning_engine = LearningEngine(self.db_path)
        preferences = learning_engine.get_all_preferences('automation_rule')
        
        rules = []
        for key, pref_data in preferences.get('automation_rule', {}).items():
            try:
                rule_data = json.loads(pref_data['value'])
                if not enabled_only or rule_data.get('enabled', True):
                    rules.append(rule_data)
            except:
                continue
        
        return rules
    
    def execute_automation(
        self,
        rule_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute automation rules
        
        Args:
            rule_name: Specific rule to execute (None for all enabled rules)
            
        Returns:
            List of executed actions
        """
        rules = self.get_automation_rules(enabled_only=True)
        
        if rule_name:
            rules = [r for r in rules if r.get('name') == rule_name]
        
        executed = []
        
        for rule in rules:
            try:
                result = self._execute_rule(rule)
                if result:
                    executed.append({
                        'rule': rule.get('name'),
                        'result': result,
                        'success': True
                    })
            except Exception as e:
                executed.append({
                    'rule': rule.get('name'),
                    'result': f"Error: {str(e)}",
                    'success': False
                })
        
        return executed
    
    def auto_create_recurring_items(
        self,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Automatically create recurring events and tasks
        
        Args:
            days_ahead: Number of days ahead to create items
            
        Returns:
            List of created items
        """
        created = []
        
        # Detect recurring patterns
        recurring_events = self.pattern_detector.detect_recurring_events(days_back=60, min_frequency=3)
        recurring_tasks = self.pattern_detector.detect_recurring_tasks(days_back=60, min_frequency=3)
        
        today = jdatetime.date.today()
        target_date = today + jdatetime.timedelta(days=days_ahead)
        
        # Create missing recurring events
        for pattern in recurring_events:
            next_date = jdatetime.datetime.strptime(pattern['next_occurrence'], '%Y-%m-%d').date()
            
            if today <= next_date <= target_date:
                # Check if event already exists
                existing = self.db.get_events(
                    date=next_date.strftime('%Y-%m-%d'),
                    title=pattern['title']
                )
                
                if not existing:
                    sample = pattern['sample_item']
                    event_id = self.db.create_event(
                        date=next_date.strftime('%Y-%m-%d'),
                        title=pattern['title'],
                        attendee=sample.get('attendee'),
                        description=sample.get('description'),
                        location=sample.get('location')
                    )
                    
                    created.append({
                        'type': 'event',
                        'id': event_id,
                        'date': next_date.strftime('%Y-%m-%d'),
                        'title': pattern['title'],
                        'pattern': pattern['pattern_description']
                    })
        
        # Create missing recurring tasks
        for pattern in recurring_tasks:
            next_date = jdatetime.datetime.strptime(pattern['next_occurrence'], '%Y-%m-%d').date()
            
            if today <= next_date <= target_date:
                # Check if task already exists
                existing = self.db.get_tasks(
                    due_date=next_date.strftime('%Y-%m-%d'),
                    description=pattern['title']
                )
                
                if not existing:
                    sample = pattern['sample_item']
                    task_id = self.db.create_task(
                        due_date=next_date.strftime('%Y-%m-%d'),
                        description=pattern['title'],
                        project=sample.get('project'),
                        attendant=sample.get('attendant')
                    )
                    
                    created.append({
                        'type': 'task',
                        'id': task_id,
                        'due_date': next_date.strftime('%Y-%m-%d'),
                        'description': pattern['title'],
                        'pattern': pattern['pattern_description']
                    })
        
        return created
    
    def _execute_rule(
        self,
        rule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute a single automation rule"""
        rule_type = rule.get('type')
        action = rule.get('action', {})
        
        if rule_type == 'recurring_event':
            return self._create_recurring_event(action)
        elif rule_type == 'recurring_task':
            return self._create_recurring_task(action)
        elif rule_type == 'template':
            return self._apply_template(action)
        else:
            return None
    
    def _create_recurring_event(
        self,
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create event from recurring pattern"""
        date = action.get('date')
        if not date:
            # Calculate next occurrence
            pattern = action.get('pattern', {})
            last_date = jdatetime.datetime.strptime(pattern.get('last_occurrence'), '%Y-%m-%d').date()
            interval = pattern.get('interval_days', 7)
            date = (last_date + jdatetime.timedelta(days=interval)).strftime('%Y-%m-%d')
        
        event_id = self.db.create_event(
            date=date,
            title=action.get('title', ''),
            attendee=action.get('attendee'),
            description=action.get('description'),
            location=action.get('location')
        )
        
        return {
            'type': 'event_created',
            'event_id': event_id,
            'date': date
        }
    
    def _create_recurring_task(
        self,
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create task from recurring pattern"""
        due_date = action.get('due_date')
        if not due_date:
            # Calculate next occurrence
            pattern = action.get('pattern', {})
            last_date = jdatetime.datetime.strptime(pattern.get('last_occurrence'), '%Y-%m-%d').date()
            interval = pattern.get('interval_days', 7)
            due_date = (last_date + jdatetime.timedelta(days=interval)).strftime('%Y-%m-%d')
        
        task_id = self.db.create_task(
            due_date=due_date,
            description=action.get('description', ''),
            project=action.get('project'),
            attendant=action.get('attendant')
        )
        
        return {
            'type': 'task_created',
            'task_id': task_id,
            'due_date': due_date
        }
    
    def _apply_template(
        self,
        action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a template to create item"""
        template_type = action.get('template_type', 'event')
        fields = action.get('fields', {})
        
        if template_type == 'event':
            event_id = self.db.create_event(
                date=fields.get('date', jdatetime.date.today().strftime('%Y-%m-%d')),
                title=fields.get('title', ''),
                attendee=fields.get('attendee'),
                description=fields.get('description'),
                location=fields.get('location')
            )
            return {
                'type': 'event_created',
                'event_id': event_id
            }
        elif template_type == 'task':
            task_id = self.db.create_task(
                due_date=fields.get('due_date', jdatetime.date.today().strftime('%Y-%m-%d')),
                description=fields.get('description', ''),
                project=fields.get('project'),
                attendant=fields.get('attendant')
            )
            return {
                'type': 'task_created',
                'task_id': task_id
            }
        
        return None

