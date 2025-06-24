#!/usr/bin/env python3
"""Advanced CLI Commands for SME Agent
Phase 11.4: Advanced SME Agent Features

This module provides CLI commands for advanced SME Agent features following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Modular component testing
5. Progressive complexity support
6. Resource management and cleanup
"""

import asyncio
import json
import logging
from pathlib import Path

import click

from ..enhanced_code_intelligence import (
    EnhancedCodeIntelligence,
    validate_enhanced_code_intelligence_environment,
)
from ..proactive_development_assistance import (
    ProactiveDevelopmentAssistance,
    validate_proactive_development_environment,
)
from ..specialized_domain_expertise import (
    SpecializedDomainExpertise,
    validate_specialized_domain_environment,
)

logger = logging.getLogger(__name__)


@click.group(name="advanced")
@click.pass_context
def advanced_commands(ctx):
    """Advanced SME Agent features and capabilities."""
    if ctx.obj is None:
        ctx.obj = {}


# Specialized Domain Expertise Commands


@advanced_commands.group(name="domain")
@click.pass_context
def domain_commands(ctx):
    """Specialized domain expertise commands."""
    pass


@domain_commands.command(name="validate-env")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def validate_domain_environment(ctx, verbose):
    """Validate specialized domain expertise environment."""
    try:
        result = asyncio.run(validate_specialized_domain_environment())

        if result["valid"]:
            click.echo(
                click.style(
                    "✅ Specialized domain expertise environment is valid", fg="green"
                )
            )
            if verbose and result.get("warnings"):
                for warning in result["warnings"]:
                    click.echo(click.style(f"⚠️  {warning}", fg="yellow"))
        else:
            click.echo(click.style("❌ Environment validation failed", fg="red"))
            for error in result.get("errors", []):
                click.echo(click.style(f"   • {error}", fg="red"))
            ctx.exit(1)

    except Exception as e:
        click.echo(click.style(f"❌ Validation failed: {e!s}", fg="red"))
        ctx.exit(1)


@domain_commands.command(name="info")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def domain_info(ctx, format):
    """Get specialized domain expertise information."""
    try:
        from ..specialized_domain_expertise import get_specialized_domain_info

        info = get_specialized_domain_info()

        if format == "json":
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo(
                click.style("🔬 Specialized Domain Expertise", fg="blue", bold=True)
            )
            click.echo(f"Module: {info['module']}")
            click.echo(f"Version: {info['version']}")
            click.echo(f"Knowledge Areas: {len(info['knowledge_areas'])}")
            click.echo(f"Complexity Levels: {', '.join(info['complexity_levels'])}")

            click.echo("\n📋 Capabilities:")
            for capability in info["capabilities"]:
                click.echo(f"  • {capability}")

    except Exception as e:
        click.echo(click.style(f"❌ Failed to get domain info: {e!s}", fg="red"))
        ctx.exit(1)


@domain_commands.command(name="query")
@click.argument("domain", type=str)
@click.argument("question", type=str)
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.option("--context", type=str, help="Additional context for the query")
@click.pass_context
def domain_query(ctx, domain, question, complexity, context):
    """Query specialized domain expertise."""
    try:

        async def run_query():
            expertise = SpecializedDomainExpertise()
            await expertise.initialize()

            context_dict = {}
            if context:
                try:
                    context_dict = json.loads(context)
                except json.JSONDecodeError:
                    context_dict = {"additional_info": context}

            result = await expertise.query_domain_expertise(
                domain=domain,
                question=question,
                context=context_dict,
                complexity=complexity,
            )

            if result["status"] == "success":
                response = result["response"]
                click.echo(click.style(f"🔬 Domain: {domain}", fg="blue", bold=True))
                click.echo(click.style(f"📝 Question: {question}", fg="cyan"))
                click.echo(click.style(f"🎯 Complexity: {complexity}", fg="magenta"))
                click.echo()

                click.echo(click.style("💡 Answer:", fg="green", bold=True))
                click.echo(response.get("answer", "No answer provided"))

                if response.get("recommendations"):
                    click.echo(
                        click.style("\n📋 Recommendations:", fg="yellow", bold=True)
                    )
                    for rec in response["recommendations"]:
                        click.echo(f"  • {rec}")

                if response.get("references"):
                    click.echo(click.style("\n📚 References:", fg="blue", bold=True))
                    for ref in response["references"]:
                        click.echo(f"  • {ref}")

            else:
                click.echo(
                    click.style(f"❌ Query failed: {result['message']}", fg="red")
                )
                ctx.exit(1)

        asyncio.run(run_query())

    except Exception as e:
        click.echo(click.style(f"❌ Domain query failed: {e!s}", fg="red"))
        ctx.exit(1)


