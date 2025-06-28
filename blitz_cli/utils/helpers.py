from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()
js_code = '''
function greet(name) {
    console.log(`Hello, ${name}`);
}
'''

Console().print(Syntax(js_code, "javascript", theme="monokai", line_numbers=True))

