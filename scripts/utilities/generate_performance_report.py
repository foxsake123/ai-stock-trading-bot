"""
Performance Report Generator

Analyzes benchmark results and generates comprehensive reports with:
- Performance metrics (timing, memory, throughput)
- Bottleneck identification
- Optimization recommendations
- Visual comparisons
- Historical trend analysis

Usage:
    python scripts/utilities/generate_performance_report.py
    python scripts/utilities/generate_performance_report.py --benchmark-file benchmarks/reports/performance_report_20251023.json
    python scripts/utilities/generate_performance_report.py --compare file1.json file2.json
"""

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class MetricSummary:
    """Summary of a performance metric"""
    name: str
    min_value: float
    max_value: float
    avg_value: float
    std_dev: float
    median: float
    unit: str


@dataclass
class Bottleneck:
    """Performance bottleneck"""
    component: str
    metric: str
    value: float
    threshold: float
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    recommendation: str


@dataclass
class PerformanceInsight:
    """Performance insight or recommendation"""
    category: str  # "OPTIMIZATION", "WARNING", "SUCCESS", "INFO"
    title: str
    description: str
    priority: int  # 1-5 (5 = highest)
    action_items: List[str]


# ============================================================================
# Performance Analyzer
# ============================================================================

class PerformanceAnalyzer:
    """Analyzes performance benchmark results"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.bottlenecks: List[Bottleneck] = []
        self.insights: List[PerformanceInsight] = []

    def load_benchmark_file(self, filepath: str) -> Dict[str, Any]:
        """Load benchmark results from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def analyze_benchmarks(self, data: Dict[str, Any]):
        """Analyze benchmark data and extract insights"""

        # Analyze benchmark results
        if "benchmarks" in data:
            self._analyze_benchmark_results(data["benchmarks"])

        # Analyze comparisons
        if "comparisons" in data:
            self._analyze_comparisons(data["comparisons"])

        # Identify bottlenecks
        self._identify_bottlenecks(data)

        # Generate insights
        self._generate_insights(data)

    def _analyze_benchmark_results(self, benchmarks: List[Dict]):
        """Analyze individual benchmark results"""

        durations = []
        memories = []

        for benchmark in benchmarks:
            if benchmark.get("success"):
                durations.append(benchmark["duration_seconds"])
                memories.append(benchmark["memory_mb"])

        if durations:
            self.metrics["duration"] = durations
        if memories:
            self.metrics["memory"] = memories

    def _analyze_comparisons(self, comparisons: List[Dict]):
        """Analyze comparison results"""

        speedups = []
        quality_improvements = []

        for comp in comparisons:
            speedups.append(comp["speedup"])
            quality_improvements.append(comp["quality_improvement"])

        if speedups:
            self.metrics["speedup"] = speedups
        if quality_improvements:
            self.metrics["quality_improvement"] = quality_improvements

    def _identify_bottlenecks(self, data: Dict[str, Any]):
        """Identify performance bottlenecks"""

        # Check for slow benchmarks (>30s)
        if "benchmarks" in data:
            for benchmark in data["benchmarks"]:
                if not benchmark.get("success"):
                    continue

                duration = benchmark["duration_seconds"]
                memory = benchmark["memory_mb"]

                # Timing bottleneck
                if duration > 30.0:
                    severity = "CRITICAL" if duration > 60 else "HIGH"
                    self.bottlenecks.append(Bottleneck(
                        component=benchmark["name"],
                        metric="Duration",
                        value=duration,
                        threshold=30.0,
                        severity=severity,
                        recommendation=f"Optimize {benchmark['name']} - currently {duration:.2f}s (target: <30s)"
                    ))

                # Memory bottleneck
                if memory > 500.0:
                    severity = "HIGH" if memory > 1000 else "MEDIUM"
                    self.bottlenecks.append(Bottleneck(
                        component=benchmark["name"],
                        metric="Memory",
                        value=memory,
                        threshold=500.0,
                        severity=severity,
                        recommendation=f"Reduce memory usage in {benchmark['name']} - currently {memory:.2f}MB (target: <500MB)"
                    ))

        # Check for poor speedups
        if "comparisons" in data:
            for comp in data["comparisons"]:
                if comp["speedup"] < 1.1:
                    self.bottlenecks.append(Bottleneck(
                        component=comp["approach_b_name"],
                        metric="Speedup",
                        value=comp["speedup"],
                        threshold=1.5,
                        severity="MEDIUM",
                        recommendation=f"{comp['approach_b_name']} shows minimal improvement over {comp['approach_a_name']} ({comp['speedup']:.2f}x speedup)"
                    ))

    def _generate_insights(self, data: Dict[str, Any]):
        """Generate performance insights and recommendations"""

        # Insight 1: Overall performance summary
        if "summary" in data:
            summary = data["summary"]
            success_rate = (summary["successful_benchmarks"] / summary["total_benchmarks"]) * 100

            if success_rate == 100:
                self.insights.append(PerformanceInsight(
                    category="SUCCESS",
                    title="All Benchmarks Passed",
                    description=f"All {summary['total_benchmarks']} benchmarks completed successfully.",
                    priority=3,
                    action_items=["Continue monitoring performance in production"]
                ))
            elif success_rate < 80:
                self.insights.append(PerformanceInsight(
                    category="WARNING",
                    title="Low Success Rate",
                    description=f"Only {success_rate:.1f}% of benchmarks passed ({summary['successful_benchmarks']}/{summary['total_benchmarks']}).",
                    priority=5,
                    action_items=[
                        "Investigate failing benchmarks",
                        "Check for infrastructure issues",
                        "Review error logs"
                    ]
                ))

        # Insight 2: Debate mechanism performance
        if "comparisons" in data:
            debate_comp = next((c for c in data["comparisons"] if "Debate" in c.get("approach_b_name", "")), None)
            if debate_comp:
                if debate_comp["approach_b_time"] < 25.0:
                    self.insights.append(PerformanceInsight(
                        category="SUCCESS",
                        title="Debate Mechanism Meets Performance Target",
                        description=f"Debate completes in {debate_comp['approach_b_time']:.2f}s (target: <30s) with {debate_comp['quality_improvement']:.1f}% quality improvement.",
                        priority=3,
                        action_items=["Consider enabling debates for more trades"]
                    ))
                elif debate_comp["approach_b_time"] > 28.0:
                    self.insights.append(PerformanceInsight(
                        category="WARNING",
                        title="Debate Mechanism Approaching Timeout",
                        description=f"Debate takes {debate_comp['approach_b_time']:.2f}s (timeout: 30s).",
                        priority=4,
                        action_items=[
                            "Optimize prompt length",
                            "Reduce number of debate rounds",
                            "Consider increasing timeout to 45s"
                        ]
                    ))

        # Insight 3: Concurrent processing benefits
        if "comparisons" in data:
            concurrent_comp = next((c for c in data["comparisons"] if "Concurrent" in c.get("approach_b_name", "")), None)
            if concurrent_comp and concurrent_comp["speedup"] > 2.0:
                self.insights.append(PerformanceInsight(
                    category="OPTIMIZATION",
                    title="Concurrent Processing Highly Effective",
                    description=f"Concurrent processing provides {concurrent_comp['speedup']:.2f}x speedup over sequential.",
                    priority=4,
                    action_items=[
                        "Use concurrent processing for all batch operations",
                        "Consider increasing concurrent task limit",
                        "Apply to other data-fetching operations"
                    ]
                ))

        # Insight 4: Alternative data impact
        if "comparisons" in data:
            alt_data_comp = next((c for c in data["comparisons"] if "Alt Data" in c.get("approach_b_name", "")), None)
            if alt_data_comp:
                time_overhead = alt_data_comp["approach_b_time"] - alt_data_comp["approach_a_time"]
                quality_improvement = alt_data_comp["quality_improvement"]

                if quality_improvement > 10 and time_overhead < 5.0:
                    self.insights.append(PerformanceInsight(
                        category="SUCCESS",
                        title="Alternative Data Provides Good ROI",
                        description=f"Alternative data adds {time_overhead:.2f}s overhead but improves quality by {quality_improvement:.1f}%.",
                        priority=3,
                        action_items=["Enable alternative data for all analysis"]
                    ))
                elif time_overhead > 10.0:
                    self.insights.append(PerformanceInsight(
                        category="OPTIMIZATION",
                        title="Alternative Data Fetching Slow",
                        description=f"Alternative data adds {time_overhead:.2f}s overhead.",
                        priority=4,
                        action_items=[
                            "Implement better caching for alt data",
                            "Use concurrent fetching for multiple sources",
                            "Consider reducing lookback periods"
                        ]
                    ))

        # Insight 5: Memory usage
        if "summary" in data and data["summary"]["max_memory_mb"] > 500:
            self.insights.append(PerformanceInsight(
                category="WARNING",
                title="High Memory Usage Detected",
                description=f"Peak memory usage: {data['summary']['max_memory_mb']:.2f}MB (target: <500MB).",
                priority=4,
                action_items=[
                    "Profile memory usage to find leaks",
                    "Implement data streaming for large datasets",
                    "Clear caches more aggressively"
                ]
            ))

    def get_metric_summary(self, metric_name: str, unit: str = "") -> Optional[MetricSummary]:
        """Get summary statistics for a metric"""
        if metric_name not in self.metrics:
            return None

        values = self.metrics[metric_name]

        return MetricSummary(
            name=metric_name,
            min_value=min(values),
            max_value=max(values),
            avg_value=statistics.mean(values),
            std_dev=statistics.stdev(values) if len(values) > 1 else 0.0,
            median=statistics.median(values),
            unit=unit
        )


