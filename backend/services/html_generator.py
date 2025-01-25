from typing import List, Dict

class HTMLGenerator:
    @staticmethod
    def generate_table(data: List[Dict], columns: List[str]) -> str:
        if not data:
            return "<div class='no-results'>No results found</div>"
            
        html = """
        <div class="table-container">
            <table class="result-table">
                <thead>
                    <tr>%s</tr>
                </thead>
                <tbody>%s</tbody>
            </table>
        </div>
        """ % (
            "".join(f"<th>{col}</th>" for col in columns),
            "".join(
                f"<tr>%s</tr>" % "".join(f"<td>{row.get(col, '')}</td>" for col in columns)
                for row in data
            )
        )
        return html

    @staticmethod
    def error_template(message: str) -> str:
        return f"""
        <div class="error-alert">
            <div class="error-icon">!</div>
            <div class="error-message">{message}</div>
        </div>
        """