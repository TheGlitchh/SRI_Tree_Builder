import customtkinter as ctk
from tkinter import simpledialog, Canvas
import tkinter as tk

# Configure the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class RenameDialog(ctk.CTkToplevel):
    def __init__(self, parent, node):
        super().__init__(parent)
        self.node = node
        self.title("Rename and Change Color")
        self.geometry("400x300")
        
        # Create frame for content
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Name input
        self.name_label = ctk.CTkLabel(frame, text="Enter new name:")
        self.name_label.pack(pady=5)
        self.name_entry = ctk.CTkEntry(frame, width=300)
        self.name_entry.insert(0, self.node.text)
        self.name_entry.pack(pady=5)
        
        # Color input
        self.color_label = ctk.CTkLabel(frame, text="Enter new HEX color (e.g. #ed7d31):")
        self.color_label.pack(pady=5)
        self.color_entry = ctk.CTkEntry(frame, width=300)
        self.color_entry.insert(0, self.node.color)
        self.color_entry.pack(pady=5)
        
        # Button frame
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Buttons
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left", padx=10)
        
        self.submit_button = ctk.CTkButton(button_frame, text="Apply", command=self.apply_changes)
        self.submit_button.pack(side="left", padx=10)
        
        # Set focus to name entry
        self.name_entry.focus_set()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
    def apply_changes(self):
        new_text = self.name_entry.get()
        new_color = self.color_entry.get()
        
        if new_text:
            self.node.text = new_text
            self.node.canvas.itemconfig(self.node.label, text=new_text)
            
        if new_color:
            if new_color.startswith("#") and len(new_color) in [4, 7]:
                self.node.color = new_color
                self.node.canvas.itemconfig(self.node.oval, fill=self.node.color)
            else:
                self.node.canvas.master.update_status("Invalid HEX color. Color not changed.", "error")
                
        self.destroy()

class TreeNode:
    def __init__(self, canvas, x, y, text, parent=None, color="#ed7d31"):
        self.canvas = canvas
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.width = 80
        self.height = 40
        self.parent = parent
        self.children = []
        self.arrows = []
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
        self.canvas.master.update_status(f"Selected: {self.text}")
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
            
        # Update arrow from parent to this node
        if self.parent:
            index = self.parent.children.index(self)
            arrow = self.parent.arrows[index]
            self.canvas.coords(
                arrow,
                self.parent.x, self.parent.y + self.parent.height // 2,
                self.x, self.y - self.height // 2
            )
            
        # Update arrows to children
        for child, arrow in zip(self.children, self.arrows):
            self.canvas.coords(
                arrow,
                self.x, self.y + self.height // 2,
                child.x, child.y - child.height // 2
            )
            
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
        
    def rename_node(self, event):
        dialog = RenameDialog(self.canvas.master, self)
        
    def delete(self):
        for child in self.children:
            child.delete()
            
        for arrow in self.arrows:
            self.canvas.delete(arrow)
            
        for item in (self.oval, self.label, self.resize_handle):
            if item:
                self.canvas.delete(item)


class ColorInputDialog(ctk.CTkInputDialog):
    def __init__(self, title, text):
        super().__init__(title=title, text=text)
        
    def get_input(self):
        value = super().get_input()
        if value and (not value.startswith("#") or len(value) not in [4, 7]):
            return None
        return value


class TextInputDialog(ctk.CTkInputDialog):
    def __init__(self, title, text):
        super().__init__(title=title, text=text)


class TreeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tree Builder with HTML Export")
        self.geometry("1200x800")
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Canvas
        self.grid_rowconfigure(2, weight=0)  # Controls
        self.grid_rowconfigure(3, weight=0)  # Status
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Tree Builder", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # Theme selector in header
        theme_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        theme_frame.pack(side="right", padx=20)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Theme:")
        theme_label.pack(side="left", padx=(0, 10))
        
        theme_options = ctk.CTkOptionMenu(
            theme_frame,
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode,
            width=100
        )
        theme_options.pack(side="left")
        
        # Main frame for canvas
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas for tree drawing
        self.canvas = Canvas(self.main_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Control buttons at bottom
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Create buttons in a horizontal row
        self.add_root_btn = ctk.CTkButton(
            self.control_frame, text="Add Root", command=self.add_root_node, width=120
        )
        self.add_root_btn.pack(side="left", padx=10, pady=10)
        
        self.add_child_btn = ctk.CTkButton(
            self.control_frame, text="Add Child", command=self.add_child_node, width=120
        )
        self.add_child_btn.pack(side="left", padx=10, pady=10)
        
        self.delete_btn = ctk.CTkButton(
            self.control_frame, text="Delete Node", command=self.delete_node, 
            fg_color="#d32f2f", hover_color="#b71c1c", width=120
        )
        self.delete_btn.pack(side="left", padx=10, pady=10)
        
        self.export_btn = ctk.CTkButton(
            self.control_frame, text="Export HTML", command=self.generate_html, width=120
        )
        self.export_btn.pack(side="left", padx=10, pady=10)
        
        # Status bar at the bottom
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.grid(row=3, column=0, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Select a node to add/delete/rename")
        self.status_label.pack(side="left", padx=20, pady=5)
        
        # Initialize variables
        self.selected_node = None
        self.drag_start = (0, 0)
        self.root_nodes = []
        
        # Create initial root node
        self.add_root_node()
        
        # Update button states
        self.update_buttons()
        
    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
    
    def update_status(self, message, level="info"):
        self.status_label.configure(text=message)
        
        # Change text color based on message level
        if level == "error":
            self.status_label.configure(text_color="red")
        elif level == "success":
            self.status_label.configure(text_color="green")
        else:
            self.status_label.configure(text_color=("gray10", "gray90"))
    
    def update_buttons(self):
        if self.selected_node:
            self.add_child_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
        else:
            self.add_child_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
    
    def add_root_node(self):
        dialog = TextInputDialog(title="New Root", text="Enter root node name:")
        name = dialog.get_input()
        
        if not name:
            name = f"Root {len(self.root_nodes) + 1}"
            
        color_dialog = ColorInputDialog(title="Node Color", text="Enter HEX color (e.g. #ed7d31):")
        color_code = color_dialog.get_input()
        
        if not color_code:
            self.update_status("Invalid or no HEX color. Using default.", "info")
            color_code = "#ed7d31"
            
        x = 100 + len(self.root_nodes) * 250
        y = 100
        root_node = TreeNode(self.canvas, x, y, name, color=color_code)
        self.root_nodes.append(root_node)
        self.selected_node = root_node
        self.update_status(f"Created new root node: {name}", "success")
        self.update_buttons()
    
    def add_child_node(self):
        if not self.selected_node:
            self.update_status("Please select a node first", "error")
            return
            
        dialog = TextInputDialog(title="New Node", text="Enter name for child node:")
        name = dialog.get_input()
        
        if not name:
            return
            
        color_dialog = ColorInputDialog(title="Node Color", text="Enter HEX color (e.g. #ed7d31):")
        color_code = color_dialog.get_input()
        
        if not color_code:
            self.update_status("Invalid or no HEX color. Using default.", "info")
            color_code = "#ed7d31"
            
        x = self.selected_node.x + len(self.selected_node.children) * 150 - 75
        y = self.selected_node.y + 100
        
        child_node = TreeNode(self.canvas, x, y, name, parent=self.selected_node, color=color_code)
        arrow = self.canvas.create_line(
            self.selected_node.x, self.selected_node.y + self.selected_node.height // 2,
            x, y - child_node.height // 2,
            arrow=tk.LAST, fill="gray", width=2
        )
        self.selected_node.children.append(child_node)
        self.selected_node.arrows.append(arrow)
        child_node.on_click(None)
        self.update_status(f"Added child node: {name}", "success")
    
    def delete_node(self):
        if not self.selected_node:
            self.update_status("Please select a node first", "error")
            return
            
        node_text = self.selected_node.text
            
        if self.selected_node in self.root_nodes:
            self.root_nodes.remove(self.selected_node)
            
        if self.selected_node.parent:
            parent = self.selected_node.parent
            if self.selected_node in parent.children:
                index = parent.children.index(self.selected_node)
                del parent.children[index]
                self.canvas.delete(parent.arrows[index])
                del parent.arrows[index]
                
        self.update_status(f"Deleted: {node_text}", "info")
        self.selected_node.delete()
        self.selected_node = None
        self.update_buttons()
    
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
            for child in node.children:
                add_node_div(child)
                
        def add_arrow_lines(node):
            for child in node.children:
                lines.append(self._arrow_svg(node, child))
                add_arrow_lines(child)
                
        for root in self.root_nodes:
            add_node_div(root)
            add_arrow_lines(root)
            
        html += "".join(lines)
        html += "</div></body></html>"
        
        # Create popup with modern UI
        popup = ctk.CTkToplevel(self)
        popup.title("Generated HTML")
        popup.geometry("800x600")
        
        # Create frame for content
        content_frame = ctk.CTkFrame(popup)
        content_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame, 
            text="Generated HTML", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Text display frame
        text_frame = ctk.CTkFrame(content_frame)
        text_frame.pack(fill="both", expand=True)
        
        # Since CTkTextbox doesn't have syntax highlighting, we use standard Text widget
        text_widget = tk.Text(text_frame, wrap="none", bg="#1e1e1e", fg="#f0f0f0", insertbackground="white")
        text_widget.insert("1.0", html)
        text_widget.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Scrollbars
        y_scrollbar = ctk.CTkScrollbar(text_frame, command=text_widget.yview)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ctk.CTkScrollbar(content_frame, orientation="horizontal", command=text_widget.xview)
        x_scrollbar.pack(side="bottom", fill="x")
        
        text_widget.config(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Button frame
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Copy button
        def copy_to_clipboard():
            popup.clipboard_clear()
            popup.clipboard_append(html)
            self.update_status("HTML copied to clipboard", "success")
            
        copy_button = ctk.CTkButton(button_frame, text="Copy to Clipboard", command=copy_to_clipboard)
        copy_button.pack(side="left", padx=10)
        
        # Close button
        close_button = ctk.CTkButton(button_frame, text="Close", command=popup.destroy, fg_color="gray")
        close_button.pack(side="left", padx=10)
        
        self.update_status("Generated HTML successfully", "success")
    
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