@domain_commands.command(name="troubleshoot")
@click.argument("system_type", type=str)
@click.argument("symptoms", type=str)
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.option("--environment", type=str, help="Environment details (JSON)")
@click.pass_context
def domain_troubleshoot(ctx, system_type, symptoms, complexity, environment):
    """Get troubleshooting guidance for system issues."""
    try:

        async def run_troubleshoot():
            expertise = SpecializedDomainExpertise()
            await expertise.initialize()

            symptoms_list = [s.strip() for s in symptoms.split(",")]
            env_dict = {}
            if environment:
                try:
                    env_dict = json.loads(environment)
                except json.JSONDecodeError:
                    env_dict = {"description": environment}

            result = await expertise.provide_troubleshooting_guidance(
                system_type=system_type,
                symptoms=symptoms_list,
                environment_context=env_dict,
                complexity=complexity,
            )

            if result["status"] == "success":
                guidance = result["guidance"]
                click.echo(
                    click.style(f"🔧 System: {system_type}", fg="blue", bold=True)
                )
                click.echo(
                    click.style(f"⚠️  Symptoms: {', '.join(symptoms_list)}", fg="yellow")
                )
                click.echo()

                if guidance.get("likely_causes"):
                    click.echo(click.style("🎯 Likely Causes:", fg="red", bold=True))
                    for cause in guidance["likely_causes"]:
                        click.echo(f"  • {cause}")

                if guidance.get("diagnostic_steps"):
                    click.echo(
                        click.style("\n🔍 Diagnostic Steps:", fg="cyan", bold=True)
                    )
                    for i, step in enumerate(guidance["diagnostic_steps"], 1):
                        click.echo(f"  {i}. {step}")

                if guidance.get("resolution_steps"):
                    click.echo(
                        click.style("\n🛠️  Resolution Steps:", fg="green", bold=True)
                    )
                    for i, step in enumerate(guidance["resolution_steps"], 1):
                        click.echo(f"  {i}. {step}")

            else:
                click.echo(
                    click.style(
                        f"❌ Troubleshooting failed: {result['message']}", fg="red"
                    )
                )
                ctx.exit(1)

        asyncio.run(run_troubleshoot())

    except Exception as e:
        click.echo(click.style(f"❌ Troubleshooting failed: {e!s}", fg="red"))
        ctx.exit(1)


# Proactive Development Assistance Commands


@advanced_commands.group(name="assist")
@click.pass_context
def assistance_commands(ctx):
    """Proactive development assistance commands."""
    pass


@assistance_commands.command(name="validate-env")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def validate_assistance_environment(ctx, verbose):
    """Validate proactive development assistance environment."""
    try:
        result = asyncio.run(validate_proactive_development_environment())

        if result["valid"]:
            click.echo(
                click.style(
                    "✅ Proactive development assistance environment is valid",
                    fg="green",
                )
            )
            if verbose and result.get("warnings"):
                for warning in result["warnings"]:
                    click.echo(click.style(f"⚠️  {warning}", fg="yellow"))
        else:
            click.echo(click.style("❌ Environment validation failed", fg="red"))
            for error in result.get("errors", []):
                click.echo(click.style(f"   • {error}", fg="red"))
            ctx.exit(1)

    except Exception as e:
        click.echo(click.style(f"❌ Validation failed: {e!s}", fg="red"))
        ctx.exit(1)


