"""
LangChain関数呼び出しテスト結果のためのHTMLレポートジェネレーター

以下を含む包括的なHTMLレポートを生成:
- インタラクティブなチャートとグラフ
- 詳細なテスト結果テーブル
- パフォーマンスメトリクスの可視化
- 統計分析
- エクスポート機能

使用方法:
    python test_reporter.py --input test_results.json --output report.html
    python test_reporter.py --input performance_results.json --type performance
"""

import json
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64
import os

class HTMLReportGenerator:
    """テスト結果の包括的なHTMLレポートを生成"""
    
    def __init__(self):
        self.template = self._get_html_template()
        
    def generate_comprehensive_report(self, results: Dict[str, Any], output_file: str):
        """Generate a comprehensive test report"""
        
        # Extract data for report
        report_data = self._process_comprehensive_results(results)
        
        # Generate HTML content
        html_content = self._generate_comprehensive_html(report_data)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"📄 HTML report generated: {output_file}")
        
    def generate_performance_report(self, results: Dict[str, Any], output_file: str):
        """Generate a performance-focused report"""
        
        # Extract performance data
        perf_data = self._process_performance_results(results)
        
        # Generate HTML content
        html_content = self._generate_performance_html(perf_data)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"📄 Performance report generated: {output_file}")
        
    def _process_comprehensive_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process comprehensive test results for HTML generation"""
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_duration = 0
        perspective_stats = {}
        
        for perspective_name, perspective_results in results.items():
            if isinstance(perspective_results, dict):
                # Handle nested results (like complexity levels)
                perspective_total = 0
                perspective_passed = 0
                perspective_duration = 0
                
                for sub_name, session_data in perspective_results.items():
                    if isinstance(session_data, dict) and "total_tests" in session_data:
                        perspective_total += session_data["total_tests"]
                        perspective_passed += session_data["passed_tests"]
                        perspective_duration += session_data.get("duration_seconds", 0)
                        
                perspective_stats[perspective_name] = {
                    "total": perspective_total,
                    "passed": perspective_passed,
                    "failed": perspective_total - perspective_passed,
                    "success_rate": (perspective_passed / perspective_total * 100) if perspective_total > 0 else 0,
                    "duration": perspective_duration,
                    "subcategories": perspective_results
                }
                
                total_tests += perspective_total
                total_passed += perspective_passed
                total_duration += perspective_duration
                
        overall_stats = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration
        }
        
        return {
            "overall": overall_stats,
            "perspectives": perspective_stats,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def _process_performance_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance test results for HTML generation"""
        
        processed = {
            "benchmark_results": results.get("results", {}),
            "system_info": results.get("system_info", {}),
            "timestamp": results.get("timestamp", datetime.now().isoformat())
        }
        
        return processed
        
    def _generate_comprehensive_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for comprehensive test report"""
        
        # Prepare chart data
        perspective_labels = list(data["perspectives"].keys())
        perspective_success_rates = [data["perspectives"][p]["success_rate"] for p in perspective_labels]
        
        # Generate success rate chart data
        chart_data = {
            "labels": perspective_labels,
            "success_rates": perspective_success_rates
        }
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangChain Function Calling Test Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 LangChain Function Calling Test Report</h1>
            <p class="timestamp">Generated: {data["timestamp"]}</p>
        </header>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Tests</h3>
                <div class="metric">{data["overall"]["total_tests"]}</div>
            </div>
            <div class="card success">
                <h3>Passed</h3>
                <div class="metric">{data["overall"]["total_passed"]}</div>
            </div>
            <div class="card failure">
                <h3>Failed</h3>
                <div class="metric">{data["overall"]["total_failed"]}</div>
            </div>
            <div class="card">
                <h3>Success Rate</h3>
                <div class="metric">{data["overall"]["success_rate"]:.1f}%</div>
            </div>
        </div>
        
        <div class="chart-section">
            <h2>📊 Success Rate by Perspective</h2>
            <canvas id="successRateChart" width="400" height="200"></canvas>
        </div>
        
        <div class="detailed-results">
            <h2>📋 Detailed Results</h2>
            {self._generate_perspective_tables(data["perspectives"])}
        </div>
        
        <div class="insights">
            <h2>💡 Key Insights</h2>
            {self._generate_insights(data)}
        </div>
    </div>
    
    <script>
        {self._generate_chart_script(chart_data)}
    </script>
</body>
</html>
"""
        return html
        
    def _generate_performance_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML for performance report"""
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangChain Performance Benchmark Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ LangChain Performance Benchmark Report</h1>
            <p class="timestamp">Generated: {data["timestamp"]}</p>
        </header>
        
        {self._generate_performance_summary(data["benchmark_results"])}
        
        <div class="performance-charts">
            <h2>📈 Performance Metrics</h2>
            {self._generate_performance_charts(data["benchmark_results"])}
        </div>
        
        <div class="system-info">
            <h2>🖥️ System Information</h2>
            {self._generate_system_info_table(data["system_info"])}
        </div>
    </div>
    
    <script>
        {self._generate_performance_chart_script(data["benchmark_results"])}
    </script>
</body>
</html>
"""
        return html
        
    def _generate_perspective_tables(self, perspectives: Dict[str, Any]) -> str:
        """Generate HTML tables for each test perspective"""
        tables_html = ""
        
        for perspective_name, perspective_data in perspectives.items():
            status_icon = "✅" if perspective_data["success_rate"] >= 80 else "⚠️" if perspective_data["success_rate"] >= 60 else "❌"
            
            tables_html += f"""
            <div class="perspective-section">
                <h3>{status_icon} {perspective_name.title().replace('_', ' ')}</h3>
                <div class="perspective-stats">
                    <span class="stat">Tests: {perspective_data["total"]}</span>
                    <span class="stat success">Passed: {perspective_data["passed"]}</span>
                    <span class="stat failure">Failed: {perspective_data["failed"]}</span>
                    <span class="stat">Success Rate: {perspective_data["success_rate"]:.1f}%</span>
                    <span class="stat">Duration: {perspective_data["duration"]:.2f}s</span>
                </div>
                
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Subcategory</th>
                            <th>Tests</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Success Rate</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for sub_name, sub_data in perspective_data["subcategories"].items():
                if isinstance(sub_data, dict) and "total_tests" in sub_data:
                    success_rate = sub_data.get("success_rate", 0)
                    status_class = "success" if success_rate >= 80 else "warning" if success_rate >= 60 else "failure"
                    
                    tables_html += f"""
                        <tr class="{status_class}">
                            <td>{sub_name.title().replace('_', ' ')}</td>
                            <td>{sub_data["total_tests"]}</td>
                            <td>{sub_data["passed_tests"]}</td>
                            <td>{sub_data["total_tests"] - sub_data["passed_tests"]}</td>
                            <td>{success_rate:.1f}%</td>
                        </tr>
                    """
                    
            tables_html += """
                    </tbody>
                </table>
            </div>
            """
            
        return tables_html
        
    def _generate_performance_summary(self, results: Dict[str, Any]) -> str:
        """Generate performance summary cards"""
        summary_html = '<div class="summary-cards">'
        
        for test_name, stats in results.items():
            if "error" in stats:
                continue
                
            summary_html += f"""
            <div class="card">
                <h3>{test_name.title().replace('_', ' ')}</h3>
                <div class="metric">{stats.get('throughput_rps', 0):.1f} RPS</div>
                <div class="sub-metric">Avg: {stats.get('response_time', {}).get('mean', 0):.3f}s</div>
            </div>
            """
            
        summary_html += '</div>'
        return summary_html
        
    def _generate_performance_charts(self, results: Dict[str, Any]) -> str:
        """Generate performance chart containers"""
        return """
        <div class="chart-grid">
            <div class="chart-container">
                <h3>Response Times</h3>
                <canvas id="responseTimeChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Throughput</h3>
                <canvas id="throughputChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Memory Usage</h3>
                <canvas id="memoryChart"></canvas>
            </div>
        </div>
        """
        
    def _generate_system_info_table(self, system_info: Dict[str, Any]) -> str:
        """Generate system information table"""
        if not system_info:
            return "<p>No system information available</p>"
            
        table_html = """
        <table class="system-table">
            <tbody>
        """
        
        for key, value in system_info.items():
            display_key = key.replace('_', ' ').title()
            table_html += f"""
                <tr>
                    <td>{display_key}</td>
                    <td>{value}</td>
                </tr>
            """
            
        table_html += """
            </tbody>
        </table>
        """
        
        return table_html
        
    def _generate_insights(self, data: Dict[str, Any]) -> str:
        """Generate insights based on test results"""
        insights = []
        overall = data["overall"]
        
        if overall["success_rate"] >= 90:
            insights.append("🎉 Excellent overall performance! The system is working very well.")
        elif overall["success_rate"] >= 80:
            insights.append("👍 Good overall performance with room for improvement.")
        elif overall["success_rate"] >= 60:
            insights.append("⚠️ Moderate performance. Some areas need attention.")
        else:
            insights.append("🚨 Poor performance. Significant issues need to be addressed.")
            
        # Analyze perspectives
        best_perspective = max(data["perspectives"].items(), key=lambda x: x[1]["success_rate"])
        worst_perspective = min(data["perspectives"].items(), key=lambda x: x[1]["success_rate"])
        
        insights.append(f"🏆 Best performing perspective: {best_perspective[0]} ({best_perspective[1]['success_rate']:.1f}%)")
        insights.append(f"📉 Lowest performing perspective: {worst_perspective[0]} ({worst_perspective[1]['success_rate']:.1f}%)")
        
        insights_html = "<ul>"
        for insight in insights:
            insights_html += f"<li>{insight}</li>"
        insights_html += "</ul>"
        
        return insights_html
        
    def _generate_chart_script(self, chart_data: Dict[str, Any]) -> str:
        """Generate JavaScript for charts"""
        return f"""
        const ctx = document.getElementById('successRateChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data["labels"])},
                datasets: [{{
                    label: 'Success Rate (%)',
                    data: {json.dumps(chart_data["success_rates"])},
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
        """
        
    def _generate_performance_chart_script(self, results: Dict[str, Any]) -> str:
        """Generate JavaScript for performance charts"""
        # Extract data for charts
        test_names = []
        response_times = []
        throughputs = []
        memory_usage = []
        
        for test_name, stats in results.items():
            if "error" not in stats:
                test_names.append(test_name.replace('_', ' ').title())
                response_times.append(stats.get('response_time', {}).get('mean', 0))
                throughputs.append(stats.get('throughput_rps', 0))
                memory_usage.append(stats.get('memory', {}).get('peak_mb', 0))
                
        return f"""
        // Response Time Chart
        const responseCtx = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(responseCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Avg Response Time (s)',
                    data: {json.dumps(response_times)},
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true
                }}]
            }},
            options: {{ responsive: true }}
        }});
        
        // Throughput Chart
        const throughputCtx = document.getElementById('throughputChart').getContext('2d');
        new Chart(throughputCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Throughput (RPS)',
                    data: {json.dumps(throughputs)},
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{ responsive: true }}
        }});
        
        // Memory Chart
        const memoryCtx = document.getElementById('memoryChart').getContext('2d');
        new Chart(memoryCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(test_names)},
                datasets: [{{
                    label: 'Peak Memory (MB)',
                    data: {json.dumps(memory_usage)},
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(75, 192, 192, 0.6)'
                    ]
                }}]
            }},
            options: {{ responsive: true }}
        }});
        """
        
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .timestamp {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #ddd;
        }
        
        .card.success {
            border-left-color: #10b981;
        }
        
        .card.failure {
            border-left-color: #ef4444;
        }
        
        .card h3 {
            color: #666;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }
        
        .sub-metric {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.25rem;
        }
        
        .chart-section, .detailed-results, .insights, .performance-charts, .system-info {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .chart-section h2, .detailed-results h2, .insights h2, .performance-charts h2, .system-info h2 {
            margin-bottom: 1.5rem;
            color: #333;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 0.5rem;
        }
        
        .perspective-section {
            margin-bottom: 2rem;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .perspective-section h3 {
            background: #f8f9fa;
            padding: 1rem;
            margin: 0;
            font-size: 1.2rem;
        }
        
        .perspective-stats {
            padding: 1rem;
            background: #fafafa;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .stat {
            display: inline-block;
            margin-right: 1.5rem;
            padding: 0.25rem 0.5rem;
            background: white;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .stat.success {
            background: #dcfce7;
            color: #166534;
        }
        
        .stat.failure {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .results-table, .system-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        .results-table th, .results-table td, .system-table th, .system-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e5e5e5;
        }
        
        .results-table th, .system-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #374151;
        }
        
        .results-table tr.success {
            background: #f0fdf4;
        }
        
        .results-table tr.warning {
            background: #fffbeb;
        }
        
        .results-table tr.failure {
            background: #fef2f2;
        }
        
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .chart-container {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .chart-container h3 {
            margin-bottom: 1rem;
            text-align: center;
            color: #374151;
        }
        
        .insights ul {
            list-style: none;
            padding: 0;
        }
        
        .insights li {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #3b82f6;
        }
        
        @media (max-width: 768px) {
            .summary-cards {
                grid-template-columns: 1fr;
            }
            
            .chart-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 10px;
            }
            
            header h1 {
                font-size: 2rem;
            }
        }
        """
        
    def _get_html_template(self) -> str:
        """Get the base HTML template"""
        return ""  # Template is generated dynamically

def generate_html_report(results: Dict[str, Any], output_file: str, report_type: str = "comprehensive"):
    """Main function to generate HTML reports"""
    generator = HTMLReportGenerator()
    
    if report_type == "performance":
        generator.generate_performance_report(results, output_file)
    else:
        generator.generate_comprehensive_report(results, output_file)

def main():
    parser = argparse.ArgumentParser(description="Generate HTML reports from test results")
    
    parser.add_argument("--input", type=str, required=True, help="Input JSON results file")
    parser.add_argument("--output", type=str, default="report.html", help="Output HTML file")
    parser.add_argument("--type", type=str, choices=["comprehensive", "performance"], 
                       default="comprehensive", help="Report type")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
        generate_html_report(results, args.output, args.type)
        
        return 0
        
    except FileNotFoundError:
        print(f"❌ Input file not found: {args.input}")
        return 1
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in input file: {args.input}")
        return 1
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())