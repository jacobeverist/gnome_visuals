import json
import yaml
import datetime
import plotly.io as pio
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
from typing import Dict, Any, List

def export_encoder_config(encoder_params: Dict[str, Any], filename: str = None) -> str:
    """Export encoder configuration to JSON file."""

    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"encoder_config_{timestamp}.json"

    # Add metadata
    export_data = {
        "metadata": {
            "export_timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "description": "GNOME Encoder Configuration"
        },
        "encoder_config": encoder_params
    }

    # Ensure exports directory exists
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    filepath = exports_dir / filename

    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)

    return str(filepath)

def import_encoder_config(filepath: str) -> Dict[str, Any]:
    """Import encoder configuration from JSON file."""

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data.get('encoder_config', {})

def export_comparison_config(encoder_configs: List[Dict[str, Any]],
                           comparison_mode: str,
                           filename: str = None) -> str:
    """Export comparison configuration with multiple encoders."""

    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_config_{timestamp}.json"

    export_data = {
        "metadata": {
            "export_timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "description": "GNOME Encoder Comparison Configuration",
            "comparison_mode": comparison_mode,
            "num_encoders": len(encoder_configs)
        },
        "encoder_configs": encoder_configs
    }

    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    filepath = exports_dir / filename

    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)

    return str(filepath)

def export_plot_html(figure: go.Figure, filename: str = None) -> str:
    """Export Plotly figure as standalone HTML file."""

    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plot_{timestamp}.html"

    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    filepath = exports_dir / filename

    # Configure the HTML export
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': filename.replace('.html', ''),
            'height': 800,
            'width': 1200,
            'scale': 1
        }
    }

    pio.write_html(figure, filepath, config=config, include_plotlyjs=True)

    return str(filepath)

def export_plot_image(figure: go.Figure, format: str = 'png',
                     width: int = 1200, height: int = 800,
                     filename: str = None) -> str:
    """Export Plotly figure as static image."""

    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plot_{timestamp}.{format}"

    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    filepath = exports_dir / filename

    try:
        pio.write_image(figure, filepath, format=format, width=width, height=height)
        return str(filepath)
    except Exception as e:
        # Fallback: save as HTML if image export fails
        print(f"Image export failed: {e}. Saving as HTML instead.")
        return export_plot_html(figure, filename.replace(f'.{format}', '.html'))

def generate_analysis_report(encoder_configs: List[Dict[str, Any]],
                           analysis_results: Dict[str, Any],
                           filename: str = None) -> str:
    """Generate comprehensive analysis report."""

    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{timestamp}.md"

    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    filepath = exports_dir / filename

    # Generate markdown report
    report_content = f"""# GNOME Encoder Analysis Report

Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

This report analyzes {len(encoder_configs)} encoder configuration(s) and their performance characteristics.

## Encoder Configurations

"""

    for i, config in enumerate(encoder_configs):
        report_content += f"""### Encoder {chr(65 + i)}

- **Type**: {config.get('encoder_type', 'Unknown')}
- **Number of Bins (n)**: {config.get('n', 'Unknown')}
- **Bin Width (w)**: {config.get('w', 'Unknown')}
- **Period**: {config.get('period', 'Unknown')}
- **Offset**: {config.get('offset', 'Unknown')}
- **Input Range**: [{config.get('xmin', 'Unknown')}, {config.get('xmax', 'Unknown')}]

"""

    # Add analysis results
    if analysis_results:
        report_content += """## Analysis Results

"""

        if 'similarity_stats' in analysis_results:
            stats = analysis_results['similarity_stats']
            report_content += f"""### Similarity Statistics

- **Mean Similarity**: {stats.get('mean', 'N/A'):.4f}
- **Standard Deviation**: {stats.get('std', 'N/A'):.4f}
- **Min Similarity**: {stats.get('min', 'N/A'):.4f}
- **Max Similarity**: {stats.get('max', 'N/A'):.4f}

"""

        if 'overlap_analysis' in analysis_results:
            overlap = analysis_results['overlap_analysis']
            report_content += f"""### Overlap Analysis

- **Average Overlap**: {overlap.get('mean_overlap', 'N/A'):.4f}
- **Overlap Range**: [{overlap.get('min_overlap', 'N/A'):.4f}, {overlap.get('max_overlap', 'N/A'):.4f}]

"""

        if 'performance_metrics' in analysis_results:
            perf = analysis_results['performance_metrics']
            report_content += f"""### Performance Metrics

- **Encoding Speed**: {perf.get('encoding_speed', 'N/A')} encodings/second
- **Memory Usage**: {perf.get('memory_usage', 'N/A')} MB
- **Sparsity**: {perf.get('sparsity', 'N/A'):.2%}

"""

    report_content += f"""## Recommendations

Based on the analysis:

1. **Parameter Optimization**: Consider adjusting parameters for better performance
2. **Use Case Suitability**: Evaluate encoder configurations for specific applications
3. **Comparison Analysis**: Review similarity and overlap metrics for optimal selection

## Configuration Files

The encoder configurations used in this analysis are saved as:
- Individual configs: `encoder_config_*.json`
- Comparison config: `comparison_config_*.json`

## Visualizations

Interactive plots and static images are available in the exports directory.

---
*Report generated by GNOME Encoder Interactive Dashboard*
"""

    with open(filepath, 'w') as f:
        f.write(report_content)

    return str(filepath)

