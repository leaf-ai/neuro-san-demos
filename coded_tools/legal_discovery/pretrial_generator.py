from neuro_san.interfaces.coded_tool import CodedTool


class PretrialGenerator(CodedTool):
    """Generate simple pretrial statements for accepted theories."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_statement(self, cause: str, elements: list[str]) -> str:
        """Return a pretrial statement summarising the elements for a cause."""

        lines = [f"Pretrial Statement for {cause}", ""]
        for el in elements:
            lines.append(f"- {el}")
        return "\n".join(lines)