@assistance_commands.command(name="info")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def assistance_info(ctx, format):
    """Get proactive development assistance information."""
    try:
        from ..proactive_development_assistance import get_proactive_development_info

        info = get_proactive_development_info()

        if format == "json":
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo(
                click.style("🚀 Proactive Development Assistance", fg="blue", bold=True)
            )
            click.echo(f"Module: {info['module']}")
            click.echo(f"Version: {info['version']}")
            click.echo(
                f"Architecture Patterns: {', '.join(info['architecture_patterns'])}"
            )
            click.echo(f"Component Types: {', '.join(info['component_types'])}")

            click.echo("\n📋 Capabilities:")
            for capability in info["capabilities"]:
                click.echo(f"  • {capability}")

    except Exception as e:
        click.echo(click.style(f"❌ Failed to get assistance info: {e!s}", fg="red"))
        ctx.exit(1)


@assistance_commands.command(name="suggest-architecture")
@click.argument("requirements", type=str)
@click.option("--constraints", type=str, help="Project constraints (JSON)")
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.pass_context
def suggest_architecture(ctx, requirements, constraints, complexity):
    """Suggest architecture patterns based on project requirements."""
    try:

        async def run_suggestion():
            assistance = ProactiveDevelopmentAssistance()
            await assistance.initialize()

            try:
                requirements_dict = json.loads(requirements)
            except json.JSONDecodeError:
                requirements_dict = {"description": requirements}

            constraints_dict = {}
            if constraints:
                try:
                    constraints_dict = json.loads(constraints)
                except json.JSONDecodeError:
                    constraints_dict = {"description": constraints}

            result = await assistance.suggest_architecture_pattern(
                project_requirements=requirements_dict,
                constraints=constraints_dict,
                complexity=complexity,
            )

            if result["status"] == "success":
                suggestions = result["suggestions"]
                click.echo(
                    click.style(
                        "🏗️  Architecture Pattern Suggestions", fg="blue", bold=True
                    )
                )
                click.echo(f"Complexity Level: {complexity}")
                click.echo(f"Patterns Analyzed: {result['patterns_analyzed']}")
                click.echo()

                for i, pattern in enumerate(
                    suggestions.get("recommended_patterns", []), 1
                ):
                    click.echo(
                        click.style(f"{i}. {pattern['name']}", fg="green", bold=True)
                    )
                    click.echo(f"   Description: {pattern['description']}")
                    click.echo(f"   Fit Score: {pattern['fit_score']:.1f}%")

                    if pattern.get("advantages"):
                        click.echo("   Advantages:")
                        for adv in pattern["advantages"][:3]:  # Show top 3
                            click.echo(f"     • {adv}")
                    click.echo()

            else:
                click.echo(
                    click.style(
                        f"❌ Architecture suggestion failed: {result['message']}",
                        fg="red",
                    )
                )
                ctx.exit(1)

        asyncio.run(run_suggestion())

    except Exception as e:
        click.echo(click.style(f"❌ Architecture suggestion failed: {e!s}", fg="red"))
        ctx.exit(1)


