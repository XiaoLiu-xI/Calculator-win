import ast
import operator
import tkinter as tk


class Calculator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("简易计算器")
        self.root.geometry("320x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#f2f3f5")

        self.expression = tk.StringVar(value="0")
        self.display = tk.Entry(
            root,
            textvariable=self.expression,
            justify="right",
            font=("Microsoft YaHei", 28, "bold"),
            bd=0,
            relief="flat",
            bg="#ffffff",
            fg="#1f1f1f",
            highlightthickness=1,
            highlightbackground="#d9d9d9",
            highlightcolor="#4a90e2",
            state="readonly",
        )
        self.display.bind("<Key>", lambda event: "break")
        self.display.bind("<KeyRelease>", lambda event: "break")
        self.display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(10, 8))

        button_frame = tk.Frame(root, bg="#f2f3f5")
        button_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="nsew")

        buttons = [
            ("C", 0, 0, 1, 1), ("←", 0, 1, 1, 1), ("/", 0, 2, 1, 1), ("*", 0, 3, 1, 1),
            ("7", 1, 0, 1, 1), ("8", 1, 1, 1, 1), ("9", 1, 2, 1, 1), ("-", 1, 3, 1, 1),
            ("4", 2, 0, 1, 1), ("5", 2, 1, 1, 1), ("6", 2, 2, 1, 1), ("+", 2, 3, 1, 1),
            ("1", 3, 0, 1, 1), ("2", 3, 1, 1, 1), ("3", 3, 2, 1, 1), ("=", 3, 3, 1, 2),
            ("0", 4, 0, 2, 1), (".", 4, 2, 1, 1),
        ]

        for text, row, col, colspan, rowspan in buttons:
            button = tk.Button(
                button_frame,
                text=text,
                font=("Microsoft YaHei", 16, "bold"),
                width=4,
                height=2,
                bd=1,
                relief="raised",
                command=lambda value=text: self.on_click(value),
            )
            self._configure_button(button, text, row, col)
            button.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, sticky="nsew", padx=4, pady=4)
            button.bind("<ButtonPress-1>", lambda event, target=button: self._press_button(target))
            button.bind("<ButtonRelease-1>", lambda event, target=button: self._release_button(target))
            button.bind("<Leave>", lambda event, target=button: self._release_button(target))

        for index in range(4):
            button_frame.columnconfigure(index, weight=1)
        for index in range(5):
            button_frame.rowconfigure(index, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=0)
        root.rowconfigure(1, weight=1)

    def _configure_button(self, button: tk.Button, text: str, row: int, col: int) -> None:
        if text in {"/", "*", "-", "+", "="}:
            base_bg, fg, pressed_bg = "#4a90e2", "#ffffff", "#3b7dc0"
        elif text in {"C", "←"}:
            base_bg, fg, pressed_bg = "#f28b82", "#ffffff", "#d96b5f"
        else:
            base_bg = "#ffffff" if (row + col) % 2 == 0 else "#f6f7f8"
            fg, pressed_bg = "#1f1f1f", "#dfe3e8"

        button.configure(
            bg=base_bg,
            fg=fg,
            activebackground=pressed_bg,
            activeforeground=fg,
            highlightthickness=1,
            highlightbackground="#d0d0d0",
            highlightcolor="#4a90e2",
        )
        button._base_bg = base_bg
        button._base_fg = fg
        button._pressed_bg = pressed_bg
        button._pressed_fg = fg

    def _press_button(self, button: tk.Button) -> None:
        button.configure(bg=button._pressed_bg, relief="sunken", highlightbackground="#4a90e2")

    def _release_button(self, button: tk.Button) -> None:
        button.configure(bg=button._base_bg, relief="raised", highlightbackground="#d0d0d0")

    def on_click(self, value: str) -> None:
        current = self.expression.get()
        if value == "=":
            self.calculate()
            return
        if value == "C":
            self.expression.set("0")
            return
        if value == "←":
            if current in {"0", "Error", ""}:
                self.expression.set("0")
            else:
                self.expression.set(current[:-1] or "0")
            return

        if value in {"+", "-", "*", "/"}:
            if current in {"0", "Error", ""}:
                return
            if current[-1] in {"+", "-", "*", "/"}:
                return

        if current == "0" and value not in {".", "+", "-", "*", "/"}:
            current = ""
        elif current == "Error":
            current = ""

        self.expression.set(current + value)

    def calculate(self) -> None:
        expr = self.expression.get().strip()
        if not expr:
            expr = "0"

        try:
            result = self._safe_eval(expr)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression.set(str(result))
        except Exception:
            self.expression.set("Error")

    def _safe_eval(self, expression: str):
        allowed_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        node = ast.parse(expression, mode="eval").body

        def _eval(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                left = _eval(node.left)
                right = _eval(node.right)
                return allowed_ops[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.operand))
            raise ValueError("Unsupported expression")

        return _eval(node)


if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
