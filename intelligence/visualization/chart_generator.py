"""
Chart Generator
Generates charts and visualizations from data using natural language
"""
from typing import List, Dict, Any, Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging
import json

logger = logging.getLogger(__name__)

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("Pandas not available")


class ChartGenerator:
    """Generates charts from data and natural language descriptions"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
    
    def generate_chart(
        self,
        data: List[Dict[str, Any]],
        chart_type: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chart from data
        
        Args:
            data: Data to visualize (list of dictionaries)
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', 'area')
            title: Chart title
            description: Natural language description of what to visualize
            output_path: Path to save chart image
            
        Returns:
            Chart generation result
        """
        if not MATPLOTLIB_AVAILABLE:
            return {
                'success': False,
                'error': 'Matplotlib not available. Please install: pip install matplotlib'
            }
        
        try:
            # Parse data
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(data)
            else:
                df = None
            
            # Generate chart based on type
            if chart_type == 'bar':
                chart_path = self._generate_bar_chart(data, title, output_path)
            elif chart_type == 'line':
                chart_path = self._generate_line_chart(data, title, output_path)
            elif chart_type == 'pie':
                chart_path = self._generate_pie_chart(data, title, output_path)
            elif chart_type == 'scatter':
                chart_path = self._generate_scatter_chart(data, title, output_path)
            elif chart_type == 'area':
                chart_path = self._generate_area_chart(data, title, output_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported chart type: {chart_type}'
                }
            
            return {
                'success': True,
                'chart_type': chart_type,
                'chart_path': chart_path,
                'title': title
            }
        
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_chart_from_description(
        self,
        data: List[Dict[str, Any]],
        description: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chart from natural language description
        
        Args:
            data: Data to visualize
            description: Natural language description (e.g., "Show sales by month")
            output_path: Path to save chart
            
        Returns:
            Chart generation result
        """
        # Use LLM to determine chart type and configuration
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Determine the best chart type and configuration from a natural language description.

Chart types: bar, line, pie, scatter, area

Return JSON with:
- chart_type: type of chart
- title: suggested title
- x_axis: x-axis label/field
- y_axis: y-axis label/field"""),
            ("human", """Description: {description}

Data sample: {data_sample}

Determine chart configuration.""")
        ])
        
        try:
            # Sample data for context
            data_sample = json.dumps(data[:5] if len(data) > 5 else data, ensure_ascii=False)
            
            response = self.llm.invoke(
                prompt.format_messages(
                    description=description,
                    data_sample=data_sample
                )
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            try:
                config = json.loads(text)
            except:
                # Fallback parsing
                config = self._parse_chart_config(text)
            
            # Generate chart
            return self.generate_chart(
                data=data,
                chart_type=config.get('chart_type', 'bar'),
                title=config.get('title', description),
                output_path=output_path
            )
        
        except Exception as e:
            logger.error(f"Error generating chart from description: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_bar_chart(
        self,
        data: List[Dict[str, Any]],
        title: Optional[str],
        output_path: Optional[str]
    ) -> str:
        """Generate bar chart"""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib not available")
        
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(data)
            # Auto-detect columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            categorical_cols = df.select_dtypes(exclude=['number']).columns
            
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                x_col = categorical_cols[0]
                y_col = numeric_cols[0]
                
                plt.figure(figsize=(10, 6))
                plt.bar(df[x_col], df[y_col])
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                if title:
                    plt.title(title)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
            else:
                # Fallback
                plt.figure(figsize=(10, 6))
                plt.bar(range(len(data)), [d.get('value', 0) for d in data])
                if title:
                    plt.title(title)
                plt.tight_layout()
        else:
            # Simple bar chart
            plt.figure(figsize=(10, 6))
            values = [d.get('value', 0) for d in data]
            labels = [d.get('label', str(i)) for i, d in enumerate(data)]
            plt.bar(labels, values)
            if title:
                plt.title(title)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        
        if not output_path:
            output_path = 'chart.png'
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _generate_line_chart(
        self,
        data: List[Dict[str, Any]],
        title: Optional[str],
        output_path: Optional[str]
    ) -> str:
        """Generate line chart"""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib not available")
        
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(data)
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            plt.figure(figsize=(10, 6))
            for col in numeric_cols[:3]:  # Max 3 series
                plt.plot(df.index, df[col], label=col, marker='o')
            plt.xlabel('Index')
            plt.ylabel('Value')
            if title:
                plt.title(title)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
        else:
            plt.figure(figsize=(10, 6))
            values = [d.get('value', 0) for d in data]
            plt.plot(values, marker='o')
            if title:
                plt.title(title)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
        
        if not output_path:
            output_path = 'chart.png'
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _generate_pie_chart(
        self,
        data: List[Dict[str, Any]],
        title: Optional[str],
        output_path: Optional[str]
    ) -> str:
        """Generate pie chart"""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib not available")
        
        labels = [d.get('label', str(i)) for i, d in enumerate(data)]
        values = [d.get('value', 0) for d in data]
        
        plt.figure(figsize=(8, 8))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        if title:
            plt.title(title)
        plt.tight_layout()
        
        if not output_path:
            output_path = 'chart.png'
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _generate_scatter_chart(
        self,
        data: List[Dict[str, Any]],
        title: Optional[str],
        output_path: Optional[str]
    ) -> str:
        """Generate scatter chart"""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib not available")
        
        x_values = [d.get('x', d.get('x_value', 0)) for d in data]
        y_values = [d.get('y', d.get('y_value', 0)) for d in data]
        
        plt.figure(figsize=(10, 6))
        plt.scatter(x_values, y_values, alpha=0.6)
        plt.xlabel('X')
        plt.ylabel('Y')
        if title:
            plt.title(title)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if not output_path:
            output_path = 'chart.png'
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _generate_area_chart(
        self,
        data: List[Dict[str, Any]],
        title: Optional[str],
        output_path: Optional[str]
    ) -> str:
        """Generate area chart"""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib not available")
        
        values = [d.get('value', 0) for d in data]
        labels = [d.get('label', str(i)) for i, d in enumerate(data)]
        
        plt.figure(figsize=(10, 6))
        plt.fill_between(range(len(values)), values, alpha=0.5)
        plt.plot(range(len(values)), values, marker='o')
        plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
        if title:
            plt.title(title)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if not output_path:
            output_path = 'chart.png'
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _parse_chart_config(self, text: str) -> Dict[str, Any]:
        """Parse chart configuration from text"""
        config = {
            'chart_type': 'bar',
            'title': 'Chart',
            'x_axis': 'x',
            'y_axis': 'y'
        }
        
        text_lower = text.lower()
        
        # Determine chart type
        if 'pie' in text_lower:
            config['chart_type'] = 'pie'
        elif 'line' in text_lower:
            config['chart_type'] = 'line'
        elif 'scatter' in text_lower:
            config['chart_type'] = 'scatter'
        elif 'area' in text_lower:
            config['chart_type'] = 'area'
        else:
            config['chart_type'] = 'bar'
        
        return config