def save_session_state(app_state: Dict[str, Any], filename: str = None) -> str:
    """Save complete application session state."""

    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_state_{timestamp}.json"

    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)

    filepath = exports_dir / filename

    session_data = {
        "metadata": {
            "save_timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "description": "Complete GNOME Encoder Dashboard Session"
        },
        "app_state": app_state
    }

    with open(filepath, 'w') as f:
        json.dump(session_data, f, indent=2, default=str)

    return str(filepath)

def load_session_state(filepath: str) -> Dict[str, Any]:
    """Load application session state."""

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data.get('app_state', {})

def get_export_summary() -> Dict[str, List[str]]:
    """Get summary of all exported files."""

    exports_dir = Path("exports")
    if not exports_dir.exists():
        return {"message": "No exports directory found"}

    files = {
        "configs": [],
        "plots": [],
        "reports": [],
        "sessions": []
    }

    for file_path in exports_dir.iterdir():
        if file_path.is_file():
            filename = file_path.name
            if filename.startswith("encoder_config") or filename.startswith("comparison_config"):
                files["configs"].append(filename)
            elif filename.startswith("plot_"):
                files["plots"].append(filename)
            elif filename.startswith("analysis_report"):
                files["reports"].append(filename)
            elif filename.startswith("session_state"):
                files["sessions"].append(filename)

    return files

def calculate_encoder_metrics(encoder, params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate various metrics for an encoder."""

    metrics = {}

    try:
        xmin, xmax = params.get('xmin', -1.0), params.get('xmax', 2.0)
        test_points = np.linspace(xmin, xmax, 100)

        # Encoding speed test
        start_time = datetime.datetime.now()
        encodings = []
        for x in test_points[:10]:  # Test with smaller subset
            encodings.append(encoder.encode(x))
        end_time = datetime.datetime.now()

        duration = (end_time - start_time).total_seconds()
        metrics['encoding_speed'] = len(test_points[:10]) / duration if duration > 0 else float('inf')

        # Sparsity calculation
        all_encodings = np.array(encodings)
        total_bits = all_encodings.size
        active_bits = np.sum(all_encodings)
        metrics['sparsity'] = 1 - (active_bits / total_bits) if total_bits > 0 else 0

        # Memory estimation (rough)
        metrics['memory_usage'] = all_encodings.nbytes / 1024 / 1024  # MB

        # Overlap consistency
        overlaps = []
        for i in range(len(encodings)-1):
            overlap = np.dot(encodings[i], encodings[i+1])
            overlaps.append(overlap)

        metrics['mean_overlap'] = np.mean(overlaps) if overlaps else 0
        metrics['overlap_std'] = np.std(overlaps) if overlaps else 0

    except Exception as e:
        metrics['error'] = str(e)

    return metrics