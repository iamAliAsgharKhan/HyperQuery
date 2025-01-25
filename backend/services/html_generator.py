from typing import List, Dict

class HTMLGenerator:
    @staticmethod
    def generate_table(data: List[Dict], columns: List[str]) -> str:
        """Generate HTML table with robust empty state handling"""
        if not columns:
            return "<div class='error'>No columns detected in query results</div>"
            
        headers = "".join(f"<th>{col}</th>" for col in columns)
        rows = "".join(
            f"<tr>{''.join(f'<td>{row.get(col, "")}</td>' for col in columns)}</tr>"
            for row in data
        )
        
        return f"""
        <div class="table-container">
            <table class="result-table">
                <thead><tr>{headers}</tr></thead>
                <tbody>{rows or '<tr><td colspan="100%">No results found</td></tr>'}</tbody>
            </table>
        </div>
        """

    @staticmethod
    def error_template(message: str) -> str:
        """Standard error display template"""
        return f"""
        <div class="error-alert">
            <div class="error-icon">!</div>
            <div class="error-message">{message}</div>
        </div>
        """