@assistance_commands.command(name="optimize-components")
@click.argument("components", type=str)
@click.argument("requirements", type=str)
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.pass_context
def optimize_components(ctx, components, requirements, complexity):
    """Optimize component selection and configuration."""
    try:

        async def run_optimization():
            assistance = ProactiveDevelopmentAssistance()
            await assistance.initialize()

            components_list = [c.strip() for c in components.split(",")]

            try:
                requirements_dict = json.loads(requirements)
            except json.JSONDecodeError:
                requirements_dict = {"description": requirements}

            result = await assistance.optimize_component_selection(
                system_components=components_list,
                performance_requirements=requirements_dict,
                complexity=complexity,
            )

            if result["status"] == "success":
                optimizations = result["optimizations"]
                click.echo(
                    click.style(
                        "⚡ Component Optimization Recommendations",
                        fg="blue",
                        bold=True,
                    )
                )
                click.echo(f"Components: {', '.join(components_list)}")
                click.echo(f"Recommendations Found: {result['recommendations_found']}")
                click.echo()

                for rec in optimizations.get("component_recommendations", []):
                    click.echo(
                        click.style(
                            f"🔧 {rec['component_name']}", fg="green", bold=True
                        )
                    )
                    click.echo(f"   Type: {rec['component_type']}")
                    click.echo(f"   Performance Impact: {rec['performance_impact']}")

                    if rec.get("optimization_tips"):
                        click.echo("   Optimization Tips:")
                        for tip in rec["optimization_tips"][:3]:  # Show top 3
                            click.echo(f"     • {tip}")
                    click.echo()

            else:
                click.echo(
                    click.style(
                        f"❌ Component optimization failed: {result['message']}",
                        fg="red",
                    )
                )
                ctx.exit(1)

        asyncio.run(run_optimization())

    except Exception as e:
        click.echo(click.style(f"❌ Component optimization failed: {e!s}", fg="red"))
        ctx.exit(1)


# Enhanced Code Intelligence Commands


@advanced_commands.group(name="code")
@click.pass_context
def code_commands(ctx):
    """Enhanced code intelligence commands."""
    pass


@code_commands.command(name="validate-env")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def validate_code_environment(ctx, verbose):
    """Validate enhanced code intelligence environment."""
    try:
        result = asyncio.run(validate_enhanced_code_intelligence_environment())

        if result["valid"]:
            click.echo(
                click.style(
                    "✅ Enhanced code intelligence environment is valid", fg="green"
                )
            )
            if verbose and result.get("warnings"):
                for warning in result["warnings"]:
                    click.echo(click.style(f"⚠️  {warning}", fg="yellow"))
        else:
            click.echo(click.style("❌ Environment validation failed", fg="red"))
            for error in result.get("errors", []):
                click.echo(click.style(f"   • {error}", fg="red"))
            ctx.exit(1)

    except Exception as e:
        click.echo(click.style(f"❌ Validation failed: {e!s}", fg="red"))
        ctx.exit(1)


@code_commands.command(name="info")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def code_info(ctx, format):
    """Get enhanced code intelligence information."""
    try:
        from ..enhanced_code_intelligence import get_enhanced_code_intelligence_info

        info = get_enhanced_code_intelligence_info()

        if format == "json":
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo(
                click.style("🧠 Enhanced Code Intelligence", fg="blue", bold=True)
            )
            click.echo(f"Module: {info['module']}")
            click.echo(f"Version: {info['version']}")
            click.echo(f"Analysis Types: {', '.join(info['analysis_types'])}")
            click.echo(f"Pattern Types: {', '.join(info['pattern_types'])}")

            click.echo("\n📋 Capabilities:")
            for capability in info["capabilities"]:
                click.echo(f"  • {capability}")

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to get code intelligence info: {e!s}", fg="red")
        )
        ctx.exit(1)


