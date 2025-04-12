import tkinter as tk
from tkinter import simpledialog

class TreeNode:
    def __init__(self, canvas, x, y, text, parent=None, side=None, color="#ed7d31"):
        self.canvas = canvas
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.width = 80
        self.height = 40
        self.parent = parent
        self.side = side
        self.left = None
        self.right = None
        self.arrow_to_parent = None
        self.oval = None
        self.label = None
        self.resize_handle = None
        self.draw()
        self.bind_events()

    def draw(self):
        self.oval = self.canvas.create_oval(
            self.x - self.width // 2, self.y - self.height // 2,
            self.x + self.width // 2, self.y + self.height // 2,
            fill=self.color, outline="white", width=2
        )
        self.label = self.canvas.create_text(
            self.x, self.y, text=self.text, fill="white", font=("Arial", 10, "bold")
        )
        self.resize_handle = self.canvas.create_rectangle(
            self.x + self.width // 2 - 5, self.y + self.height // 2 - 5,
            self.x + self.width // 2 + 5, self.y + self.height // 2 + 5,
            fill="white", outline=self.color
        )

    def bind_events(self):
        for item in (self.oval, self.label):
            self.canvas.tag_bind(item, "<Button-1>", self.on_click)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_release)
            self.canvas.tag_bind(item, "<Double-Button-1>", self.rename_node)

        self.canvas.tag_bind(self.resize_handle, "<Button-1>", self.on_resize_click)
        self.canvas.tag_bind(self.resize_handle, "<B1-Motion>", self.on_resize_drag)

    def on_click(self, event):
        self.canvas.master.selected_node = self
        self.canvas.master.drag_start = (event.x, event.y)
        self.canvas.master.status_label.config(text=f"Selected: {self.text}")
        self.canvas.master.update_buttons()

    def on_drag(self, event):
        dx = event.x - self.canvas.master.drag_start[0]
        dy = event.y - self.canvas.master.drag_start[1]
        self.move(dx, dy)
        self.canvas.master.drag_start = (event.x, event.y)

    def on_release(self, event):
        pass

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        for item in (self.oval, self.label, self.resize_handle):
            self.canvas.move(item, dx, dy)

        if self.arrow_to_parent and self.parent:
            self.canvas.coords(
                self.arrow_to_parent,
                self.parent.x, self.parent.y + self.parent.height // 2,
                self.x, self.y - self.height // 2
            )

        if self.left:
            self.left.move(dx, dy)
        if self.right:
            self.right.move(dx, dy)

    def on_resize_click(self, event):
        self.canvas.master.drag_start = (event.x, event.y)

    def on_resize_drag(self, event):
        dx = event.x - self.canvas.master.drag_start[0]
        dy = event.y - self.canvas.master.drag_start[1]
        self.width = max(40, self.width + dx)
        self.height = max(20, self.height + dy)
        self.redraw()
        self.canvas.master.drag_start = (event.x, event.y)

    def redraw(self):
        self.canvas.coords(
            self.oval,
            self.x - self.width // 2, self.y - self.height // 2,
            self.x + self.width // 2, self.y + self.height // 2
        )
        self.canvas.coords(self.label, self.x, self.y)
        self.canvas.coords(
            self.resize_handle,
            self.x + self.width // 2 - 5, self.y + self.height // 2 - 5,
            self.x + self.width // 2 + 5, self.y + self.height // 2 + 5
        )
        if self.arrow_to_parent and self.parent:
            self.canvas.coords(
                self.arrow_to_parent,
                self.parent.x, self.parent.y + self.parent.height // 2,
                self.x, self.y - self.height // 2
            )

    def rename_node(self, event):
        new_text = simpledialog.askstring("Rename Node", "Enter new name:", initialvalue=self.text)
        if new_text:
            self.text = new_text
            self.canvas.itemconfig(self.label, text=new_text)
            self.canvas.master.status_label.config(text=f"Renamed to: {self.text}")

    def delete(self):
        if self.left:
            self.left.delete()
        if self.right:
            self.right.delete()

        if self.parent:
            if self.side == "left":
                self.parent.left = None
            elif self.side == "right":
                self.parent.right = None

        for item in (self.oval, self.label, self.arrow_to_parent, self.resize_handle):
            if item:
                self.canvas.delete(item)


class TreeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tree Builder with HTML Export")
        self.geometry("1000x700")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(self)
        control_frame.pack()

        tk.Button(control_frame, text="Add Left", command=lambda: self.add_node("left")).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Add Right", command=lambda: self.add_node("right")).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Delete Node", command=self.delete_node).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Export HTML", command=self.generate_html).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(control_frame, text="Select a node to add/delete/rename", fg="blue")
        self.status_label.pack(pady=5)

        self.selected_node = None
        self.drag_start = (0, 0)

        self.root_node = TreeNode(self.canvas, 500, 50, "root")
        self.selected_node = self.root_node

    def update_buttons(self):
        pass

    def add_node(self, direction):
        if not self.selected_node:
            return

        if direction == "left" and self.selected_node.left:
            self.status_label.config(text="Left child already exists.")
            return
        if direction == "right" and self.selected_node.right:
            self.status_label.config(text="Right child already exists.")
            return

        name = simpledialog.askstring("New Node", f"Enter name for {direction} child:", parent=self)
        if not name:
            return

        color_code = simpledialog.askstring("Node Color", "Enter HEX color (e.g. #ed7d31):", initialvalue="#ed7d31", parent=self)
        if not color_code or not color_code.startswith("#") or len(color_code) not in [4, 7]:
            self.status_label.config(text="Invalid HEX color. Using default.")
            color_code = "#ed7d31"

        x_offset = -150 if direction == "left" else 150
        x = self.selected_node.x + x_offset
        y = self.selected_node.y + 100

        node = TreeNode(self.canvas, x, y, name, parent=self.selected_node, side=direction, color=color_code)

        if direction == "left":
            self.selected_node.left = node
        else:
            self.selected_node.right = node

        arrow = self.canvas.create_line(
            self.selected_node.x, self.selected_node.y + self.selected_node.height // 2,
            x, y - node.height // 2,
            arrow=tk.LAST, fill="gray", width=2
        )
        node.arrow_to_parent = arrow
        node.on_click(None)

    def delete_node(self):
        if not self.selected_node or self.selected_node == self.root_node:
            return
        self.status_label.config(text=f"Deleted: {self.selected_node.text}")
        self.selected_node.delete()
        self.selected_node = None

    def generate_html(self):
        html = """<!DOCTYPE html>
<html><head><style>
.node {
  position: absolute;
  color: white;
  text-align: center;
  border-radius: 12px;
  font-family: Arial;
  font-weight: bold;
  padding: 4px;
}
.arrow {
  position: absolute;
  pointer-events: none;
}
</style></head><body>
<div style="position: relative; width: 2000px; height: 2000px;">\n"""
        lines = []

        def add_node_div(node):
            nonlocal html
            node_div = f"<div class='node' style='left: {node.x - node.width//2}px; top: {node.y - node.height//2}px; width: {node.width}px; height: {node.height}px; background-color: {node.color};'>{node.text}</div>\n"
            html += node_div
            if node.left:
                add_node_div(node.left)
            if node.right:
                add_node_div(node.right)

        def add_arrow_lines(node):
            if node.left:
                lines.append(self._arrow_svg(node, node.left))
                add_arrow_lines(node.left)
            if node.right:
                lines.append(self._arrow_svg(node, node.right))
                add_arrow_lines(node.right)

        add_node_div(self.root_node)
        add_arrow_lines(self.root_node)

        html += "".join(lines)
        html += "</div></body></html>"

        # Show in a popup instead of saving to file
        popup = tk.Toplevel(self)
        popup.title("Generated HTML")
        popup.geometry("800x600")

        text_widget = tk.Text(popup, wrap="none", bg="black", fg="white", insertbackground="white")
        text_widget.insert("1.0", html)
        text_widget.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(popup, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)

    def _arrow_svg(self, parent, child):
        start_y = parent.y + parent.height // 2 + 10
        end_y = child.y - child.height // 2 - 5
        return f"""
<svg class="arrow" style="left:0;top:0;width:2000px;height:2000px;">
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
<path d="M0,0 L0,6 L9,3 z" fill="gray" />
</marker></defs>
<line x1="{parent.x}" y1="{start_y}" x2="{child.x}" y2="{end_y}" stroke="gray" stroke-width="2" marker-end="url(#arrow)" />
</svg>
"""

if __name__ == "__main__":
    app = TreeApp()
    app.mainloop()
