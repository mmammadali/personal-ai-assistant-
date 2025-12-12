"""
Change Analyzer
Analyzes impact of document changes and provides recommendations
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging

logger = logging.getLogger(__name__)


class ChangeAnalyzer:
    """Analyzes impact of document changes"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
    
    def analyze_change_impact(
        self,
        changes: List[Dict[str, Any]],
        document_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze impact of changes
        
        Args:
            changes: List of changes from document comparison
            document_context: Optional context about the document
            
        Returns:
            Impact analysis with recommendations
        """
        # Categorize changes
        critical_changes = [c for c in changes if c.get('severity') == 'critical']
        notable_changes = [c for c in changes if c.get('severity') == 'notable']
        minor_changes = [c for c in changes if c.get('severity') == 'minor']
        
        # Analyze financial impact
        financial_impact = self._analyze_financial_impact(changes)
        
        # Analyze risk
        risk_assessment = self._assess_risk(changes, document_context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(changes, financial_impact, risk_assessment)
        
        # Generate negotiation points
        negotiation_points = self._generate_negotiation_points(changes)
        
        return {
            'change_summary': {
                'total': len(changes),
                'critical': len(critical_changes),
                'notable': len(notable_changes),
                'minor': len(minor_changes)
            },
            'financial_impact': financial_impact,
            'risk_assessment': risk_assessment,
            'recommendations': recommendations,
            'negotiation_points': negotiation_points
        }
    
    def _analyze_financial_impact(
        self,
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze financial impact of changes"""
        financial_keywords = [
            'قیمت', 'مبلغ', 'هزینه', 'پرداخت', 'قرارداد',
            'price', 'amount', 'cost', 'payment', 'contract', 'fee'
        ]
        
        financial_changes = []
        for change in changes:
            text = (change.get('old_text', '') + change.get('new_text', '')).lower()
            if any(keyword in text for keyword in financial_keywords):
                financial_changes.append(change)
        
        return {
            'has_financial_impact': len(financial_changes) > 0,
            'financial_changes_count': len(financial_changes),
            'changes': financial_changes,
            'severity': 'high' if len(financial_changes) > 0 else 'none'
        }
    
    def _assess_risk(
        self,
        changes: List[Dict[str, Any]],
        document_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risk level of changes"""
        risk_keywords = [
            'مسئولیت', 'ضمانت', 'جریمه', 'خسارت',
            'liability', 'warranty', 'penalty', 'damage', 'risk'
        ]
        
        risk_changes = []
        for change in changes:
            text = (change.get('old_text', '') + change.get('new_text', '')).lower()
            if any(keyword in text for keyword in risk_keywords):
                risk_changes.append(change)
        
        # Determine risk level
        if len(risk_changes) > 0 or len([c for c in changes if c.get('severity') == 'critical']) > 0:
            risk_level = 'high'
        elif len([c for c in changes if c.get('severity') == 'notable']) > 3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_changes_count': len(risk_changes),
            'risk_changes': risk_changes,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _generate_recommendations(
        self,
        changes: List[Dict[str, Any]],
        financial_impact: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on changes"""
        recommendations = []
        
        # Financial recommendations
        if financial_impact.get('has_financial_impact'):
            recommendations.append('💰 تغییرات مالی شناسایی شد. بررسی دقیق مبالغ و شرایط پرداخت ضروری است.')
        
        # Risk recommendations
        if risk_assessment.get('risk_level') == 'high':
            recommendations.append('⚠️ سطح ریسک بالا است. بررسی حقوقی و مشاوره با وکیل توصیه می‌شود.')
        elif risk_assessment.get('risk_level') == 'medium':
            recommendations.append('⚠️ سطح ریسک متوسط است. بررسی دقیق تغییرات ضروری است.')
        
        # Critical changes
        critical_count = len([c for c in changes if c.get('severity') == 'critical'])
        if critical_count > 0:
            recommendations.append(f'🔴 {critical_count} تغییر بحرانی شناسایی شد. بررسی فوری لازم است.')
        
        # General recommendation
        if not recommendations:
            recommendations.append('✅ تغییرات عمدتاً جزئی هستند. بررسی کلی کافی است.')
        
        return recommendations
    
    def _generate_negotiation_points(
        self,
        changes: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate negotiation points from changes"""
        points = []
        
        # Extract key changes as negotiation points
        critical_changes = [c for c in changes if c.get('severity') == 'critical']
        
        for change in critical_changes[:5]:  # Top 5
            old_text = change.get('old_text', '')[:100]
            new_text = change.get('new_text', '')[:100]
            
            if old_text and new_text:
                points.append(f"تغییر از '{old_text}' به '{new_text}' - نیاز به توضیح")
        
        if not points:
            points.append('هیچ نکته مذاکره‌ای شناسایی نشد')
        
        return points
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get risk recommendation based on level"""
        recommendations = {
            'high': 'بررسی حقوقی فوری و مشاوره با وکیل ضروری است',
            'medium': 'بررسی دقیق تغییرات و در صورت نیاز مشاوره حقوقی',
            'low': 'بررسی کلی کافی است'
        }
        return recommendations.get(risk_level, 'بررسی کلی کافی است')