@code_commands.command(name="analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--analysis-type",
    "-t",
    type=click.Choice(["comprehensive", "refactoring", "patterns", "quality"]),
    default="comprehensive",
    help="Type of analysis",
)
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "summary"]),
    default="summary",
    help="Output format",
)
@click.pass_context
def analyze_code(ctx, file_path, analysis_type, complexity, format):
    """Analyze a code file for quality, patterns, and refactoring opportunities."""
    try:

        async def run_analysis():
            intelligence = EnhancedCodeIntelligence()
            await intelligence.initialize()

            result = await intelligence.analyze_code_file(
                file_path=str(file_path),
                analysis_type=analysis_type,
                complexity=complexity,
            )

            if result["status"] == "success":
                analysis = result["analysis"]

                if format == "json":
                    # Convert dataclass to dict for JSON serialization
                    analysis_dict = {
                        "file_path": analysis.file_path,
                        "analysis_type": analysis.analysis_type,
                        "complexity_score": analysis.complexity_score,
                        "quality_score": analysis.quality_score,
                        "maintainability_score": analysis.maintainability_score,
                        "issues": analysis.issues,
                        "recommendations": analysis.recommendations,
                        "refactoring_opportunities": analysis.refactoring_opportunities,
                        "dependencies": analysis.dependencies,
                        "metrics": analysis.metrics,
                        "ignition_specific_issues": analysis.ignition_specific_issues,
                    }
                    click.echo(json.dumps(analysis_dict, indent=2))
                else:
                    click.echo(
                        click.style(
                            f"🧠 Code Analysis: {Path(file_path).name}",
                            fg="blue",
                            bold=True,
                        )
                    )
                    click.echo(f"Analysis Type: {analysis_type}")
                    click.echo(f"Complexity Level: {complexity}")
                    click.echo()

                    # Scores
                    click.echo(click.style("📊 Scores:", fg="cyan", bold=True))
                    click.echo(f"  Quality: {analysis.quality_score:.1f}/100")
                    click.echo(
                        f"  Complexity: {analysis.complexity_score:.1f}/100 (lower is better)"
                    )
                    click.echo(
                        f"  Maintainability: {analysis.maintainability_score:.1f}/100"
                    )
                    click.echo()

                    # Metrics
                    if analysis.metrics:
                        click.echo(click.style("📏 Metrics:", fg="magenta", bold=True))
                        for key, value in analysis.metrics.items():
                            click.echo(f"  {key.replace('_', ' ').title()}: {value}")
                        click.echo()

                    # Issues
                    if analysis.issues:
                        click.echo(click.style("⚠️  Issues:", fg="red", bold=True))
                        for issue in analysis.issues[:5]:  # Show top 5
                            severity = issue.get("severity", "Unknown")
                            color = (
                                "red"
                                if severity == "High"
                                else "yellow" if severity == "Medium" else "white"
                            )
                            click.echo(
                                click.style(
                                    f"  [{severity}] {issue.get('message', 'No message')}",
                                    fg=color,
                                )
                            )
                        if len(analysis.issues) > 5:
                            click.echo(
                                f"  ... and {len(analysis.issues) - 5} more issues"
                            )
                        click.echo()

                    # Recommendations
                    if analysis.recommendations:
                        click.echo(
                            click.style("💡 Recommendations:", fg="green", bold=True)
                        )
                        for rec in analysis.recommendations[:5]:  # Show top 5
                            click.echo(f"  • {rec}")
                        if len(analysis.recommendations) > 5:
                            click.echo(
                                f"  ... and {len(analysis.recommendations) - 5} more recommendations"
                            )

            else:
                click.echo(
                    click.style(
                        f"❌ Code analysis failed: {result['message']}", fg="red"
                    )
                )
                ctx.exit(1)

        asyncio.run(run_analysis())

    except Exception as e:
        click.echo(click.style(f"❌ Code analysis failed: {e!s}", fg="red"))
        ctx.exit(1)


