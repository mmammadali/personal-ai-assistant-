"""
Dashboard Builder
Builds comprehensive dashboards from multiple data sources
"""
from typing import List, Dict, Any, Optional
from intelligence.visualization.chart_generator import ChartGenerator
import logging

logger = logging.getLogger(__name__)


class DashboardBuilder:
    """Builds dashboards with multiple visualizations"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
    
    def build_dashboard(
        self,
        data_sources: List[Dict[str, Any]],
        layout: str = "grid",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build dashboard from multiple data sources
        
        Args:
            data_sources: List of data source configurations
            layout: Layout type ('grid', 'vertical', 'horizontal')
            output_path: Path to save dashboard
            
        Returns:
            Dashboard generation result
        """
        try:
            charts = []
            
            for i, source in enumerate(data_sources):
                data = source.get('data', [])
                chart_type = source.get('chart_type', 'bar')
                title = source.get('title', f'Chart {i+1}')
                description = source.get('description')
                
                # Generate chart
                chart_result = self.chart_generator.generate_chart(
                    data=data,
                    chart_type=chart_type,
                    title=title,
                    description=description,
                    output_path=f'temp_chart_{i}.png'
                )
                
                if chart_result.get('success'):
                    charts.append({
                        'title': title,
                        'chart_path': chart_result.get('chart_path'),
                        'chart_type': chart_type
                    })
            
            # Combine charts into dashboard
            dashboard_path = self._combine_charts(charts, layout, output_path)
            
            return {
                'success': True,
                'dashboard_path': dashboard_path,
                'charts': charts,
                'layout': layout
            }
        
        except Exception as e:
            logger.error(f"Error building dashboard: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _combine_charts(
        self,
        charts: List[Dict[str, Any]],
        layout: str,
        output_path: Optional[str]
    ) -> str:
        """Combine multiple charts into a dashboard"""
        try:
            from PIL import Image
            import os
        except ImportError:
            logger.warning("PIL not available, cannot combine charts")
            return charts[0].get('chart_path', '') if charts else ''
        
        if not charts:
            return ''
        
        # Load chart images
        images = []
        for chart in charts:
            chart_path = chart.get('chart_path')
            if chart_path and os.path.exists(chart_path):
                try:
                    img = Image.open(chart_path)
                    images.append(img)
                except Exception as e:
                    logger.error(f"Error loading chart {chart_path}: {e}")
        
        if not images:
            return ''
        
        # Combine based on layout
        if layout == 'vertical':
            # Stack vertically
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            
            combined = Image.new('RGB', (max_width, total_height))
            y_offset = 0
            for img in images:
                combined.paste(img, (0, y_offset))
                y_offset += img.height
        
        elif layout == 'horizontal':
            # Stack horizontally
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            
            combined = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for img in images:
                combined.paste(img, (x_offset, 0))
                x_offset += img.width
        
        else:  # grid
            # 2x2 grid (or as close as possible)
            cols = 2
            rows = (len(images) + cols - 1) // cols
            
            max_width = max(img.width for img in images)
            max_height = max(img.height for img in images)
            
            combined = Image.new('RGB', (max_width * cols, max_height * rows))
            
            for i, img in enumerate(images):
                row = i // cols
                col = i % cols
                x = col * max_width
                y = row * max_height
                combined.paste(img, (x, y))
        
        # Save combined image
        if not output_path:
            output_path = 'dashboard.png'
        
        combined.save(output_path, 'PNG')
        
        # Clean up temp files
        for chart in charts:
            chart_path = chart.get('chart_path')
            if chart_path and chart_path.startswith('temp_chart_'):
                try:
                    os.remove(chart_path)
                except:
                    pass
        
        return output_path

