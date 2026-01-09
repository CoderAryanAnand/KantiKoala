from kkoala import create_app
from kkoala.routes.lernen import latex_to_html
import kkoala.routes.lernen

app = create_app("kkoala.config.ProdConfig")

# Define a known failing snippet structure if possible, or just raw string
# But we can't easily reproduce the user's specific failure without their file.
# However, if I run with a mock snippet that breaks, I can see the error flow.

test_latex = r"""
Broken TikZ
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\unknowncommand
\end{tikzpicture}
"""

with app.app_context():
    html = latex_to_html(test_latex)
    print(html)