# ============================================================================
# Report Generator
# ============================================================================

class ReportGenerator:
    """Generates formatted performance reports"""

    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer

    def generate_markdown_report(self, data: Dict[str, Any], output_path: str):
        """Generate comprehensive markdown report"""

        lines = []

        # Header
        lines.append("# Phase 2 Performance Analysis Report\n")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**Analysis Date:** {data.get('timestamp', 'N/A')}\n\n")
        lines.append("---\n\n")

        # Executive Summary
        lines.append("## Executive Summary\n\n")
        if "summary" in data:
            summary = data["summary"]
            lines.append(f"- **Total Benchmarks:** {summary['total_benchmarks']}\n")
            lines.append(f"- **Successful:** {summary['successful_benchmarks']} ✅\n")
            lines.append(f"- **Failed:** {summary['failed_benchmarks']} ❌\n")
            lines.append(f"- **Success Rate:** {(summary['successful_benchmarks']/summary['total_benchmarks']*100):.1f}%\n")
            lines.append(f"- **Average Duration:** {summary['avg_duration_seconds']:.3f}s\n")
            lines.append(f"- **Max Duration:** {summary['max_duration_seconds']:.3f}s\n")
            lines.append(f"- **Average Memory:** {summary['avg_memory_mb']:.2f}MB\n")
            lines.append(f"- **Max Memory:** {summary['max_memory_mb']:.2f}MB\n\n")

        # Key Insights
        lines.append("## Key Insights\n\n")
        if self.analyzer.insights:
            # Sort by priority (highest first)
            sorted_insights = sorted(self.analyzer.insights, key=lambda x: x.priority, reverse=True)

            for insight in sorted_insights:
                icon = {
                    "SUCCESS": "✅",
                    "WARNING": "⚠️",
                    "OPTIMIZATION": "💡",
                    "INFO": "ℹ️"
                }.get(insight.category, "📌")

                lines.append(f"### {icon} {insight.title} (Priority: {insight.priority}/5)\n\n")
                lines.append(f"{insight.description}\n\n")

                if insight.action_items:
                    lines.append("**Action Items:**\n")
                    for item in insight.action_items:
                        lines.append(f"- {item}\n")
                    lines.append("\n")
        else:
            lines.append("*No specific insights generated.*\n\n")

        # Performance Metrics
        lines.append("## Performance Metrics\n\n")

        # Duration metrics
        duration_summary = self.analyzer.get_metric_summary("duration", "seconds")
        if duration_summary:
            lines.append("### ⏱️ Timing\n\n")
            lines.append(f"- **Average:** {duration_summary.avg_value:.3f}s\n")
            lines.append(f"- **Median:** {duration_summary.median:.3f}s\n")
            lines.append(f"- **Min:** {duration_summary.min_value:.3f}s\n")
            lines.append(f"- **Max:** {duration_summary.max_value:.3f}s\n")
            lines.append(f"- **Std Dev:** {duration_summary.std_dev:.3f}s\n\n")

        # Memory metrics
        memory_summary = self.analyzer.get_metric_summary("memory", "MB")
        if memory_summary:
            lines.append("### 💾 Memory\n\n")
            lines.append(f"- **Average:** {memory_summary.avg_value:.2f}MB\n")
            lines.append(f"- **Median:** {memory_summary.median:.2f}MB\n")
            lines.append(f"- **Min:** {memory_summary.min_value:.2f}MB\n")
            lines.append(f"- **Max:** {memory_summary.max_value:.2f}MB\n")
            lines.append(f"- **Std Dev:** {memory_summary.std_dev:.2f}MB\n\n")

        # Speedup metrics
        speedup_summary = self.analyzer.get_metric_summary("speedup", "x")
        if speedup_summary:
            lines.append("### 🚀 Speedup\n\n")
            lines.append(f"- **Average:** {speedup_summary.avg_value:.2f}x\n")
            lines.append(f"- **Median:** {speedup_summary.median:.2f}x\n")
            lines.append(f"- **Min:** {speedup_summary.min_value:.2f}x\n")
            lines.append(f"- **Max:** {speedup_summary.max_value:.2f}x\n\n")

        # Quality improvement metrics
        quality_summary = self.analyzer.get_metric_summary("quality_improvement", "%")
        if quality_summary:
            lines.append("### 📈 Quality Improvement\n\n")
            lines.append(f"- **Average:** {quality_summary.avg_value:.1f}%\n")
            lines.append(f"- **Median:** {quality_summary.median:.1f}%\n")
            lines.append(f"- **Min:** {quality_summary.min_value:.1f}%\n")
            lines.append(f"- **Max:** {quality_summary.max_value:.1f}%\n\n")

        # Detailed Comparisons
        lines.append("## Detailed Comparisons\n\n")
        if "comparisons" in data:
            for comp in data["comparisons"]:
                lines.append(f"### {comp['approach_a_name']} vs {comp['approach_b_name']}\n\n")
                lines.append(f"| Metric | {comp['approach_a_name']} | {comp['approach_b_name']} | Improvement |\n")
                lines.append(f"|--------|----------|----------|-------------|\n")
                lines.append(f"| **Time** | {comp['approach_a_time']:.3f}s | {comp['approach_b_time']:.3f}s | {comp['speedup']:.2f}x |\n")
                lines.append(f"| **Quality** | {comp['approach_a_quality']:.2f} | {comp['approach_b_quality']:.2f} | +{comp['quality_improvement']:.1f}% |\n")
                lines.append(f"| **Winner** | | | **{comp['winner']}** |\n\n")

        # Bottlenecks
        lines.append("## Performance Bottlenecks\n\n")
        if self.analyzer.bottlenecks:
            # Sort by severity
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            sorted_bottlenecks = sorted(self.analyzer.bottlenecks, key=lambda x: severity_order.get(x.severity, 99))

            for bottleneck in sorted_bottlenecks:
                severity_icon = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(bottleneck.severity, "⚪")

                lines.append(f"### {severity_icon} {bottleneck.severity}: {bottleneck.component}\n\n")
                lines.append(f"- **Metric:** {bottleneck.metric}\n")
                lines.append(f"- **Value:** {bottleneck.value:.2f}\n")
                lines.append(f"- **Threshold:** {bottleneck.threshold:.2f}\n")
                lines.append(f"- **Recommendation:** {bottleneck.recommendation}\n\n")
        else:
            lines.append("✅ No significant bottlenecks detected.\n\n")

        # All Benchmark Results
        lines.append("## All Benchmark Results\n\n")
        if "benchmarks" in data:
            lines.append("| Benchmark Name | Duration (s) | Memory (MB) | Status |\n")
            lines.append("|----------------|--------------|-------------|--------|\n")

            for benchmark in data["benchmarks"]:
                status = "✅" if benchmark["success"] else "❌"
                duration = f"{benchmark['duration_seconds']:.3f}" if benchmark["success"] else "N/A"
                memory = f"{benchmark['memory_mb']:.2f}" if benchmark["success"] else "N/A"

                lines.append(f"| {benchmark['name']} | {duration} | {memory} | {status} |\n")
            lines.append("\n")

        # Footer
        lines.append("---\n\n")
        lines.append("*Report generated automatically by Phase 2 Performance Analyzer*\n")

        # Write to file
        with open(output_path, 'w') as f:
            f.writelines(lines)

        print(f"✅ Markdown report saved: {output_path}")

    def generate_json_report(self, data: Dict[str, Any], output_path: str):
        """Generate JSON report with analysis"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "original_data": data,
            "analysis": {
                "metrics": {
                    name: asdict(self.analyzer.get_metric_summary(name))
                    for name in self.analyzer.metrics.keys()
                },
                "bottlenecks": [asdict(b) for b in self.analyzer.bottlenecks],
                "insights": [asdict(i) for i in self.analyzer.insights]
            }
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ JSON report saved: {output_path}")


# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate Phase 2 performance analysis report")
    parser.add_argument(
        "--benchmark-file",
        type=str,
        help="Path to benchmark results JSON file",
        default=None
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("FILE1", "FILE2"),
        help="Compare two benchmark result files",
        default=None
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for reports",
        default="benchmarks/reports"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize analyzer
    analyzer = PerformanceAnalyzer()
    generator = ReportGenerator(analyzer)

    if args.compare:
        # Compare two benchmark files
        print(f"📊 Comparing benchmark files:")
        print(f"   File 1: {args.compare[0]}")
        print(f"   File 2: {args.compare[1]}")

        data1 = analyzer.load_benchmark_file(args.compare[0])
        data2 = analyzer.load_benchmark_file(args.compare[1])

        # Analyze both
        analyzer.analyze_benchmarks(data1)
        analyzer.analyze_benchmarks(data2)

        # Generate comparison report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_md = output_dir / f"comparison_report_{timestamp}.md"
        output_json = output_dir / f"comparison_report_{timestamp}.json"

        combined_data = {
            "timestamp": datetime.now().isoformat(),
            "file1": data1,
            "file2": data2,
            "summary": {
                "total_benchmarks": len(data1.get("benchmarks", [])) + len(data2.get("benchmarks", [])),
                "successful_benchmarks": sum(1 for b in data1.get("benchmarks", []) + data2.get("benchmarks", []) if b.get("success")),
                "failed_benchmarks": sum(1 for b in data1.get("benchmarks", []) + data2.get("benchmarks", []) if not b.get("success")),
                "avg_duration_seconds": 0,
                "max_duration_seconds": 0,
                "avg_memory_mb": 0,
                "max_memory_mb": 0
            }
        }

        generator.generate_markdown_report(combined_data, str(output_md))
        generator.generate_json_report(combined_data, str(output_json))

    else:
        # Analyze single benchmark file
        if args.benchmark_file:
            benchmark_file = args.benchmark_file
        else:
            # Find most recent benchmark file
            report_files = list(Path("benchmarks/reports").glob("performance_report_*.json"))
            if not report_files:
                print("❌ No benchmark files found. Run benchmarks first:")
                print("   python benchmarks/phase2_benchmarks.py")
                return

            benchmark_file = str(max(report_files, key=lambda p: p.stat().st_mtime))
            print(f"📁 Using most recent benchmark file: {benchmark_file}")

        # Load and analyze
        data = analyzer.load_benchmark_file(benchmark_file)
        analyzer.analyze_benchmarks(data)

        # Generate reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_md = output_dir / f"analysis_report_{timestamp}.md"
        output_json = output_dir / f"analysis_report_{timestamp}.json"

        generator.generate_markdown_report(data, str(output_md))
        generator.generate_json_report(data, str(output_json))

    print("\n✅ Report generation complete!")


if __name__ == "__main__":
    main()
