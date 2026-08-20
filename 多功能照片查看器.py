import tkinter as tk
import os
import sys
import json
import ctypes
import shutil
import webbrowser
import urllib.request
import urllib.error
from ctypes import wintypes
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD


def main():
	root = TkinterDnD.Tk()
	root.title("DC照片查看器")
	root.geometry("1000x700")
	root.minsize(600, 400)
	image_paths = []
	current_index = -1
	zoom_percent = 100
	min_zoom = 50
	max_zoom = 250
	max_tabs = 20
	max_address_length = 32768
	max_render_pixels = 16000000
	image_cache = {}
	thumbnail_cache = {}
	folder_thumbnail_cache = {}
	recent_paths = []
	recent_item_ids = []
	zoom_job = None
	current_folder = ""
	current_folder_images = []
	show_drives = True
	show_folders = True
	show_onedrive = False
	show_icloud = False
	cloud_settings_unlocked = False
	cloud_onedrive_preference = False
	cloud_icloud_preference = False
	startup_folder = ""
	remember_recent = True
	close_all_action = "主页"
	warn_before_close_all = True
	fullscreen_mode = False
	maximized_mode = True
	show_startup_tip = True
	left_sidebar_visible = True
	right_sidebar_visible = False
	favorites_visible = False
	favorite_paths = []
	cloud_setting_controls = []
	cloud_setting_vars = []
	slideshow_job = None
	slideshow_running = False
	file_clipboard_paths = []
	file_clipboard_mode = "copy"
	canvas_image = None
	canvas_image_id = None
	drag_start = None
	zoom_out_button = None
	zoom_in_button = None
	previous_button = None
	next_button = None
	open_folder_button = None
	zoom_scale = None
	zoom_entry = None
	settings_button = None
	home_button = None
	close_tab_button = None
	close_all_tabs_button = None
	close_selected_tab_button = None
	clear_recent_button = None
	favorite_button = None
	slideshow_button = None
	left_sidebar_button = None
	right_sidebar_button = None
	favorites_button = None
	settings_window = None
	tab_notebook = None
	home_tab = None
	tab_paths = {}
	tab_frames = {}
	folder_icon_cache = {}
	navigation_icon_cache = {}
	cloud_icon_cache = {}
	base_dir = os.path.dirname(os.path.abspath(__file__))
	icon_root = os.path.join(base_dir, "pit")
	default_folder_icon_path = os.path.join(icon_root, "imageres_3.ico")
	default_drive_icon_path = os.path.join(icon_root, "imageres_35.ico")
	system_drive_icon_path = os.path.join(icon_root, "imageres_36.ico")
	folder_icon_path = default_folder_icon_path
	drive_icon_path = default_drive_icon_path
	icon_paths = {
		"folder": folder_icon_path,
		"system_drive": system_drive_icon_path,
		"drive": drive_icon_path,
	}
	settings = {}
	config_path = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "照片查看器", "settings.json")
	try:
		with open(config_path, "r", encoding="utf-8") as config_file:
			settings = json.load(config_file)
		show_drives = bool(settings.get("show_drives", show_drives))
		show_folders = bool(settings.get("show_folders", show_folders))
		cloud_onedrive_preference = bool(settings.get("show_onedrive", cloud_onedrive_preference))
		cloud_icloud_preference = bool(settings.get("show_icloud", cloud_icloud_preference))
		startup_folder = settings.get("startup_folder", startup_folder)
		remember_recent = bool(settings.get("remember_recent", remember_recent))
		close_all_action = settings.get("close_all_action", close_all_action)
		warn_before_close_all = bool(settings.get("warn_before_close_all", warn_before_close_all))
		fullscreen_mode = bool(settings.get("fullscreen_mode", fullscreen_mode))
		maximized_mode = bool(settings.get("maximized_mode", maximized_mode))
		show_startup_tip = bool(settings.get("show_startup_tip", show_startup_tip))
		left_sidebar_visible = bool(settings.get("left_sidebar_visible", left_sidebar_visible))
		right_sidebar_visible = bool(settings.get("right_sidebar_visible", right_sidebar_visible))
		favorites_visible = bool(settings.get("favorites_visible", favorites_visible))
		favorite_paths = [path for path in settings.get("favorite_paths", []) if os.path.isfile(path)]
		stored_folder_icon_path = settings.get("folder_icon_path", folder_icon_path)
		stored_drive_icon_path = settings.get("drive_icon_path", drive_icon_path)
		if not os.path.isabs(stored_folder_icon_path):
			stored_folder_icon_path = os.path.join(base_dir, stored_folder_icon_path)
		if not os.path.isabs(stored_drive_icon_path):
			stored_drive_icon_path = os.path.join(base_dir, stored_drive_icon_path)
		if not os.path.isfile(stored_folder_icon_path):
			stored_folder_icon_path = os.path.join(icon_root, os.path.basename(stored_folder_icon_path))
		if not os.path.isfile(stored_drive_icon_path):
			stored_drive_icon_path = os.path.join(icon_root, os.path.basename(stored_drive_icon_path))
		if os.path.basename(stored_folder_icon_path) == os.path.basename(default_folder_icon_path):
			stored_folder_icon_path = default_folder_icon_path
		if os.path.basename(stored_drive_icon_path) == os.path.basename(default_drive_icon_path):
			stored_drive_icon_path = default_drive_icon_path
		folder_icon_path = stored_folder_icon_path if os.path.isfile(stored_folder_icon_path) else default_folder_icon_path
		drive_icon_path = stored_drive_icon_path if os.path.isfile(stored_drive_icon_path) else default_drive_icon_path
		icon_paths["folder"] = folder_icon_path
		icon_paths["drive"] = drive_icon_path
	except (OSError, TypeError, ValueError, json.JSONDecodeError):
		pass
	system_drive = os.path.splitdrive(os.environ.get("SystemRoot", "C:\\"))[0].upper()
	onedrive_root = next(
		(os.environ.get(name) for name in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer") if os.environ.get(name)),
		"",
	)

	def is_onedrive_path(path):
		if not onedrive_root:
			return False
		try:
			return os.path.commonpath((os.path.abspath(path), os.path.abspath(onedrive_root))) == os.path.abspath(onedrive_root)
		except ValueError:
			return False

	def unlock_cloud_settings(event=None):
		nonlocal cloud_settings_unlocked, show_onedrive, show_icloud
		if cloud_settings_unlocked:
			return "break"
		cloud_settings_unlocked = True
		show_onedrive = cloud_onedrive_preference
		show_icloud = cloud_icloud_preference
		for control, variable, value in zip(
			cloud_setting_controls,
			cloud_setting_vars,
			(show_onedrive, show_icloud),
		):
			variable.set(value)
			control.configure(state=tk.NORMAL)
		load_drives()
		return "break"

	toolbar = tk.Frame(root)
	toolbar.pack(fill="x", padx=12, pady=(12, 0))
	address_row = tk.Frame(root)
	address_row.pack(fill="x", padx=12, pady=(8, 0))
	tk.Label(address_row, text="地址").pack(side="left")
	address_entry = ttk.Entry(address_row)
	address_entry.pack(side="left", fill="x", expand=True, padx=(8, 6))
	address_entry.configure(
		validate="key",
		validatecommand=(root.register(lambda value: len(value) <= max_address_length), "%P"),
	)

	tab_bar = tk.Frame(root)
	tab_bar.pack(fill="x", padx=12, pady=(8, 0))
	tab_notebook = ttk.Notebook(tab_bar, height=30)
	tab_notebook.pack(side="left", fill="x", expand=True)
	home_tab = tk.Frame(tab_notebook)
	tab_notebook.add(home_tab, text="主页")
	tab_frames["home"] = home_tab

	content = tk.Frame(root)
	content.pack(fill="both", expand=True, padx=12, pady=(8, 12))

	list_frame = tk.Frame(content, width=260)
	list_frame.pack(side="left", fill="y", padx=(0, 12))
	list_frame.pack_propagate(False)
	browser_header = tk.Frame(list_frame)
	browser_header.pack(fill="x")
	tk.Label(browser_header, text="文件浏览器").pack(side="left")
	tree_style = ttk.Style(root)
	tree_style.configure("Explorer.Treeview", rowheight=56)
	explorer = ttk.Treeview(list_frame, show="tree", style="Explorer.Treeview")
	explorer_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=explorer.yview)
	explorer.configure(yscrollcommand=explorer_scrollbar.set)
	explorer_scrollbar.pack(side="right", fill="y", pady=(6, 0))
	explorer.pack(side="left", fill="both", expand=True, pady=(6, 0))

	viewer = tk.Frame(content)
	viewer.pack(side="left", fill="both", expand=True)
	path_label = tk.Label(viewer, text="请选择图片", anchor="w", relief="sunken")
	path_label.pack(fill="x", pady=(0, 6))
	image_area = tk.Frame(viewer)
	image_area.pack(fill="both", expand=True)
	image_canvas = tk.Canvas(
		image_area,
		background="#202020",
		highlightthickness=0,
	)
	image_horizontal_scrollbar = ttk.Scrollbar(image_area, orient="horizontal", command=image_canvas.xview)
	image_vertical_scrollbar = ttk.Scrollbar(image_area, orient="vertical", command=image_canvas.yview)
	image_canvas.configure(
		xscrollcommand=image_horizontal_scrollbar.set,
		yscrollcommand=image_vertical_scrollbar.set,
	)
	image_vertical_scrollbar.pack(side="right", fill="y")
	image_horizontal_scrollbar.pack(side="bottom", fill="x")
	image_canvas.pack(side="left", fill="both", expand=True)
	placeholder_id = image_canvas.create_text(
		500,
		300,
		text="请在左侧打开图片，或将图片拖拽到此处",
		fill="white",
		font=("Microsoft YaHei UI", 16),
		anchor="center",
		width=700,
		tags="placeholder",
	)
	image_label = image_canvas
	navigation_bar = tk.Frame(viewer)
	navigation_bar.pack(fill="x", pady=(6, 0))

	def reposition_placeholder(event=None):
		canvas_width = max(240, image_canvas.winfo_width() - 40)
		canvas_height = max(160, image_canvas.winfo_height() // 2)
		image_canvas.coords(placeholder_id, image_canvas.winfo_width() / 2, canvas_height)
		image_canvas.itemconfigure(placeholder_id, width=canvas_width)

	image_canvas.bind("<Configure>", reposition_placeholder)

	recent_frame = tk.Frame(content, width=230)
	recent_frame.pack(side="right", fill="y", padx=(12, 0))
	recent_frame.pack_propagate(False)
	recent_header = tk.Frame(recent_frame)
	recent_header.pack(fill="x")
	tk.Label(recent_header, text="最近打开").pack(side="left")
	recent_list = ttk.Treeview(recent_frame, show="tree", style="Explorer.Treeview")
	recent_scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=recent_list.yview)
	recent_list.configure(yscrollcommand=recent_scrollbar.set)
	recent_scrollbar.pack(side="right", fill="y", pady=(6, 0))
	recent_list.pack(side="left", fill="both", expand=True, pady=(6, 0))

	favorites_frame = tk.Frame(root)
	favorites_frame.pack(fill="x", padx=12, pady=(0, 8))
	favorites_header = tk.Frame(favorites_frame)
	favorites_header.pack(fill="x")
	tk.Label(favorites_header, text="收藏图片").pack(side="left")
	favorites_list = ttk.Treeview(favorites_frame, show="tree", height=2, style="Explorer.Treeview")
	favorites_list.pack(side="left", fill="x", expand=True)

	class Tooltip:
		def __init__(self, widget, text):
			self.widget = widget
			self.text = text
			self.tip = None
			widget.bind("<Enter>", self.show, add="+")
			widget.bind("<Leave>", self.hide, add="+")

		def show(self, event=None):
			if self.tip:
				return
			self.tip = tk.Toplevel(self.widget)
			self.tip.wm_overrideredirect(True)
			self.tip.wm_geometry(f"+{self.widget.winfo_rootx() + 12}+{self.widget.winfo_rooty() + self.widget.winfo_height() + 4}")
			tk.Label(self.tip, text=self.text, relief="solid", borderwidth=1, background="#ffffe0").pack()

		def hide(self, event=None):
			if self.tip:
				self.tip.destroy()
				self.tip = None

	def open_address():
		address = address_entry.get().strip().strip('"')
		if len(address) > max_address_length:
			messagebox.showwarning("地址过长", f"地址不能超过 {max_address_length} 个字符。")
			return
		if not address:
			return
		if os.path.isdir(address):
			ensure_folder_tab(address)
			load_folder(address)
			return
		if os.path.isfile(address):
			add_images([address])
			if address in image_paths:
				show_image(image_paths.index(address))
			return
		messagebox.showwarning("地址无效", f"找不到文件或文件夹：\n{address}")

	def ensure_image_tab(photo_path, force_new=False):
		photo_path = os.path.abspath(photo_path)
		if not force_new:
			return
		if len(tab_notebook.tabs()) >= max_tabs:
			messagebox.showwarning("标签页数量已达上限", f"最多只能创建 {max_tabs} 个标签页。")
			return
		tab_frame = tk.Frame(tab_notebook)
		tab_id = str(tab_frame)
		tab_paths[tab_id] = ("image", photo_path)
		tab_frames[tab_id] = tab_frame
		tab_notebook.add(tab_frame, text=os.path.basename(photo_path))
		tab_notebook.select(tab_id)
		update_close_tab_buttons()

	def ensure_folder_tab(folder_path, force_new=False):
		folder_path = os.path.abspath(folder_path)
		if not force_new:
			return
		if len(tab_notebook.tabs()) >= max_tabs:
			messagebox.showwarning("标签页数量已达上限", f"最多只能创建 {max_tabs} 个标签页。")
			return
		tab_frame = tk.Frame(tab_notebook)
		tab_id = str(tab_frame)
		tab_paths[tab_id] = ("folder", folder_path)
		tab_frames[tab_id] = tab_frame
		tab_notebook.add(tab_frame, text=os.path.basename(folder_path) or folder_path)
		tab_notebook.select(tab_id)
		update_close_tab_buttons()

	def select_tab_image(event=None):
		selected_tab = tab_notebook.select()
		if selected_tab == str(home_tab) or (selected_tab in tab_paths and tab_paths[selected_tab][0] == "home"):
			load_drives()
			path_label.configure(text="请选择图片")
			root.title("照片查看器")
			update_close_tab_buttons()
			return
		if selected_tab not in tab_paths:
			update_close_tab_buttons()
			return
		item_kind, item_path = tab_paths[selected_tab]
		if item_kind == "image" and item_path in image_paths:
			show_image(image_paths.index(item_path))
		elif item_kind == "folder":
			load_folder(item_path)
		update_close_tab_buttons()

	def update_close_tab_buttons():
		if close_tab_button is None or close_all_tabs_button is None or close_selected_tab_button is None:
			return
		state = tk.NORMAL if len(tab_notebook.tabs()) > 1 else tk.DISABLED
		close_tab_button.configure(state=state)
		close_all_tabs_button.configure(state=state)
		close_selected_tab_button.configure(state=state)

	def rename_current_tab():
		selected_tab = tab_notebook.select()
		if selected_tab == str(home_tab) or selected_tab not in tab_paths:
			return
		current_name = tab_notebook.tab(selected_tab, "text")
		new_name = simpledialog.askstring("重命名标签页", "请输入新的标签页名称：", initialvalue=current_name, parent=root)
		if new_name and new_name.strip():
			tab_notebook.tab(selected_tab, text=new_name.strip())

	def go_home():
		if tab_notebook.select() == str(home_tab) and not current_folder:
			return
		tab_notebook.select(home_tab)
		load_drives()
		path_label.configure(text="请选择图片")
		root.title("照片查看器")

	def close_tab(tab_id=None):
		tab_id = tab_id or tab_notebook.select()
		if tab_id not in tab_paths:
			return
		tab_ids = list(tab_notebook.tabs())
		closed_index = tab_ids.index(tab_id)
		tab_notebook.forget(tab_id)
		tab_paths.pop(tab_id, None)
		tab_frames.pop(tab_id, None)
		remaining_tabs = list(tab_notebook.tabs())
		if remaining_tabs:
			tab_notebook.select(remaining_tabs[min(closed_index, len(remaining_tabs) - 1)])
		else:
			tab_notebook.select(home_tab)
		update_close_tab_buttons()

	def close_all_tabs():
		non_home_tabs = [tab_id for tab_id in tab_notebook.tabs() if tab_id in tab_paths]
		if not non_home_tabs:
			go_home()
			return
		if warn_before_close_all and len(non_home_tabs) > 1:
			confirmed = messagebox.askyesno(
				"关闭多个标签页",
				f"确定要关闭全部 {len(non_home_tabs)} 个标签页吗？",
			)
			if not confirmed:
				return
		for tab_id in non_home_tabs:
			tab_notebook.forget(tab_id)
			tab_paths.pop(tab_id, None)
			tab_frames.pop(tab_id, None)
		if close_all_action == "退出":
			save_settings()
			root.destroy()
		else:
			tab_notebook.select(home_tab)
			go_home()
		update_close_tab_buttons()

	def add_home_tab():
		if len(tab_notebook.tabs()) >= max_tabs:
			messagebox.showwarning("标签页数量已达上限", f"最多只能创建 {max_tabs} 个标签页。")
			return
		tab_frame = tk.Frame(tab_notebook)
		tab_id = str(tab_frame)
		tab_paths[tab_id] = ("home", "")
		tab_frames[tab_id] = tab_frame
		tab_notebook.add(tab_frame, text="主页")
		tab_notebook.select(tab_id)
		load_drives()
		update_close_tab_buttons()

	def show_image(index, force_new_tab=False):
		nonlocal current_index, canvas_image, canvas_image_id
		if not 0 <= index < len(image_paths):
			return
		try:
			if image_paths[index] not in image_cache:
				with Image.open(image_paths[index]) as source_image:
					image_cache[image_paths[index]] = source_image.copy()
			image = image_cache[image_paths[index]]
		except (OSError, SyntaxError, ValueError) as error:
			messagebox.showerror(
				"无法打开图片",
				f"无法打开文件：\n{image_paths[index]}\n\n原因：{error}",
			)
			return

		current_index = index
		ensure_image_tab(image_paths[index], force_new=force_new_tab)
		zoom_factor = zoom_percent / 100
		width = max(1, int(image.width * zoom_factor))
		height = max(1, int(image.height * zoom_factor))
		render_scale = min(1.0, (max_render_pixels / (width * height)) ** 0.5)
		width = max(1, int(width * render_scale))
		height = max(1, int(height * render_scale))
		image = image.resize((width, height), Image.Resampling.BILINEAR)
		canvas_image = ImageTk.PhotoImage(image)
		image_canvas.delete("placeholder")
		if canvas_image_id is not None:
			image_canvas.delete(canvas_image_id)
		canvas_image_id = image_canvas.create_image(0, 0, image=canvas_image, anchor="nw")
		image_canvas.configure(scrollregion=(0, 0, width, height))
		path_label.configure(text=image_paths[index])
		address_entry.delete(0, tk.END)
		address_entry.insert(0, image_paths[index])
		selected_tab = tab_notebook.select()
		if selected_tab in tab_paths and tab_paths[selected_tab] == ("image", os.path.abspath(image_paths[index])):
			tab_notebook.tab(selected_tab, text=os.path.basename(image_paths[index]))
		select_explorer_image(image_paths[index])
		root.title(f"{os.path.basename(image_paths[index])} - 图片查看器")
		update_favorite_button()
		update_control_states()

	def add_images(photo_paths):
		invalid_paths = []
		for photo_path in photo_paths:
			if photo_path in image_paths:
				continue
			try:
				with Image.open(photo_path) as image:
					image.verify()
			except (OSError, SyntaxError, ValueError):
				invalid_paths.append(photo_path)
				continue
			image_paths.append(photo_path)
			ensure_explorer_image(photo_path)
			ensure_recent_image(photo_path)

		if invalid_paths:
			messagebox.showwarning(
				"文件无法打开",
				"以下文件不是有效图片，已跳过：\n\n" + "\n".join(invalid_paths),
			)
		if current_index == -1 and image_paths:
			show_image(0)

	def select_image():
		photo_paths = filedialog.askopenfilenames(
			title="选择照片",
			filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"), ("所有文件", "*.*")],
		)
		add_images(photo_paths)

	def select_folder():
		folder_path = filedialog.askdirectory(title="选择图片文件夹")
		if not folder_path:
			return
		ensure_folder_tab(folder_path)
		load_folder(folder_path)
		image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
		photo_paths = [
			entry.path
			for entry in os.scandir(folder_path)
			if entry.is_file() and os.path.splitext(entry.name)[1].lower() in image_extensions
		]
		add_images(sorted(photo_paths))

	def load_folder(folder_path):
		nonlocal current_folder, current_folder_images
		folder_path = os.path.abspath(folder_path)
		try:
			entries = sorted(os.scandir(folder_path), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
		except OSError as error:
			messagebox.showerror("无法打开文件夹", f"无法打开文件夹：\n{folder_path}\n\n原因：{error}")
			return
		current_folder = folder_path
		selected_tab = tab_notebook.select()
		if selected_tab in tab_paths and tab_paths[selected_tab] == ("folder", current_folder):
			tab_notebook.tab(selected_tab, text=os.path.basename(current_folder) or current_folder)
		address_entry.delete(0, tk.END)
		address_entry.insert(0, current_folder)
		current_folder_images = []
		explorer.delete(*explorer.get_children())
		parent = os.path.dirname(current_folder)
		if parent and parent != current_folder:
			explorer.insert("", "end", text="..", values=(parent, "folder"))
		else:
			explorer.insert("", "end", text="此电脑", values=("", "drives"))
		for entry in entries:
			if entry.is_dir() and not show_folders:
				continue
			if entry.is_dir() or os.path.splitext(entry.name)[1].lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}:
				kind = "folder" if entry.is_dir() else "image"
				if kind == "image":
					current_folder_images.append(entry.path)
				if kind == "folder" and is_onedrive_path(entry.path):
					thumbnail = get_folder_icon("folder")
				else:
					thumbnail = get_file_icon(entry.path, "folder") if kind == "folder" else get_thumbnail(entry.path)
				item_id = explorer.insert("", "end", text=entry.name, image=thumbnail, values=(entry.path, kind))
		update_next_button()
		if explorer.get_children():
			first_item = explorer.get_children()[0]
			explorer.selection_set(first_item)
			explorer.focus(first_item)
		explorer.focus_set()

	def get_folder_icon(icon_kind):
		if icon_kind in folder_icon_cache:
			return folder_icon_cache[icon_kind]
		try:
			with Image.open(icon_paths[icon_kind]) as source_icon:
				icon_image = source_icon.convert("RGBA")
				icon_image.thumbnail((48, 48), Image.Resampling.LANCZOS)
			folder_icon_cache[icon_kind] = ImageTk.PhotoImage(icon_image)
		except (OSError, SyntaxError, ValueError):
			return ""
		return folder_icon_cache[icon_kind]

	def get_file_icon(file_path, fallback_kind):
		cache_key = f"system:{os.path.abspath(file_path)}"
		if cache_key in folder_icon_cache:
			return folder_icon_cache[cache_key]
		try:
			shell32 = ctypes.windll.shell32
			user32 = ctypes.windll.user32
			gdi32 = ctypes.windll.gdi32
			shell32.SHGetFileInfoW.argtypes = [
				wintypes.LPCWSTR,
				wintypes.DWORD,
				ctypes.c_void_p,
				wintypes.UINT,
				wintypes.UINT,
			]
			shell32.SHGetFileInfoW.restype = ctypes.c_void_p
			user32.GetIconInfo.argtypes = [wintypes.HICON, ctypes.c_void_p]
			user32.GetIconInfo.restype = wintypes.BOOL
			user32.DestroyIcon.argtypes = [wintypes.HICON]
			user32.DestroyIcon.restype = wintypes.BOOL
			gdi32.GetObjectW.argtypes = [wintypes.HGDIOBJ, ctypes.c_int, ctypes.c_void_p]
			gdi32.GetObjectW.restype = ctypes.c_int
			gdi32.GetDIBits.argtypes = [
				wintypes.HDC,
				wintypes.HBITMAP,
				wintypes.UINT,
				wintypes.UINT,
				ctypes.c_void_p,
				ctypes.c_void_p,
				wintypes.UINT,
			]
			gdi32.GetDIBits.restype = ctypes.c_int
			gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
			gdi32.DeleteObject.restype = wintypes.BOOL

			class ShellFileInfo(ctypes.Structure):
				_fields_ = [
					("hIcon", wintypes.HICON),
					("iIcon", ctypes.c_int),
					("dwAttributes", wintypes.DWORD),
					("szDisplayName", wintypes.WCHAR * 260),
					("szTypeName", wintypes.WCHAR * 80),
				]

			class IconInfo(ctypes.Structure):
				_fields_ = [
					("fIcon", wintypes.BOOL),
					("xHotspot", wintypes.DWORD),
					("yHotspot", wintypes.DWORD),
					("hbmMask", wintypes.HBITMAP),
					("hbmColor", wintypes.HBITMAP),
				]

			class Bitmap(ctypes.Structure):
				_fields_ = [
					("bmType", ctypes.c_long),
					("bmWidth", ctypes.c_long),
					("bmHeight", ctypes.c_long),
					("bmWidthBytes", ctypes.c_long),
					("bmPlanes", ctypes.c_ushort),
					("bmBitsPixel", ctypes.c_ushort),
					("bmBits", ctypes.c_void_p),
				]

			file_info = ShellFileInfo()
			flags = 0x100 | 0x0
			result = shell32.SHGetFileInfoW(
				file_path,
				0,
				ctypes.byref(file_info),
				ctypes.sizeof(file_info),
				flags,
			)
			if not result or not file_info.hIcon:
				raise OSError("无法取得 Explorer 图标")

			icon_info = IconInfo()
			if not user32.GetIconInfo(file_info.hIcon, ctypes.byref(icon_info)):
				raise OSError("无法读取 Explorer 图标")
			bitmap = Bitmap()
			if not gdi32.GetObjectW(icon_info.hbmColor, ctypes.sizeof(bitmap), ctypes.byref(bitmap)):
				raise OSError("无法读取 Explorer 图像")
			width = bitmap.bmWidth
			height = bitmap.bmHeight
			bitmap_info = (ctypes.c_ubyte * (40 + 4 * 3))()
			ctypes.memset(bitmap_info, 0, ctypes.sizeof(bitmap_info))
			bitmap_header = ctypes.cast(bitmap_info, ctypes.POINTER(ctypes.c_ulong))
			bitmap_header[0] = 40
			ctypes.cast(bitmap_info, ctypes.POINTER(ctypes.c_long))[1] = width
			ctypes.cast(bitmap_info, ctypes.POINTER(ctypes.c_long))[2] = -height
			ctypes.cast(bitmap_info, ctypes.POINTER(ctypes.c_ushort))[6] = 1
			ctypes.cast(bitmap_info, ctypes.POINTER(ctypes.c_ushort))[7] = 32
			pixel_buffer = (ctypes.c_ubyte * (width * height * 4))()
			if not gdi32.GetDIBits(
				0,
				icon_info.hbmColor,
				0,
				height,
				pixel_buffer,
				bitmap_info,
				0,
			):
				raise OSError("无法转换 Explorer 图标")
			icon_image = Image.frombuffer("RGBA", (width, height), bytes(pixel_buffer), "raw", "BGRA", 0, 1)
			icon_image.thumbnail((48, 48), Image.Resampling.LANCZOS)
			folder_icon_cache[cache_key] = ImageTk.PhotoImage(icon_image)
			return folder_icon_cache[cache_key]
		except (OSError, AttributeError, TypeError, ValueError, ctypes.ArgumentError):
			return get_folder_icon(fallback_kind)
		finally:
			try:
				if 'file_info' in locals() and file_info.hIcon:
					user32.DestroyIcon(file_info.hIcon)
				if 'icon_info' in locals():
					if icon_info.hbmColor:
						gdi32.DeleteObject(icon_info.hbmColor)
					if icon_info.hbmMask:
						gdi32.DeleteObject(icon_info.hbmMask)
			except (AttributeError, OSError, ctypes.ArgumentError):
				pass

	def get_cloud_icon(cloud_kind):
		if cloud_kind in cloud_icon_cache:
			return cloud_icon_cache[cloud_kind]
		cloud_icon_paths = {
			"onedrive": (os.path.join(icon_root, "onedrive.png"), "https://www.google.com/s2/favicons?domain=onedrive.live.com&sz=64"),
			"icloud": (os.path.join(icon_root, "icloud.png"), "https://www.google.com/s2/favicons?domain=icloud.com&sz=64"),
		}
		icon_path, icon_url = cloud_icon_paths[cloud_kind]
		if not os.path.isfile(icon_path):
			return get_folder_icon("folder")
		try:
			with Image.open(icon_path) as source_icon:
				icon_image = source_icon.convert("RGBA")
				icon_image.thumbnail((48, 48), Image.Resampling.LANCZOS)
			cloud_icon_cache[cloud_kind] = ImageTk.PhotoImage(icon_image)
		except (OSError, SyntaxError, ValueError):
			return get_folder_icon("folder")
		return cloud_icon_cache[cloud_kind]

	def get_navigation_icon(icon_kind):
		if icon_kind in navigation_icon_cache:
			return navigation_icon_cache[icon_kind]
		try:
			with Image.open(os.path.join(icon_root, "icon.ico")) as source_icon:
				icon_image = source_icon.convert("RGBA")
				if icon_kind == "next":
					icon_image = icon_image.rotate(180, expand=True)
				icon_image.thumbnail((20, 20), Image.Resampling.LANCZOS)
			navigation_icon_cache[icon_kind] = ImageTk.PhotoImage(icon_image)
		except (OSError, SyntaxError, ValueError):
			return ""
		return navigation_icon_cache[icon_kind]

	def get_thumbnail(photo_path):
		if photo_path in thumbnail_cache:
			return thumbnail_cache[photo_path]
		try:
			with Image.open(photo_path) as source_image:
				thumbnail_image = source_image.copy()
			thumbnail_image.thumbnail((48, 48), Image.Resampling.BILINEAR)
			thumbnail = ImageTk.PhotoImage(thumbnail_image)
		except (OSError, SyntaxError, ValueError):
			return ""
		thumbnail_cache[photo_path] = thumbnail
		return thumbnail

	def refresh_favorites():
		favorites_list.delete(*favorites_list.get_children())
		for photo_path in favorite_paths:
			favorites_list.insert(
				"",
				"end",
				image=get_thumbnail(photo_path),
				text=os.path.basename(photo_path),
				values=(photo_path, "image"),
			)

	def open_favorite(event=None):
		selection = favorites_list.selection()
		if not selection:
			return
		photo_path = os.path.abspath(favorites_list.item(selection[0], "values")[0])
		if not os.path.isfile(photo_path):
			messagebox.showwarning("文件不存在", f"收藏的图片已不存在：\n{photo_path}")
			return
		if photo_path not in image_paths:
			image_paths.append(photo_path)
		show_image(image_paths.index(photo_path))

	def update_favorite_button():
		if favorite_button is None:
			return
		is_favorite = 0 <= current_index < len(image_paths) and image_paths[current_index] in favorite_paths
		favorite_button.configure(text="取消收藏" if is_favorite else "收藏图片")

	def toggle_favorite():
		if not 0 <= current_index < len(image_paths):
			return
		photo_path = image_paths[current_index]
		if photo_path in favorite_paths:
			favorite_paths.remove(photo_path)
		else:
			favorite_paths.append(photo_path)
		refresh_favorites()
		update_favorite_button()
		save_settings()

	def stop_slideshow():
		nonlocal slideshow_job, slideshow_running
		slideshow_running = False
		if slideshow_job is not None:
			root.after_cancel(slideshow_job)
			slideshow_job = None
		if slideshow_button is not None:
			slideshow_button.configure(text="幻灯片")

	def slideshow_tick():
		nonlocal slideshow_job
		if not slideshow_running:
			return
		show_next_image()
		slideshow_job = root.after(3000, slideshow_tick)

	def get_slideshow_images():
		current_path = image_paths[current_index] if 0 <= current_index < len(image_paths) else ""
		favorite_images = [path for path in favorite_paths if os.path.isfile(path)]
		if current_path in favorite_images and len(favorite_images) >= 2:
			return favorite_images
		folder_images = [path for path in current_folder_images if os.path.isfile(path)]
		if len(folder_images) >= 2:
			return folder_images
		return [path for path in image_paths if os.path.isfile(path)]

	def toggle_slideshow():
		nonlocal slideshow_job, slideshow_running
		if len(get_slideshow_images()) < 2:
			messagebox.showinfo("幻灯片", "至少需要两张有效图片才能播放。")
			return
		if slideshow_running:
			stop_slideshow()
			return
		slideshow_running = True
		slideshow_button.configure(text="停止幻灯片")
		slideshow_job = root.after(3000, slideshow_tick)

	def toggle_left_sidebar():
		nonlocal left_sidebar_visible
		left_sidebar_visible = not left_sidebar_visible
		refresh_content_layout()
		left_sidebar_button.configure(text="收起左栏" if left_sidebar_visible else "打开左栏")

	def toggle_right_sidebar():
		nonlocal right_sidebar_visible
		right_sidebar_visible = not right_sidebar_visible
		refresh_content_layout()
		right_sidebar_button.configure(text="收起右栏" if right_sidebar_visible else "打开右栏")

	def refresh_content_layout():
		for frame in (list_frame, viewer, recent_frame):
			frame.pack_forget()
		if left_sidebar_visible:
			list_frame.pack(side="left", fill="y", padx=(0, 12))
		viewer.pack(side="left", fill="both", expand=True)
		if right_sidebar_visible:
			recent_frame.pack(side="right", fill="y", padx=(12, 0))

	def toggle_favorites_bar():
		nonlocal favorites_visible
		favorites_visible = not favorites_visible
		if favorites_visible:
			favorites_list.pack(side="left", fill="x", expand=True, padx=(8, 0))
			favorites_button.configure(text="收起收藏栏")
		else:
			favorites_list.pack_forget()
			favorites_button.configure(text="打开收藏栏")

	def get_selected_file_paths():
		paths = []
		for item_id in explorer.selection():
			values = explorer.item(item_id, "values")
			if len(values) >= 2 and values[1] in ("folder", "image") and os.path.exists(values[0]):
				paths.append(values[0])
		return paths

	def copy_selected_files(cut=False):
		nonlocal file_clipboard_paths, file_clipboard_mode
		file_clipboard_paths = get_selected_file_paths()
		file_clipboard_mode = "cut" if cut else "copy"

	def paste_files():
		nonlocal file_clipboard_paths
		if not file_clipboard_paths:
			return
		destination = current_folder or os.path.expanduser("~")
		if not os.path.isdir(destination):
			messagebox.showwarning("无法粘贴", "请先打开一个有效文件夹。")
			return
		failed = []
		for source in file_clipboard_paths:
			try:
				target = os.path.join(destination, os.path.basename(source))
				if os.path.abspath(source) == os.path.abspath(target):
					continue
				if os.path.exists(target):
					messagebox.showwarning("无法粘贴", f"目标已存在：\n{target}")
					continue
				if file_clipboard_mode == "cut":
					shutil.move(source, target)
				elif os.path.isdir(source):
					shutil.copytree(source, target)
				else:
					shutil.copy2(source, target)
			except OSError as error:
				failed.append(f"{source}: {error}")
		if file_clipboard_mode == "cut":
			file_clipboard_paths = []
		if failed:
			messagebox.showwarning("部分文件无法粘贴", "\n".join(failed))
		load_folder(destination)

	def delete_selected_files():
		selected_paths = get_selected_file_paths()
		if not selected_paths:
			return
		if not messagebox.askyesno("删除文件", f"确定删除选中的 {len(selected_paths)} 个项目吗？"):
			return
		failed = []
		for path in selected_paths:
			try:
				if os.path.isdir(path):
					shutil.rmtree(path)
				else:
					os.remove(path)
			except OSError as error:
				failed.append(f"{path}: {error}")
		if failed:
			messagebox.showwarning("部分文件无法删除", "\n".join(failed))
		load_folder(current_folder) if current_folder else load_drives()

	def get_folder_thumbnail(folder_path):
		if folder_path in folder_thumbnail_cache:
			return folder_thumbnail_cache[folder_path]
		try:
			image_paths_in_folder = sorted(
				entry.path
				for entry in os.scandir(folder_path)
				if entry.is_file() and os.path.splitext(entry.name)[1].lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
			)
		except OSError:
			return ""
		for photo_path in image_paths_in_folder:
			thumbnail = get_thumbnail(photo_path)
			if thumbnail:
				folder_thumbnail_cache[folder_path] = thumbnail
				return thumbnail
		return ""

	def ensure_explorer_image(photo_path):
		for item_id in explorer.get_children():
			item_path, item_kind = explorer.item(item_id, "values")
			if item_kind == "image" and os.path.abspath(item_path) == os.path.abspath(photo_path):
				return
		item_id = explorer.insert(
			"",
			"end",
			text=os.path.basename(photo_path),
			image=get_thumbnail(photo_path),
			values=(photo_path, "image"),
		)
		explorer.see(item_id)

	def select_explorer_image(photo_path):
		for item_id in explorer.get_children():
			item_values = explorer.item(item_id, "values")
			if len(item_values) >= 2 and item_values[1] == "image" and os.path.abspath(item_values[0]) == os.path.abspath(photo_path):
				explorer.selection_set(item_id)
				explorer.focus(item_id)
				explorer.see(item_id)
				return

	def ensure_recent_image(photo_path):
		if not remember_recent:
			update_recent_clear_button()
			return
		if photo_path in recent_paths:
			recent_list.selection_set(recent_item_ids[recent_paths.index(photo_path)])
			return
		recent_paths.append(photo_path)
		recent_item_ids.append(
			recent_list.insert(
				"",
				"end",
				image=get_thumbnail(photo_path),
				text=os.path.basename(photo_path),
				values=(photo_path, "image"),
			)
		)
		recent_list.selection_set(recent_item_ids[-1])
		update_recent_clear_button()

	def update_recent_clear_button():
		if clear_recent_button is not None:
			state = tk.NORMAL if remember_recent and recent_paths else tk.DISABLED
			clear_recent_button.configure(state=state)

	def load_recent_images():
		if not remember_recent:
			return
		for recent_path in settings.get("recent_paths", []):
			if not os.path.isfile(recent_path) or recent_path in recent_paths:
				continue
			recent_paths.append(recent_path)
			recent_item_ids.append(
				recent_list.insert(
					"",
					"end",
					image=get_thumbnail(recent_path),
					text=os.path.basename(recent_path),
					values=(recent_path, "image"),
				)
			)
		update_recent_clear_button()

	def save_settings():
		try:
			os.makedirs(os.path.dirname(config_path), exist_ok=True)
			with open(config_path, "w", encoding="utf-8") as config_file:
				json.dump(
					{
						"show_drives": show_drives,
						"show_folders": show_folders,
						"show_onedrive": cloud_onedrive_preference,
						"show_icloud": cloud_icloud_preference,
						"startup_folder": startup_folder,
						"remember_recent": remember_recent,
						"close_all_action": close_all_action,
						"warn_before_close_all": warn_before_close_all,
						"fullscreen_mode": fullscreen_mode,
						"maximized_mode": maximized_mode,
						"show_startup_tip": show_startup_tip,
						"folder_icon_path": os.path.relpath(folder_icon_path, base_dir),
						"drive_icon_path": os.path.relpath(drive_icon_path, base_dir),
						"recent_paths": recent_paths if remember_recent else [],
						"favorite_paths": favorite_paths,
						"left_sidebar_visible": left_sidebar_visible,
						"right_sidebar_visible": right_sidebar_visible,
						"favorites_visible": favorites_visible,
					},
					config_file,
					ensure_ascii=False,
					indent=2,
				)
		except OSError:
			pass

	def open_recent_image(event):
		item_id = recent_list.identify_row(event.y)
		if item_id:
			recent_list.selection_set(item_id)
			item_values = recent_list.item(item_id, "values")
			if not item_values:
				return
			photo_path = item_values[0]
			if not os.path.isfile(photo_path):
				messagebox.showwarning("文件不存在", f"最近打开的文件已不存在：\n{photo_path}")
				return
			photo_folder = os.path.dirname(os.path.abspath(photo_path))
			if current_folder != photo_folder:
				load_folder(photo_folder)
			add_images([photo_path])
			if photo_path in image_paths:
				show_image(image_paths.index(photo_path))

	def remove_recent_image():
		selection = recent_list.selection()
		if not selection:
			return
		item_id = selection[0]
		item_values = recent_list.item(item_id, "values")
		if not item_values:
			return
		photo_path = item_values[0]
		if photo_path in recent_paths:
			recent_paths.remove(photo_path)
		recent_item_ids[:] = [item for item in recent_item_ids if item != item_id]
		recent_list.delete(item_id)
		save_settings()
		update_recent_clear_button()

	def clear_recent_images():
		if not recent_paths:
			return
		if not messagebox.askyesno("清空最近打开", "确定要删除全部最近打开记录吗？"):
			return
		recent_paths.clear()
		recent_item_ids.clear()
		recent_list.delete(*recent_list.get_children())
		save_settings()
		update_recent_clear_button()

	def open_settings():
		nonlocal show_drives, show_folders, show_onedrive, show_icloud, cloud_onedrive_preference, cloud_icloud_preference, startup_folder, folder_icon_path, drive_icon_path, remember_recent, close_all_action, warn_before_close_all, fullscreen_mode, maximized_mode, show_startup_tip, settings_window
		if settings_window is not None and settings_window.winfo_exists():
			settings_window.deiconify()
			settings_window.lift()
			settings_window.focus_force()
			return
		settings_window = tk.Toplevel(root)
		settings_window.title("设置")
		settings_height = min(1000, max(760, root.winfo_screenheight() - 80))
		settings_window.geometry(f"600x{settings_height}")
		settings_window.minsize(600, 760)
		settings_window.resizable(True, True)
		settings_window.transient(root)
		settings_window.grab_set()
		settings_window.lift()
		settings_window.focus_force()
		show_drives_var = tk.BooleanVar(value=show_drives)
		show_folders_var = tk.BooleanVar(value=show_folders)
		show_onedrive_var = tk.BooleanVar(value=show_onedrive)
		show_icloud_var = tk.BooleanVar(value=show_icloud)
		remember_recent_var = tk.BooleanVar(value=remember_recent)
		warn_before_close_all_var = tk.BooleanVar(value=warn_before_close_all)
		fullscreen_var = tk.BooleanVar(value=fullscreen_mode)
		maximized_var = tk.BooleanVar(value=maximized_mode)
		show_startup_tip_var = tk.BooleanVar(value=show_startup_tip)
		close_all_action_var = tk.StringVar(value=close_all_action)
		startup_folder_var = tk.StringVar(value=startup_folder or "启动时显示磁盘")
		folder_icon_var = tk.StringVar(value=folder_icon_path)
		drive_icon_var = tk.StringVar(value=drive_icon_path)
		alt_underlined_widgets = []

		def bind_alt(key, widget, invoke=True):
			try:
				label = str(widget.cget("text"))
				underline_index = label.lower().rfind(key.lower())
				widget.configure(underline=-1)
				alt_underlined_widgets.append((widget, underline_index))
			except (tk.TclError, AttributeError):
				pass
			def activate(event=None):
				if invoke and hasattr(widget, "invoke"):
					widget.invoke()
				else:
					widget.focus_set()
				return "break"
			settings_window.bind(f"<Alt-KeyPress-{key}>", activate)

		def show_alt_underlines(event=None):
			for widget, underline_index in alt_underlined_widgets:
				try:
					widget.configure(underline=underline_index)
				except tk.TclError:
					pass

		def hide_alt_underlines(event=None):
			for widget, _ in alt_underlined_widgets:
				try:
					widget.configure(underline=-1)
				except tk.TclError:
					pass

		settings_window.bind("<KeyPress-Alt_L>", show_alt_underlines)
		settings_window.bind("<KeyPress-Alt_R>", show_alt_underlines)
		settings_window.bind("<KeyRelease-Alt_L>", hide_alt_underlines)
		settings_window.bind("<KeyRelease-Alt_R>", hide_alt_underlines)

		settings_notebook = ttk.Notebook(settings_window)
		settings_notebook.pack(fill="both", expand=True, padx=12, pady=12)
		general_tab_container = tk.Frame(settings_notebook)
		general_canvas = tk.Canvas(general_tab_container, highlightthickness=0)
		general_scrollbar = ttk.Scrollbar(general_tab_container, orient="vertical", command=general_canvas.yview)
		general_canvas.configure(yscrollcommand=general_scrollbar.set)
		general_scrollbar.pack(side="right", fill="y")
		general_canvas.pack(side="left", fill="both", expand=True)
		general_tab = tk.Frame(general_canvas)
		general_window_id = general_canvas.create_window((0, 0), window=general_tab, anchor="nw")

		def resize_general_content(event):
			general_canvas.itemconfigure(general_window_id, width=event.width)
			general_canvas.configure(scrollregion=general_canvas.bbox("all"))

		general_tab.bind("<Configure>", resize_general_content)
		general_canvas.bind("<Configure>", resize_general_content)
		shortcut_tab = tk.Frame(settings_notebook)
		settings_notebook.add(general_tab_container, text="常规设置")
		settings_notebook.add(shortcut_tab, text="快捷键编辑")
		tk.Label(shortcut_tab, text="设置快捷键一览", font=("Microsoft YaHei UI", 12, "bold")).pack(anchor="w", padx=16, pady=(16, 10))
		for shortcut_text in (
			"Alt+1  显示磁盘",
			"Alt+2  显示文件夹",
			"Alt+3  显示 OneDrive",
			"Alt+4  显示 iCloud",
			"Alt+5  记录最近打开",
			"Alt+6  关闭多个标签页前提示",
			"Alt+7  启动时全屏",
			"Alt+8  启动时最大化",
			"Alt+9  启动时显示提示",
			"Alt+C  选择关闭标签后的行为",
			"Alt+F  选择启动文件夹，Alt+G/H 修改或恢复文件夹图标",
			"Alt+D/R 修改或恢复磁盘图标，Alt+A 应用，Alt+X 取消",
		):
			shortcut_font = ("Microsoft YaHei UI", 9, "overstrike") if shortcut_text.startswith(("Alt+3", "Alt+4")) else None
			tk.Label(shortcut_tab, text=shortcut_text, anchor="w", font=shortcut_font).pack(fill="x", padx=24, pady=2)

		tk.Label(general_tab, text="文件浏览器显示设置").pack(anchor="w", padx=16, pady=(16, 8))
		show_drives_checkbutton = tk.Checkbutton(general_tab, text="显示磁盘 (1)", variable=show_drives_var)
		show_drives_checkbutton.pack(anchor="w", padx=16)
		bind_alt("1", show_drives_checkbutton)
		show_folders_checkbutton = tk.Checkbutton(general_tab, text="显示文件夹 (2)", variable=show_folders_var)
		show_folders_checkbutton.pack(anchor="w", padx=16)
		bind_alt("2", show_folders_checkbutton)
		onedrive_checkbutton = tk.Checkbutton(
			general_tab,
			text="显示 OneDrive (3)",
			variable=show_onedrive_var,
			state=tk.NORMAL if cloud_settings_unlocked else tk.DISABLED,
		)
		onedrive_checkbutton.pack(anchor="w", padx=16)
		bind_alt("3", onedrive_checkbutton)
		icloud_checkbutton = tk.Checkbutton(
			general_tab,
			text="显示 iCloud (4)",
			variable=show_icloud_var,
			state=tk.NORMAL if cloud_settings_unlocked else tk.DISABLED,
		)
		icloud_checkbutton.pack(anchor="w", padx=16)
		bind_alt("4", icloud_checkbutton)
		cloud_setting_controls[:] = [onedrive_checkbutton, icloud_checkbutton]
		cloud_setting_vars[:] = [show_onedrive_var, show_icloud_var]
		for key, text, variable in (
			("5", "记录最近打开", remember_recent_var),
			("6", "关闭多个标签页前提示", warn_before_close_all_var),
			("7", "启动时全屏", fullscreen_var),
			("8", "启动时最大化", maximized_var),
			("9", "启动时显示提示", show_startup_tip_var),
		):
			checkbutton = tk.Checkbutton(general_tab, text=f"{text} ({key})", variable=variable)
			checkbutton.pack(anchor="w", padx=16)
			bind_alt(key, checkbutton)
		close_action_row = tk.Frame(general_tab)
		close_action_row.pack(fill="x", padx=16, pady=(8, 0))
		tk.Label(close_action_row, text="关闭全部标签后 (C)", width=16, anchor="w").pack(side="left")
		close_action_combo = ttk.Combobox(close_action_row, textvariable=close_all_action_var, values=("主页", "退出"), state="readonly", width=10)
		close_action_combo.pack(side="left")
		bind_alt("c", close_action_combo, invoke=False)
		folder_row = tk.Frame(general_tab)
		folder_row.pack(fill="x", padx=16, pady=12)
		tk.Label(folder_row, textvariable=startup_folder_var, anchor="w").pack(side="left", fill="x", expand=True)

		def choose_startup_folder():
			folder_path = filedialog.askdirectory(parent=settings_window, title="选择启动文件夹")
			if folder_path:
				startup_folder_var.set(folder_path)

		def close_settings():
			nonlocal settings_window
			if settings_window is not None and settings_window.winfo_exists():
				settings_window.grab_release()
				settings_window.destroy()
			settings_window = None

		def apply_settings():
			nonlocal show_drives, show_folders, show_onedrive, show_icloud, cloud_onedrive_preference, cloud_icloud_preference, startup_folder, folder_icon_path, drive_icon_path, remember_recent, close_all_action, warn_before_close_all, fullscreen_mode, maximized_mode, show_startup_tip
			show_drives = show_drives_var.get()
			show_folders = show_folders_var.get()
			show_onedrive = show_onedrive_var.get()
			show_icloud = show_icloud_var.get()
			if cloud_settings_unlocked:
				cloud_onedrive_preference = show_onedrive
				cloud_icloud_preference = show_icloud
			remember_recent = remember_recent_var.get()
			warn_before_close_all = warn_before_close_all_var.get()
			fullscreen_mode = fullscreen_var.get()
			maximized_mode = maximized_var.get()
			show_startup_tip = show_startup_tip_var.get()
			close_all_action = close_all_action_var.get()
			root.attributes("-fullscreen", fullscreen_mode)
			root.state("zoomed" if maximized_mode else "normal")
			folder_icon_path = folder_icon_var.get()
			drive_icon_path = drive_icon_var.get()
			icon_paths["folder"] = folder_icon_path
			icon_paths["drive"] = drive_icon_path
			icon_paths["system_drive"] = system_drive_icon_path
			folder_icon_cache.clear()
			if not remember_recent:
				recent_paths.clear()
				recent_item_ids.clear()
				recent_list.delete(*recent_list.get_children())
			update_recent_clear_button()
			selected_folder = startup_folder_var.get()
			startup_folder = "" if selected_folder == "启动时显示磁盘" else selected_folder
			if startup_folder and os.path.isdir(startup_folder):
				load_folder(startup_folder)
			else:
				load_drives()
			save_settings()
			close_settings()

		def choose_icon(icon_var, title, embedded_name):
			icon_path = filedialog.askopenfilename(
				parent=settings_window,
				title=title,
				filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")],
			)
			if icon_path:
				embedded_path = os.path.join(icon_root, embedded_name)
				try:
					if os.path.abspath(icon_path) != os.path.abspath(embedded_path):
						shutil.copy2(icon_path, embedded_path)
					icon_var.set(embedded_path)
				except OSError as error:
					messagebox.showwarning("图标复制失败", f"无法将图标内置到软件目录：\n{error}", parent=settings_window)

		def reset_icon(icon_var, default_path):
			icon_var.set(default_path)

		def update_icon_preview(icon_var, preview_label):
			try:
				with Image.open(icon_var.get()) as source_icon:
					preview_image = source_icon.convert("RGBA")
				preview_image.thumbnail((40, 40), Image.Resampling.LANCZOS)
				preview_label.image = ImageTk.PhotoImage(preview_image)
				preview_label.configure(image=preview_label.image, text="", width=64, height=64)
			except (OSError, SyntaxError, ValueError):
				preview_label.configure(image="", text="无预览", width=8, height=4)

		def choose_icon_with_preview(icon_var, title, embedded_name, preview_label):
			choose_icon(icon_var, title, embedded_name)
			update_icon_preview(icon_var, preview_label)

		def reset_icon_with_preview(icon_var, default_path, preview_label):
			reset_icon(icon_var, default_path)
			update_icon_preview(icon_var, preview_label)

		choose_folder_button = ttk.Button(folder_row, text="选择文件夹 (F)", command=choose_startup_folder)
		choose_folder_button.pack(side="right", padx=(8, 0))
		bind_alt("f", choose_folder_button)
		for label, icon_var, title, embedded_name in (
			("文件夹图标", folder_icon_var, "选择文件夹图标", "custom_folder.ico"),
			("磁盘图标", drive_icon_var, "选择磁盘图标", "custom_drive.ico"),
		):
			icon_row = tk.Frame(general_tab)
			icon_row.pack(fill="x", padx=16, pady=3)
			tk.Label(icon_row, text=label, width=10, anchor="w").pack(side="left")
			icon_preview = tk.Label(icon_row, width=8, height=4, relief="groove", anchor="center")
			icon_preview.pack(side="left", padx=(0, 8))
			update_icon_preview(icon_var, icon_preview)
			button_text = "修改文件夹图标 (G)" if label == "文件夹图标" else "修改磁盘图标 (D)"
			choose_icon_button = ttk.Button(icon_row, text=button_text, command=lambda value=icon_var, text=title, embedded=embedded_name, preview=icon_preview: choose_icon_with_preview(value, text, embedded, preview))
			choose_icon_button.pack(side="right")
			default_path = default_folder_icon_path if label == "文件夹图标" else default_drive_icon_path
			reset_text = "恢复默认 (H)" if label == "文件夹图标" else "恢复默认 (R)"
			reset_icon_button = ttk.Button(icon_row, text=reset_text, command=lambda value=icon_var, path=default_path, preview=icon_preview: reset_icon_with_preview(value, path, preview))
			reset_icon_button.pack(side="right", padx=(0, 6))
			if label == "文件夹图标":
				bind_alt("g", choose_icon_button)
				bind_alt("h", reset_icon_button)
			else:
				bind_alt("d", choose_icon_button)
				bind_alt("r", reset_icon_button)

		about_frame = ttk.LabelFrame(general_tab, text="关于")
		about_frame.pack(fill="x", padx=16, pady=(14, 0))
		tk.Label(about_frame, text="作者：DevinChang", anchor="w").pack(fill="x", padx=10, pady=(8, 2))
		tk.Label(about_frame, text="版本：1.1.2（测试版）", anchor="w", foreground="red").pack(fill="x", padx=10, pady=2)
		tk.Label(about_frame, text="邮箱：Changdevin2025@outlook.com", anchor="w").pack(fill="x", padx=10, pady=2)
		tk.Label(about_frame, text="这是一个开源软件", anchor="w").pack(fill="x", padx=10, pady=2)
		tk.Label(about_frame, text="由 AI 辅助生成", anchor="w").pack(fill="x", padx=10, pady=(2, 8))
		github_url = "https://github.com/DevinChang2026/Personal"
		github_link = tk.Label(
			about_frame,
			text="GitHub 项目：DevinChang2026/Personal",
			anchor="w",
			foreground="#06c",
			cursor="hand2",
		)
		github_link.pack(fill="x", padx=10, pady=(0, 8))
		github_link.bind("<Button-1>", lambda event: webbrowser.open(github_url))

		button_row = tk.Frame(general_tab)
		button_row.pack(side="bottom", fill="x", padx=16, pady=16)
		apply_button = ttk.Button(button_row, text="应用 (A)", width=8, command=apply_settings)
		apply_button.pack(side="right")
		bind_alt("a", apply_button)
		cancel_button = ttk.Button(button_row, text="取消 (X)", width=8, command=close_settings)
		cancel_button.pack(side="right", padx=(0, 8))
		bind_alt("x", cancel_button)
		settings_window.protocol("WM_DELETE_WINDOW", close_settings)

	def load_drives():
		nonlocal current_folder, current_folder_images
		current_folder = ""
		current_folder_images = []
		address_entry.delete(0, tk.END)
		address_entry.insert(0, "此电脑")
		explorer.delete(*explorer.get_children())
		if not show_drives:
			update_next_button()
			explorer.focus_set()
			return
		cloud_locations = []
		onedrive_path = next(
			(os.environ.get(name) for name in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer") if os.environ.get(name)),
			"",
		)
		if show_onedrive and onedrive_path and os.path.isdir(onedrive_path):
			cloud_locations.append(("OneDrive", onedrive_path, "onedrive"))
		icloud_candidates = (
			os.path.join(os.path.expanduser("~"), "iCloudDrive"),
			os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "iCloudDrive"),
		)
		icloud_path = next((path for path in icloud_candidates if os.path.isdir(path)), "")
		if show_icloud and icloud_path:
			cloud_locations.append(("iCloud", icloud_path, "icloud"))
		for cloud_name, cloud_path, cloud_kind in cloud_locations:
			explorer.insert("", "end", text=cloud_name, image=get_cloud_icon(cloud_kind), values=(cloud_path, "folder"))
		for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
			drive_path = f"{drive_letter}:\\"
			if os.path.isdir(drive_path):
				icon_kind = "system_drive" if f"{drive_letter}:" == system_drive else "drive"
				explorer.insert(
					"",
					"end",
					text=f"{drive_letter}: 盘",
					image=get_file_icon(drive_path, icon_kind),
					values=(drive_path, "folder"),
				)
		if explorer.get_children():
			first_item = explorer.get_children()[0]
			explorer.selection_set(first_item)
			explorer.focus(first_item)
		explorer.focus_set()

	def open_explorer_item(event):
		selection = explorer.selection()
		if not selection:
			return
		item_id = selection[0]
		item_path, kind = explorer.item(item_id, "values")
		if kind == "drives":
			load_drives()
			return
		if kind == "folder":
			ensure_folder_tab(item_path)
			load_folder(item_path)
			return
		if kind == "image":
			add_images([item_path])
			show_image(image_paths.index(item_path))

	def open_explorer_image(event):
		item_id = explorer.identify_row(event.y)
		if not item_id:
			return
		item_path, kind = explorer.item(item_id, "values")
		if kind == "image":
			add_images([item_path])
			show_image(image_paths.index(item_path))

	def navigate_explorer_keyboard(event):
		selection = explorer.selection()
		items = explorer.get_children()
		if event.keysym in ("Up", "Down"):
			if not items:
				return "break"
			if selection and selection[0] in items:
				current_position = items.index(selection[0])
			else:
				current_position = 0 if event.keysym == "Down" else len(items) - 1
			step = 1 if event.keysym == "Down" else -1
			next_position = max(0, min(len(items) - 1, current_position + step))
			explorer.selection_set(items[next_position])
			explorer.focus(items[next_position])
			explorer.see(items[next_position])
			return "break"
		if not selection:
			return "break"
		item_path, kind = explorer.item(selection[0], "values")
		if event.keysym in ("Return", "KP_Enter"):
			if kind == "folder":
				ensure_folder_tab(item_path)
				load_folder(item_path)
			elif kind == "image":
				add_images([item_path])
				show_image(image_paths.index(item_path))
			return "break"
		if event.keysym == "BackSpace":
			if current_folder:
				parent = os.path.dirname(current_folder)
				if parent and parent != current_folder:
					load_folder(parent)
				else:
					load_drives()
			return "break"

	def go_back_with_alt_left(event):
		if current_folder:
			parent = os.path.dirname(current_folder)
			if parent and parent != current_folder:
				load_folder(parent)
			else:
				load_drives()
		return "break"

	def update_control_states():
		has_image = current_index >= 0
		if zoom_out_button is None:
			return
		zoom_out_button.configure(state=tk.NORMAL if has_image and zoom_percent > min_zoom else tk.DISABLED)
		zoom_in_button.configure(state=tk.NORMAL if has_image and zoom_percent < max_zoom else tk.DISABLED)
		next_button.configure(
			state=tk.NORMAL if has_image and len(get_slideshow_images()) >= 2 else tk.DISABLED,
		)
		open_folder_button.configure(state=tk.NORMAL if has_image or current_folder else tk.DISABLED)
		zoom_scale.configure(state=tk.NORMAL if has_image else tk.DISABLED)
		zoom_entry.configure(state=tk.NORMAL if has_image else tk.DISABLED)
		favorite_button.configure(state=tk.NORMAL if has_image else tk.DISABLED)

	def scroll_explorer(event):
		explorer.yview_scroll(-1 if event.delta > 0 else 1, "units")
		return "break"

	def drop_image(event):
		add_images(root.tk.splitlist(event.data))

	def change_zoom(amount):
		set_zoom(zoom_percent + amount)

	def set_zoom(value):
		nonlocal zoom_percent, zoom_job
		try:
			zoom_percent = max(min_zoom, min(max_zoom, int(float(value))))
		except (TypeError, ValueError):
			zoom_percent = 100
		if zoom_scale is not None:
			zoom_scale.set(zoom_percent)
			zoom_entry.configure(state=tk.NORMAL)
			zoom_entry.delete(0, tk.END)
			zoom_entry.insert(0, f"{zoom_percent}%")
		update_control_states()
		if zoom_job is not None:
			root.after_cancel(zoom_job)
		zoom_job = root.after(80, render_zoom)

	def render_zoom():
		nonlocal zoom_job
		zoom_job = None
		if 0 <= current_index < len(image_paths):
			show_image(current_index)

	def wheel_zoom(event):
		change_zoom(20 if event.delta > 0 else -20)

	def start_drag(event):
		nonlocal drag_start
		if canvas_image_id is None or not image_canvas.find_withtag(canvas_image_id):
			return
		drag_start = (event.x, event.y)
		image_canvas.scan_mark(event.x, event.y)

	def drag_image(event):
		nonlocal drag_start
		if drag_start is not None:
			image_canvas.scan_dragto(event.x, event.y, gain=1)

	def stop_drag(event):
		nonlocal drag_start
		drag_start = None

	def show_next_image():
		navigation_paths = get_slideshow_images()
		if len(navigation_paths) < 2:
			return
		current_path = image_paths[current_index] if 0 <= current_index < len(image_paths) else ""
		try:
			next_index = (navigation_paths.index(current_path) + 1) % len(navigation_paths)
		except ValueError:
			next_index = 0
		add_images([navigation_paths[next_index]])
		show_image(image_paths.index(navigation_paths[next_index]))

	def show_previous_image():
		navigation_paths = get_slideshow_images()
		if len(navigation_paths) < 2:
			return
		current_path = image_paths[current_index] if 0 <= current_index < len(image_paths) else ""
		try:
			previous_index = (navigation_paths.index(current_path) - 1) % len(navigation_paths)
		except ValueError:
			previous_index = len(navigation_paths) - 1
		add_images([navigation_paths[previous_index]])
		show_image(image_paths.index(navigation_paths[previous_index]))

	def update_next_button():
		if next_button is not None and previous_button is not None:
			state = tk.NORMAL if len(get_slideshow_images()) >= 2 else tk.DISABLED
			next_button.configure(state=state)
			previous_button.configure(state=state)

	def open_in_new_window(item_path=None, item_kind=None):
		if item_path is None:
			selection = explorer.selection()
			if not selection:
				return
			item_values = explorer.item(selection[0], "values")
			if len(item_values) < 2:
				return
			item_path, item_kind = item_values[0], item_values[1]
		if item_kind == "folder":
			if not os.path.isdir(item_path):
				messagebox.showwarning("文件夹不存在", f"找不到文件夹：\n{item_path}")
				return
			folder_window = tk.Toplevel(root)
			folder_window.title(f"{os.path.basename(item_path) or item_path} - 文件浏览器")
			folder_window.geometry("560x480")
			tk.Label(folder_window, text=item_path, anchor="w").pack(fill="x", padx=12, pady=(12, 6))
			folder_tree = ttk.Treeview(folder_window, show="tree")
			folder_scrollbar = ttk.Scrollbar(folder_window, orient="vertical", command=folder_tree.yview)
			folder_tree.configure(yscrollcommand=folder_scrollbar.set)
			folder_scrollbar.pack(side="right", fill="y", padx=(0, 12), pady=(0, 12))
			folder_tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=(0, 12))
			try:
				entries = sorted(os.scandir(item_path), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
			except OSError as error:
				messagebox.showerror("无法打开文件夹", f"无法读取：\n{item_path}\n\n原因：{error}", parent=folder_window)
				folder_window.destroy()
				return
			for entry in entries:
				folder_tree.insert("", "end", text=entry.name, values=(entry.path, "folder" if entry.is_dir() else "file"))
			return
		if item_kind != "image":
			return
		photo_path = item_path
		if not os.path.isfile(photo_path):
			messagebox.showwarning("文件不存在", f"找不到图片文件：\n{photo_path}")
			return
		try:
			with Image.open(photo_path) as source_image:
				image = source_image.copy()
			image.thumbnail((900, 600))
		except (OSError, SyntaxError, ValueError) as error:
			messagebox.showerror(
				"无法打开图片",
				f"无法打开文件：\n{photo_path}\n\n原因：{error}",
			)
			return

		new_window = tk.Toplevel(root)
		new_window.title(f"{os.path.basename(photo_path)} - 图片查看器")
		new_window.geometry("920x640")
		new_zoom_percent = 100
		new_toolbar = tk.Frame(new_window)
		new_toolbar.pack(fill="x", padx=12, pady=(12, 0))
		new_label = tk.Label(new_window)
		new_label.pack(fill="both", expand=True, padx=12, pady=12)
		new_zoom_scale = tk.Scale(
			new_toolbar,
			from_=min_zoom,
			to=max_zoom,
			orient="horizontal",
			length=260,
			showvalue=False,
		)
		new_zoom_scale.pack(side="left")
		new_zoom_entry = tk.Entry(new_toolbar, width=6, justify="center")
		new_zoom_entry.pack(side="left", padx=(8, 0))

		def show_new_image():
			try:
				with Image.open(photo_path) as source_image:
					new_image = source_image.copy()
				new_zoom_factor = new_zoom_percent / 100
				new_image.thumbnail((900 * new_zoom_factor, 600 * new_zoom_factor))
			except (OSError, SyntaxError, ValueError) as error:
				messagebox.showerror(
					"无法打开图片",
					f"无法打开文件：\n{photo_path}\n\n原因：{error}",
					parent=new_window,
				)
				return
			photo = ImageTk.PhotoImage(new_image)
			new_label.configure(image=photo)
			new_label.image = photo

		def set_new_zoom(value):
			nonlocal new_zoom_percent
			try:
				new_zoom_percent = max(min_zoom, min(max_zoom, int(float(value))))
			except (TypeError, ValueError):
				new_zoom_percent = 100
			new_zoom_scale.set(new_zoom_percent)
			new_zoom_entry.delete(0, tk.END)
			new_zoom_entry.insert(0, f"{new_zoom_percent}%")
			show_new_image()

		def change_new_zoom(amount):
			set_new_zoom(new_zoom_percent + amount)

		def update_new_zoom_buttons():
			new_zoom_out_button.configure(state=tk.DISABLED if new_zoom_percent <= min_zoom else tk.NORMAL)
			new_zoom_in_button.configure(state=tk.DISABLED if new_zoom_percent >= max_zoom else tk.NORMAL)

		def wheel_new_zoom(event):
			change_new_zoom(20 if event.delta > 0 else -20)

		new_zoom_scale.configure(command=set_new_zoom)
		new_zoom_entry.bind("<Return>", lambda event: set_new_zoom(new_zoom_entry.get().rstrip("%")))
		new_zoom_out_button = ttk.Button(new_toolbar, text="缩小", command=lambda: change_new_zoom(-20))
		new_zoom_out_button.pack(side="left", padx=(8, 0))
		new_zoom_in_button = ttk.Button(new_toolbar, text="放大", command=lambda: change_new_zoom(20))
		new_zoom_in_button.pack(side="left", padx=(6, 0))
		new_zoom_scale.set(100)
		new_zoom_entry.insert(0, "100%")
		update_new_zoom_buttons()
		new_label.bind("<MouseWheel>", wheel_new_zoom)
		new_window.bind("<MouseWheel>", wheel_new_zoom)
		show_new_image()

	def open_in_new_tab():
		selection = explorer.selection()
		if not selection:
			return
		photo_path, kind = explorer.item(selection[0], "values")
		if kind == "folder":
			ensure_folder_tab(photo_path, force_new=True)
			load_folder(photo_path)
			return
		if kind != "image":
			return
		add_images([photo_path])
		show_image(image_paths.index(photo_path), force_new_tab=True)

	context_menu = tk.Menu(root, tearoff=False)
	context_menu.add_command(label="复制", command=lambda: copy_selected_files(False))
	context_menu.add_command(label="剪切", command=lambda: copy_selected_files(True))
	context_menu.add_command(label="粘贴", command=paste_files)
	context_menu.add_command(label="删除", command=delete_selected_files)
	context_menu.add_separator()
	context_menu.add_command(label="在新标签页打开", command=open_in_new_tab)
	context_menu.add_command(label="在新窗口打开", command=open_in_new_window)
	recent_context_menu = tk.Menu(root, tearoff=False)
	recent_context_menu.add_command(label="在新窗口打开", command=lambda: open_recent_in_new_window())
	recent_context_menu.add_command(label="删除记录", command=remove_recent_image)
	tab_context_menu = tk.Menu(root, tearoff=False)
	tab_context_menu.add_command(label="关闭标签", command=close_tab)
	tab_context_menu.add_command(label="重命名标签", command=rename_current_tab)

	def show_context_menu(event):
		item_id = explorer.identify_row(event.y)
		if item_id:
			explorer.selection_set(item_id)
			explorer.focus(item_id)
			context_menu.post(event.x_root, event.y_root)
		else:
			context_menu.post(event.x_root, event.y_root)

	def close_context_menu(event):
		context_menu.unpost()
		tab_context_menu.unpost()
		recent_context_menu.unpost()

	def open_recent_in_new_window():
		selection = recent_list.selection()
		if not selection:
			return
		item_values = recent_list.item(selection[0], "values")
		if item_values:
			open_in_new_window(item_values[0], "image")

	def show_recent_context_menu(event):
		item_id = recent_list.identify_row(event.y)
		if not item_id:
			return
		recent_list.selection_set(item_id)
		recent_context_menu.post(event.x_root, event.y_root)

	def show_tab_context_menu(event):
		selected_tab = tab_notebook.index(f"@{event.x},{event.y}")
		tab_id = tab_notebook.tabs()[selected_tab]
		if tab_id in tab_paths:
			tab_notebook.select(tab_id)
			tab_context_menu.entryconfigure("关闭标签", command=lambda: close_tab(tab_id))
			tab_context_menu.entryconfigure("重命名标签", command=rename_current_tab)
			tab_context_menu.post(event.x_root, event.y_root)

	def close_tab_with_middle_click(event):
		try:
			selected_tab = tab_notebook.index(f"@{event.x},{event.y}")
			tab_id = tab_notebook.tabs()[selected_tab]
			close_tab(tab_id)
		except (tk.TclError, IndexError):
			pass

	image_label.drop_target_register(DND_FILES)
	image_label.dnd_bind("<<Drop>>", drop_image)
	image_label.bind("<MouseWheel>", wheel_zoom)
	image_label.bind("<ButtonPress-1>", start_drag)
	image_label.bind("<B1-Motion>", drag_image)
	image_label.bind("<ButtonRelease-1>", stop_drag)
	explorer.bind("<Double-1>", open_explorer_item)
	explorer.bind("<ButtonRelease-1>", open_explorer_image)
	explorer.bind("<Return>", navigate_explorer_keyboard)
	explorer.bind("<KP_Enter>", navigate_explorer_keyboard)
	explorer.bind("<BackSpace>", navigate_explorer_keyboard)
	explorer.bind("<Alt-Left>", go_back_with_alt_left)
	explorer.bind("<Button-3>", show_context_menu)
	explorer.bind("<MouseWheel>", scroll_explorer)
	explorer_scrollbar.bind("<MouseWheel>", scroll_explorer)
	recent_list.bind("<ButtonRelease-1>", open_recent_image)
	favorites_list.bind("<ButtonRelease-1>", open_favorite)
	recent_list.bind("<Button-3>", show_recent_context_menu)
	address_entry.bind("<Return>", lambda event: open_address())
	tab_notebook.bind("<<NotebookTabChanged>>", select_tab_image)
	tab_notebook.bind("<Button-3>", show_tab_context_menu)
	tab_notebook.bind("<Button-2>", close_tab_with_middle_click)
	root.bind("<Control-l>", lambda event: address_entry.focus_set())
	root.bind_all("<Control-Alt-KeyPress-q>", unlock_cloud_settings)
	root.bind("<Left>", lambda event: show_previous_image() if current_index >= 0 else None)
	root.bind("<Right>", lambda event: show_next_image() if current_index >= 0 else None)
	root.bind("<Control-f>", lambda event: toggle_favorite())
	root.bind("<F5>", lambda event: toggle_slideshow())
	root.bind("<F2>", lambda event: rename_current_tab())
	root.bind("<F6>", lambda event: toggle_left_sidebar())
	root.bind("<F7>", lambda event: toggle_right_sidebar())
	root.bind("<F8>", lambda event: toggle_favorites_bar())
	root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
	root.bind("<Button-1>", close_context_menu, add="+")

	home_button = ttk.Button(browser_header, text="主页", command=go_home)
	home_button.pack(side="right")
	close_selected_tab_button = ttk.Button(tab_bar, text="×", width=3, command=close_tab, state=tk.DISABLED)
	close_selected_tab_button.pack(side="left", padx=(4, 0))
	ttk.Button(tab_bar, text="+", width=3, command=add_home_tab).pack(side="left", padx=(4, 0))
	ttk.Button(tab_bar, text="重命名", command=rename_current_tab).pack(side="left", padx=(4, 0))
	close_tab_button = ttk.Button(tab_bar, text="关闭标签", command=close_tab, state=tk.DISABLED)
	close_tab_button.pack(side="left", padx=(4, 0))
	close_all_tabs_button = ttk.Button(tab_bar, text="关闭所有标签", command=close_all_tabs, state=tk.DISABLED)
	close_all_tabs_button.pack(side="left", padx=(4, 0))
	clear_recent_button = ttk.Button(recent_header, text="清空", command=clear_recent_images, state=tk.DISABLED)
	clear_recent_button.pack(side="right")
	left_sidebar_button = ttk.Button(toolbar, text="收起左栏", command=toggle_left_sidebar)
	left_sidebar_button.pack(side="left", padx=(6, 0))
	right_sidebar_button = ttk.Button(toolbar, text="打开右栏", command=toggle_right_sidebar)
	right_sidebar_button.pack(side="left", padx=(6, 0))
	favorites_button = ttk.Button(toolbar, text="打开收藏栏", command=toggle_favorites_bar)
	favorites_button.pack(side="left", padx=(6, 0))
	ttk.Button(toolbar, text="选择图片", command=select_image).pack(side="left", padx=(6, 0))
	open_folder_button = ttk.Button(toolbar, text="打开文件夹", command=select_folder, state=tk.DISABLED)
	open_folder_button.pack(side="right")
	settings_button = ttk.Button(toolbar, text="设置", command=open_settings)
	settings_button.pack(side="right", padx=(0, 6))
	zoom_scale = tk.Scale(
		toolbar,
		from_=min_zoom,
		to=max_zoom,
		orient="horizontal",
		length=220,
		showvalue=False,
	)
	zoom_scale.pack(side="right", padx=(8, 0))
	zoom_scale.configure(state=tk.DISABLED)
	zoom_entry = tk.Entry(toolbar, width=6, justify="center")
	zoom_entry.pack(side="right")
	zoom_entry.configure(state=tk.DISABLED)
	zoom_scale.configure(command=set_zoom)
	zoom_entry.bind("<Return>", lambda event: set_zoom(zoom_entry.get().rstrip("%")))
	zoom_scale.set(100)
	zoom_entry.insert(0, "100%")
	previous_button = ttk.Button(
		navigation_bar,
		text="上一个",
		image=get_navigation_icon("previous"),
		compound="left",
		command=show_previous_image,
		state=tk.DISABLED,
	)
	previous_button.pack(side="left")
	slideshow_button = ttk.Button(navigation_bar, text="幻灯片", command=toggle_slideshow)
	slideshow_button.pack(side="left", padx=(6, 0))
	next_button = ttk.Button(
		navigation_bar,
		text="下一个",
		image=get_navigation_icon("next"),
		compound="left",
		command=show_next_image,
		state=tk.DISABLED,
	)
	next_button.pack(side="left", padx=(6, 0))
	zoom_out_button = ttk.Button(navigation_bar, text="缩小", command=lambda: change_zoom(-20), state=tk.DISABLED)
	zoom_out_button.pack(side="left", padx=(18, 0))
	zoom_in_button = ttk.Button(navigation_bar, text="放大", command=lambda: change_zoom(20), state=tk.DISABLED)
	zoom_in_button.pack(side="left", padx=(6, 0))
	favorite_button = ttk.Button(navigation_bar, text="收藏图片", command=toggle_favorite, state=tk.DISABLED)
	favorite_button.pack(side="left", padx=(18, 0))

	for widget, tip in (
		(left_sidebar_button, "收起或展开左侧文件浏览器（F6）"),
		(right_sidebar_button, "收起或展开右侧最近打开（F7）"),
		(favorites_button, "收起或展开底部收藏栏（F8）"),
		(favorite_button, "收藏或取消收藏当前图片（Ctrl+F）"),
		(slideshow_button, "每 3 秒自动切换当前文件夹图片（F5）"),
		(previous_button, "查看上一张图片（左方向键）"),
		(next_button, "查看下一张图片（右方向键）"),
		(zoom_out_button, "缩小图片"),
		(zoom_in_button, "放大图片"),
		(settings_button, "打开设置"),
	):
		Tooltip(widget, tip)

	def open_startup_arguments():
		startup_files = [
			os.path.abspath(argument.strip().strip('"'))
			for argument in sys.argv[1:]
			if argument.strip().strip('"')
		]
		startup_files = [path for path in startup_files if os.path.exists(path)]
		if not startup_files:
			return
		first_path = startup_files[0]
		if os.path.isdir(first_path):
			load_folder(first_path)
			return
		image_files = [path for path in startup_files if os.path.isfile(path)]
		if not image_files:
			return
		load_folder(os.path.dirname(image_files[0]))
		add_images(image_files)
		if image_files[0] in image_paths:
			show_image(image_paths.index(image_files[0]))

	refresh_favorites()
	refresh_content_layout()
	if not left_sidebar_visible:
		left_sidebar_button.configure(text="打开左栏")
	if not right_sidebar_visible:
		right_sidebar_button.configure(text="打开右栏")
	if not favorites_visible:
		favorites_list.pack_forget()
		favorites_button.configure(text="打开收藏栏")
	root.attributes("-fullscreen", fullscreen_mode)
	root.state("zoomed" if maximized_mode else "normal")
	load_recent_images()
	update_recent_clear_button()
	load_drives()
	open_startup_arguments()
	update_close_tab_buttons()
	explorer.focus_set()
	root.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), root.destroy()))
	if show_startup_tip:
		root.after(500, lambda: messagebox.showinfo(
			"使用提示",
			"双击或按回车打开项目；右键可在新标签页或新窗口打开。\n"
			"标签栏的 + 只会手动新建主页标签，Esc 可退出全屏。",
		))
	root.mainloop()


if __name__ == "__main__":
	main()			