@code_commands.command(name="suggest-refactoring")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--focus", type=str, help="Focus areas (comma-separated)")
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.pass_context
def suggest_refactoring(ctx, file_path, focus, complexity):
    """Generate intelligent refactoring suggestions."""
    try:

        async def run_suggestion():
            intelligence = EnhancedCodeIntelligence()
            await intelligence.initialize()

            focus_areas = []
            if focus:
                focus_areas = [f.strip() for f in focus.split(",")]

            result = await intelligence.generate_refactoring_suggestions(
                file_path=str(file_path), focus_areas=focus_areas, complexity=complexity
            )

            if result["status"] == "success":
                suggestions = result["suggestions"]
                click.echo(
                    click.style(
                        f"🔧 Refactoring Suggestions: {Path(file_path).name}",
                        fg="blue",
                        bold=True,
                    )
                )
                click.echo(
                    f"Focus Areas: {', '.join(focus_areas) if focus_areas else 'All'}"
                )
                click.echo(f"Suggestions Generated: {len(suggestions)}")
                click.echo()

                for i, suggestion in enumerate(suggestions, 1):
                    priority_color = (
                        "red"
                        if suggestion.priority == "High"
                        else "yellow" if suggestion.priority == "Medium" else "white"
                    )
                    click.echo(
                        click.style(
                            f"{i}. {suggestion.description}", fg="green", bold=True
                        )
                    )
                    click.echo(
                        click.style(
                            f"   Priority: {suggestion.priority}", fg=priority_color
                        )
                    )
                    click.echo(f"   Type: {suggestion.suggestion_type}")
                    click.echo(f"   Rationale: {suggestion.rationale}")

                    if suggestion.implementation_steps:
                        click.echo("   Implementation Steps:")
                        for step in suggestion.implementation_steps[:3]:  # Show top 3
                            click.echo(f"     • {step}")
                    click.echo()

            else:
                click.echo(
                    click.style(
                        f"❌ Refactoring suggestion failed: {result['message']}",
                        fg="red",
                    )
                )
                ctx.exit(1)

        asyncio.run(run_suggestion())

    except Exception as e:
        click.echo(click.style(f"❌ Refactoring suggestion failed: {e!s}", fg="red"))
        ctx.exit(1)


@code_commands.command(name="detect-patterns")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--pattern-types", type=str, help="Pattern types to search (comma-separated)"
)
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Complexity level",
)
@click.pass_context
def detect_patterns(ctx, file_path, pattern_types, complexity):
    """Detect code patterns and anti-patterns."""
    try:

        async def run_detection():
            intelligence = EnhancedCodeIntelligence()
            await intelligence.initialize()

            types_list = []
            if pattern_types:
                types_list = [t.strip() for t in pattern_types.split(",")]

            result = await intelligence.detect_code_patterns(
                file_path=str(file_path),
                pattern_types=types_list,
                complexity=complexity,
            )

            if result["status"] == "success":
                patterns = result["patterns"]
                click.echo(
                    click.style(
                        f"🔍 Pattern Detection: {Path(file_path).name}",
                        fg="blue",
                        bold=True,
                    )
                )
                click.echo(
                    f"Pattern Types Searched: {', '.join(types_list) if types_list else 'All'}"
                )
                click.echo(f"Patterns Detected: {len(patterns)}")
                click.echo()

                for pattern in patterns:
                    severity_color = (
                        "red"
                        if pattern["severity"] == "High"
                        else "yellow" if pattern["severity"] == "Medium" else "white"
                    )
                    ignition_marker = "🎯 " if pattern["ignition_specific"] else ""

                    click.echo(
                        click.style(
                            f"{ignition_marker}{pattern['pattern_name']}",
                            fg="green",
                            bold=True,
                        )
                    )
                    click.echo(
                        click.style(
                            f"   Severity: {pattern['severity']}", fg=severity_color
                        )
                    )
                    click.echo(f"   Type: {pattern['pattern_type']}")
                    click.echo(f"   Description: {pattern['description']}")

                    if pattern.get("fix_suggestions"):
                        click.echo("   Fix Suggestions:")
                        for suggestion in pattern["fix_suggestions"][:2]:  # Show top 2
                            click.echo(f"     • {suggestion}")
                    click.echo()

            else:
                click.echo(
                    click.style(
                        f"❌ Pattern detection failed: {result['message']}", fg="red"
                    )
                )
                ctx.exit(1)

        asyncio.run(run_detection())

    except Exception as e:
        click.echo(click.style(f"❌ Pattern detection failed: {e!s}", fg="red"))
        ctx.exit(1)


# Statistics and Status Commands


