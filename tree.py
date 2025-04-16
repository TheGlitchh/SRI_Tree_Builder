import tkinter as tk
import customtkinter as ctk
from tkinter import simpledialog
import pyperclip
import webview
from PIL import ImageGrab, ImageTk
import pyautogui
import os


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def center_window(window, parent=None):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()

    if parent:
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    else:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

    window.geometry(f"+{x}+{y}")
class RenameDialog(ctk.CTkToplevel):
    def __init__(self, parent, node):
        super().__init__(parent)
        self.node = node
        self.title("Rename and Change Color")
        self.geometry("400x250")
        center_window(self, parent)

        self.name_label = ctk.CTkLabel(self, text="Enter new name:")
        self.name_label.pack(pady=5)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.insert(0, self.node.text)
        self.name_entry.pack(pady=5)
        self.attributes("-topmost", True)

        self.color_label = ctk.CTkLabel(self, text="Enter new HEX color (e.g. #ed7d31):")
        self.color_label.pack(pady=5)
        self.color_entry = ctk.CTkEntry(self)
        self.color_entry.insert(0, self.node.color)
        self.color_entry.pack(pady=5)
        
        self.pick_color_button = ctk.CTkButton(self, text="Pick Color from Screen", command=self.pick_color_from_screen)
        self.pick_color_button.pack(pady=5)

        self.submit_button = ctk.CTkButton(self, text="Apply", command=self.apply_changes)
        self.submit_button.pack(pady=10)
        
    def pick_color_from_screen(self):
        # Hide the dialog so it doesn't appear in the screenshot
        self.withdraw()
        self.after(300, self.open_color_picker_overlay)

    def open_color_picker_overlay(self):
        # Take screenshot
        screenshot = ImageGrab.grab()
        self.screenshot = screenshot  # Save for color picking

        # Create fullscreen overlay window
        self.overlay = tk.Toplevel()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-topmost", True)
        self.overlay.config(cursor="crosshair")
        self.overlay.bind("<Button-1>", self.get_color_from_click)

        # Show screenshot as background
        self.tk_img = ImageTk.PhotoImage(screenshot)
        label = tk.Label(self.overlay, image=self.tk_img)
        label.pack()

    def get_color_from_click(self, event):
        x, y = event.x, event.y
        rgb = self.screenshot.getpixel((x, y))
        hex_color = '#%02x%02x%02x' % rgb

        # Insert the color into the entry box
        self.color_entry.delete(0, "end")
        self.color_entry.insert(0, hex_color)

        # Destroy overlay and show main dialog again
        self.overlay.destroy()
        self.deiconify()
            
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
                self.node.canvas.master.status_label.configure(text="Invalid HEX color. Color not changed.")

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
        self.canvas.master.status_label.configure(text=f"Selected: {self.text}")
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

        if self.parent:
            index = self.parent.children.index(self)
            arrow = self.parent.arrows[index]
            self.canvas.coords(
                arrow,
                self.parent.x, self.parent.y + self.parent.height // 2,
                self.x, self.y - self.height // 2
            )

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

class TreeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tree Builder with HTML Export")
        self.geometry("1200x600")
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        control_frame = ctk.CTkFrame(self)
        control_frame.pack()

        ctk.CTkButton(control_frame, text="Add Root", command=self.add_root_node).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(control_frame, text="Add Child", command=self.add_child_node).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(control_frame, text="Delete Node", command=self.delete_node).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(control_frame, text="Export HTML", command=self.generate_html).pack(side=tk.LEFT, padx=5)

        self.status_label = ctk.CTkLabel(control_frame, text="Select a node to add/delete/rename", text_color="blue")
        self.status_label.pack(pady=5)

        self.selected_node = None
        self.drag_start = (0, 0)
        self.root_nodes = []
        self.add_root_node()

    def update_buttons(self):
        pass

    def add_root_node(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Root Node")
        popup.geometry("400x300")
        popup.attributes("-topmost", True)
        center_window(popup)
        frame = ctk.CTkFrame(popup)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        label_name = ctk.CTkLabel(frame, text="Enter root node name:")
        label_name.pack(pady=5)
        entry_name = ctk.CTkEntry(frame)
        entry_name.pack(pady=5)
        entry_name.insert(0, f"Root {len(self.root_nodes) + 1}")

        label_color = ctk.CTkLabel(frame, text="Enter HEX color (e.g. #ed7d31):")
        label_color.pack(pady=5)
        entry_color = ctk.CTkEntry(frame)
        entry_color.insert(0, "#ed7d31")
        entry_color.pack(pady=5)

        def submit():
            name = entry_name.get()
            color = entry_color.get()
            if not color.startswith("#") or len(color) not in [4, 7]:
                self.status_label.configure(text="Invalid HEX color. Using default.")
                color = "#ed7d31"
            x = 100 + len(self.root_nodes) * 250
            y = 50
            node = TreeNode(self.canvas, x, y, name, color=color)
            self.root_nodes.append(node)
            self.selected_node = node
            popup.destroy()

        submit_btn = ctk.CTkButton(frame, text="Create Root Node", command=submit)
        submit_btn.pack(pady=10)

    def add_child_node(self):
        if not self.selected_node:
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Add Child Node")
        popup.geometry("400x300")
        popup.attributes("-topmost", True)
        center_window(popup)
        frame = ctk.CTkFrame(popup)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        label_name = ctk.CTkLabel(frame, text="Enter child node name:")
        label_name.pack(pady=5)
        entry_name = ctk.CTkEntry(frame)
        entry_name.pack(pady=5)

        label_color = ctk.CTkLabel(frame, text="Enter HEX color (e.g. #ed7d31):")
        label_color.pack(pady=5)
        entry_color = ctk.CTkEntry(frame)
        entry_color.insert(0, "#ed7d31")
        entry_color.pack(pady=5)

        def submit():
            name = entry_name.get()
            color = entry_color.get()
            if not name:
                return
            if not color.startswith("#") or len(color) not in [4, 7]:
                self.status_label.configure(text="Invalid HEX color. Using default.")
                color = "#ed7d31"

            parent = self.selected_node
            x = parent.x + len(parent.children) * 150 - 75
            y = parent.y + 100

            child_node = TreeNode(self.canvas, x, y, name, parent=parent, color=color)
            arrow = self.canvas.create_line(
                parent.x, parent.y + parent.height // 2,
                x, y - child_node.height // 2,
                arrow=tk.LAST, fill="gray", width=2
            )
            parent.children.append(child_node)
            parent.arrows.append(arrow)
            popup.destroy()
            child_node.on_click(None)
            

        submit_btn = ctk.CTkButton(frame, text="Create Child Node", command=submit)
        submit_btn.pack(pady=10)

    def delete_node(self):
        if not self.selected_node:
            return
        if self.selected_node in self.root_nodes:
            self.root_nodes.remove(self.selected_node)
        if self.selected_node.parent:
            parent = self.selected_node.parent
            if self.selected_node in parent.children:
                index = parent.children.index(self.selected_node)
                del parent.children[index]
                self.canvas.delete(parent.arrows[index])
                del parent.arrows[index]
        self.status_label.configure(text=f"Deleted: {self.selected_node.text}")
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
        current_path = os.getcwd()
        html_file_path = os.path.join(current_path, "tree_preview.html")

        with open("tree_preview.html", "w") as f:
            f.write(html)
        webview.create_window("HTML Preview", html_file_path, width=800, height=600)
        webview.start()
        def copy_html():
            self.copy_to_clipboard(html)
            
        popup = ctk.CTkToplevel(self)
        popup.title("Generated HTML")
        popup.geometry("400x300")
        popup.attributes("-topmost", True)
        copy_button = ctk.CTkButton(popup, text="Copy HTML to Clipboard", command=copy_html)
        copy_button.pack(expand=True, pady=20, padx=10)
        
    def copy_to_clipboard(self, html_content):
   
        self.clipboard_clear()  # Clear any existing clipboard content
        self.clipboard_append(html_content)  # Append the new content to the clipboard
        self.update()  # Update the window after copying

        # Optional: Show a confirmation message (e.g., in status bar or popup)
        self.status_label.config(text="HTML code copied to clipboard!", fg="green")
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
