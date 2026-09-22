def design_summary_text(design) -> str:
    """Readable Slack mrkdwn rendering of a DesignSpecification, for the
    design-review message -- shown to the reviewer before Figma is touched."""
    lines = [f"*{design.feature_name}*", "", design.design_summary]

    for screen in design.screens:
        lines.append(f"\n*Screen: {screen.screen_name}*")
        lines.append(f"Purpose: {screen.purpose}")
        lines.append(f"Layout: {screen.layout}")
        if screen.components:
            lines.append("Components: " + ", ".join(c.name for c in screen.components))
        if screen.user_actions:
            lines.append("User actions: " + ", ".join(screen.user_actions))

    if design.reusable_components:
        lines.append("\nReusable components: " + ", ".join(design.reusable_components))
    if design.design_system_rules:
        lines.append("Design system rules: " + ", ".join(design.design_system_rules))
    if design.assumptions:
        lines.append("Assumptions: " + ", ".join(design.assumptions))

    return "\n".join(lines).strip()