@advanced_commands.command(name="status")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def advanced_status(ctx, format):
    """Get status of all advanced SME Agent features."""
    try:

        async def get_status():
            status = {
                "specialized_domain": {"available": False, "statistics": {}},
                "proactive_assistance": {"available": False, "statistics": {}},
                "code_intelligence": {"available": False, "statistics": {}},
            }

            # Check specialized domain expertise
            try:
                expertise = SpecializedDomainExpertise()
                await expertise.initialize()
                status["specialized_domain"]["available"] = True
                status["specialized_domain"][
                    "statistics"
                ] = await expertise.get_expertise_statistics()
            except Exception as e:
                status["specialized_domain"]["error"] = str(e)

            # Check proactive development assistance
            try:
                assistance = ProactiveDevelopmentAssistance()
                await assistance.initialize()
                status["proactive_assistance"]["available"] = True
                status["proactive_assistance"][
                    "statistics"
                ] = await assistance.get_assistance_statistics()
            except Exception as e:
                status["proactive_assistance"]["error"] = str(e)

            # Check enhanced code intelligence
            try:
                intelligence = EnhancedCodeIntelligence()
                await intelligence.initialize()
                status["code_intelligence"]["available"] = True
                status["code_intelligence"][
                    "statistics"
                ] = await intelligence.get_intelligence_statistics()
            except Exception as e:
                status["code_intelligence"]["error"] = str(e)

            return status

        status = asyncio.run(get_status())

        if format == "json":
            click.echo(json.dumps(status, indent=2))
        else:
            click.echo(
                click.style(
                    "🚀 Advanced SME Agent Features Status", fg="blue", bold=True
                )
            )
            click.echo()

            # Specialized Domain Expertise
            if status["specialized_domain"]["available"]:
                click.echo(
                    click.style(
                        "✅ Specialized Domain Expertise", fg="green", bold=True
                    )
                )
                stats = status["specialized_domain"]["statistics"].get("statistics", {})
                click.echo(f"   Queries Processed: {stats.get('queries_processed', 0)}")
                click.echo(
                    f"   Knowledge Areas: {stats.get('knowledge_areas_loaded', 0)}"
                )
            else:
                click.echo(
                    click.style("❌ Specialized Domain Expertise", fg="red", bold=True)
                )
                if "error" in status["specialized_domain"]:
                    click.echo(f"   Error: {status['specialized_domain']['error']}")
            click.echo()

            # Proactive Development Assistance
            if status["proactive_assistance"]["available"]:
                click.echo(
                    click.style(
                        "✅ Proactive Development Assistance", fg="green", bold=True
                    )
                )
                stats = status["proactive_assistance"]["statistics"].get(
                    "statistics", {}
                )
                click.echo(
                    f"   Recommendations Generated: {stats.get('recommendations_generated', 0)}"
                )
                click.echo(
                    f"   Architecture Patterns: {stats.get('architecture_patterns_loaded', 0)}"
                )
            else:
                click.echo(
                    click.style(
                        "❌ Proactive Development Assistance", fg="red", bold=True
                    )
                )
                if "error" in status["proactive_assistance"]:
                    click.echo(f"   Error: {status['proactive_assistance']['error']}")
            click.echo()

            # Enhanced Code Intelligence
            if status["code_intelligence"]["available"]:
                click.echo(
                    click.style("✅ Enhanced Code Intelligence", fg="green", bold=True)
                )
                stats = status["code_intelligence"]["statistics"].get("statistics", {})
                click.echo(f"   Files Analyzed: {stats.get('files_analyzed', 0)}")
                click.echo(f"   Patterns Detected: {stats.get('patterns_detected', 0)}")
            else:
                click.echo(
                    click.style("❌ Enhanced Code Intelligence", fg="red", bold=True)
                )
                if "error" in status["code_intelligence"]:
                    click.echo(f"   Error: {status['code_intelligence']['error']}")

    except Exception as e:
        click.echo(click.style(f"❌ Status check failed: {e!s}", fg="red"))
        ctx.exit(1)


# Export commands for CLI integration
def get_advanced_commands():
    """Get advanced commands for CLI integration."""
    return advanced_commands
