"""Modern Tkinter GUI for the Connect 4 assignment.

This version keeps the board model untouched while redesigning the user
interface around a centered, responsive canvas. The board is redrawn from
scratch on resize so the geometry stays pixel-aligned at every window size.
"""

from __future__ import annotations

from dataclasses import dataclass
from tkinter import Canvas, StringVar, Tk, TclError, messagebox, ttk
from typing import Callable

from connect4.ai import Connect4AI
from connect4.board import COMPUTER, HUMAN, Connect4Board
from connect4.heuristics import HeuristicEvaluator
from connect4.tree import SearchStats, TraceEvent, TreePrinter


@dataclass(slots=True)
class GameColors:
    background: str = "#eef3f9"
    surface: str = "#ffffff"
    surface_alt: str = "#f4f7fb"
    board: str = "#16395f"
    board_shadow: str = "#0b1729"
    slot: str = "#dbe7f3"
    slot_edge: str = "#b9cadb"
    hover: str = "#275a87"
    hover_edge: str = "#88b8eb"
    human: str = "#e85a66"
    human_glow: str = "#ffb7bf"
    computer: str = "#f0c74d"
    computer_glow: str = "#ffe9a5"
    accent: str = "#2f6fd6"
    accent_dark: str = "#21529f"
    text: str = "#203244"
    muted_text: str = "#627287"
    success: str = "#2e9f6d"
    warning: str = "#c98319"
    danger: str = "#c94d57"
    highlight: str = "#ffde78"
    panel_border: str = "#d8e2ee"


@dataclass(slots=True)
class BoardLayout:
    canvas_width: int
    canvas_height: int
    board_x: int
    board_y: int
    board_width: int
    board_height: int
    cell_size: int
    slot_inset: int
    piece_inset: int
    radius: int


class Connect4App:
    """Main application controller for the Connect 4 game."""

    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Connect 4 - Modern Edition")
        self.colors = GameColors()
        self.root.configure(bg=self.colors.background)
        self.root.minsize(1040, 840)
        self.root.geometry(self._center_geometry(1280, 900))

        try:
            scaling = self.root.winfo_fpixels("1i") / 72.0
            self.root.tk.call("tk", "scaling", max(1.0, min(scaling, 1.7)))
        except TclError:
            pass

        self.evaluator = HeuristicEvaluator()
        self.ai = Connect4AI(self.evaluator)
        self.tree_printer = TreePrinter(enabled=True, max_depth=3)

        self.board = Connect4Board()
        self.game_active = False
        self.current_player = HUMAN
        self.selected_algorithm = StringVar(value="minimax")
        self.depth_value = StringVar(value="4")
        self.status_value = StringVar(value="Select an AI algorithm, choose a depth, and start a match.")
        self.turn_value = StringVar(value="Waiting to start")
        self.stats_value = StringVar(value="No moves yet")
        self.result_value = StringVar(value="")
        self.score_value = StringVar(value="Connect-fours: Human 0 | Computer 0")
        self.ai_score_value = StringVar(value="AI selected score: -")

        self.animating = False
        self.hover_column: int | None = None
        self.winner_player = 0
        self.canvas_width = 1
        self.canvas_height = 1
        self.drop_animation_steps = 18
        self.drop_animation_interval = 16
        self.board_margin = 28

        self.algorithm_widgets: list[ttk.Widget] = []
        self.start_button: ttk.Button | None = None
        self.restart_button: ttk.Button | None = None
        self.turn_badge: ttk.Label | None = None
        self.result_panel: ttk.Frame | None = None
        self.result_label: ttk.Label | None = None
        self.scroll_canvas: Canvas | None = None
        self.scrollbar: ttk.Scrollbar | None = None
        self.content_frame: ttk.Frame | None = None
        self.canvas: Canvas | None = None
        self.tree_view: ttk.Treeview | None = None
        self.layout = BoardLayout(1, 1, 0, 0, 0, 0, 1, 4, 6, 8)

        self._configure_styles()
        self._build_layout()
        self._set_tree_lines(["Search tree output will appear after the computer moves."])
        self._update_score_display()
        self.root.after_idle(self._redraw_scene)

    def run(self) -> None:
        self.root.mainloop()

    def _center_geometry(self, width: int, height: int) -> str:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_pos = max((screen_width - width) // 2, 0)
        y_pos = max((screen_height - height) // 2, 0)
        return f"{width}x{height}+{x_pos}+{y_pos}"

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except TclError:
            pass

        style.configure("Root.TFrame", background=self.colors.background)
        style.configure("Card.TFrame", background=self.colors.surface)
        style.configure("CardAlt.TFrame", background=self.colors.surface_alt)
        style.configure(
            "Search.Treeview",
            background="#f8fbff",
            fieldbackground="#f8fbff",
            foreground=self.colors.text,
            rowheight=22,
            font=("Consolas", 9),
        )
        style.map(
            "Search.Treeview",
            background=[("selected", "#dfeaf8")],
            foreground=[("selected", self.colors.text)],
        )
        style.configure("ResultNeutral.TFrame", background=self.colors.surface)
        style.configure("ResultSuccess.TFrame", background=self.colors.success)
        style.configure("ResultWarning.TFrame", background=self.colors.warning)
        style.configure("ResultDanger.TFrame", background=self.colors.danger)

        style.configure(
            "Title.TLabel",
            background=self.colors.background,
            foreground=self.colors.text,
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors.background,
            foreground=self.colors.muted_text,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel",
            background=self.colors.surface,
            foreground=self.colors.text,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background=self.colors.surface,
            foreground=self.colors.text,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Muted.TLabel",
            background=self.colors.surface,
            foreground=self.colors.muted_text,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Metric.TLabel",
            background=self.colors.surface,
            foreground=self.colors.text,
            font=("Segoe UI", 10),
        )
        style.configure(
            "BadgeIdle.TLabel",
            background=self.colors.surface_alt,
            foreground=self.colors.text,
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.configure(
            "BadgeHuman.TLabel",
            background=self.colors.human,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.configure(
            "BadgeComputer.TLabel",
            background=self.colors.computer,
            foreground="#1f2430",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.configure(
            "BadgeAccent.TLabel",
            background=self.colors.accent,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
        )
        style.configure(
            "ResultNeutral.TLabel",
            background=self.colors.surface,
            foreground=self.colors.text,
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
        )
        style.configure(
            "ResultSuccess.TLabel",
            background=self.colors.success,
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
        )
        style.configure(
            "ResultWarning.TLabel",
            background=self.colors.warning,
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
        )
        style.configure(
            "ResultDanger.TLabel",
            background=self.colors.danger,
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padding=(14, 10),
        )
        style.configure(
            "Accent.TButton",
            background=self.colors.accent,
            foreground="#ffffff",
            padding=(16, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.colors.accent_dark), ("pressed", self.colors.accent_dark)],
            foreground=[("disabled", "#d9e1ea"), ("active", "#ffffff")],
        )
        style.configure(
            "Secondary.TButton",
            background=self.colors.surface_alt,
            foreground=self.colors.text,
            padding=(16, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#e4ebf4"), ("pressed", "#d9e2ee")],
        )
        style.configure(
            "Option.TRadiobutton",
            background=self.colors.surface,
            foreground=self.colors.text,
            font=("Segoe UI", 10),
        )
        style.map(
            "Option.TRadiobutton",
            background=[("active", self.colors.surface)],
            foreground=[("disabled", self.colors.muted_text)],
        )
        style.configure(
            "Depth.TSpinbox",
            fieldbackground=self.colors.surface_alt,
            background=self.colors.surface_alt,
            foreground=self.colors.text,
            arrowsize=14,
            padding=4,
        )
        style.configure(
            "Modern.Vertical.TScrollbar",
            background=self.colors.surface_alt,
            troughcolor=self.colors.background,
            arrowcolor=self.colors.text,
            bordercolor=self.colors.panel_border,
            lightcolor=self.colors.surface_alt,
            darkcolor=self.colors.surface_alt,
            gripcount=0,
        )
        style.map(
            "Modern.Vertical.TScrollbar",
            background=[("active", "#dfe8f3"), ("pressed", "#cdd9e6")],
        )

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = ttk.Frame(self.root, style="Root.TFrame")
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        self.scroll_canvas = Canvas(
            shell,
            bg=self.colors.background,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(
            shell,
            orient="vertical",
            command=self.scroll_canvas.yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content_frame = ttk.Frame(self.scroll_canvas, style="Root.TFrame", padding=24)
        self.content_window = self.scroll_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.columnconfigure(0, weight=1)

        self.scroll_canvas.bind("<Configure>", self._on_scroll_canvas_resize)
        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        self._build_header(self.content_frame)
        self._build_controls(self.content_frame)
        self._build_board_section(self.content_frame)
        self._build_footer(self.content_frame)

    def _on_scroll_canvas_resize(self, event) -> None:  # type: ignore[no-untyped-def]
        if self.scroll_canvas is None:
            return

        self.scroll_canvas.itemconfigure(self.content_window, width=event.width)

    def _on_content_configure(self, _event) -> None:
        if self.scroll_canvas is None:
            return

        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event) -> None:  # type: ignore[no-untyped-def]
        if self.scroll_canvas is None:
            return

        delta = event.delta
        if delta == 0:
            return

        step = int(-delta / 120)
        if step == 0:
            step = -1 if delta > 0 else 1
        self.scroll_canvas.yview_scroll(step, "units")

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        title_row = ttk.Frame(header, style="Root.TFrame")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.columnconfigure(0, weight=1)

        ttk.Label(title_row, text="Connect 4", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(title_row, text="Modern Tkinter UI", style="BadgeAccent.TLabel").grid(row=0, column=1, sticky="e")

        ttk.Label(
            header,
            text="Centered board, hover preview, smooth drop animation, and a clean information layout.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _build_controls(self, parent: ttk.Frame) -> None:
        controls = ttk.Frame(parent, style="Card.TFrame", padding=18)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        controls.columnconfigure(0, weight=2)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)

        algorithm_panel = ttk.Frame(controls, style="Card.TFrame")
        algorithm_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        ttk.Label(algorithm_panel, text="AI algorithm", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            algorithm_panel,
            text="Choose the search strategy used by the computer player.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))

        for index, (label, value) in enumerate(
            (
                ("Minimax", "minimax"),
                ("Minimax with alpha-beta pruning", "alpha-beta"),
                ("Expected minimax", "expected"),
            )
        ):
            radio = ttk.Radiobutton(
                algorithm_panel,
                text=label,
                value=value,
                variable=self.selected_algorithm,
                style="Option.TRadiobutton",
            )
            radio.grid(row=2 + index, column=0, sticky="w", pady=2)
            self.algorithm_widgets.append(radio)

        depth_panel = ttk.Frame(controls, style="Card.TFrame")
        depth_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 16))
        ttk.Label(depth_panel, text="Depth", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            depth_panel,
            text="Higher values improve AI strength but take longer to search.",
            style="Muted.TLabel",
            wraplength=230,
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))
        depth_row = ttk.Frame(depth_panel, style="Card.TFrame")
        depth_row.grid(row=2, column=0, sticky="w")
        ttk.Label(depth_row, text="Search depth K:", style="Body.TLabel").pack(side="left")
        self.depth_spinbox = ttk.Spinbox(
            depth_row,
            from_=1,
            to=8,
            textvariable=self.depth_value,
            width=8,
            style="Depth.TSpinbox",
        )
        self.depth_spinbox.pack(side="left", padx=(8, 0))
        self.algorithm_widgets.append(self.depth_spinbox)

        actions_panel = ttk.Frame(controls, style="Card.TFrame")
        actions_panel.grid(row=0, column=2, sticky="nsew")
        ttk.Label(actions_panel, text="Match controls", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.turn_badge = ttk.Label(actions_panel, textvariable=self.turn_value, style="BadgeIdle.TLabel")
        self.turn_badge.grid(row=1, column=0, sticky="ew", pady=(8, 10))

        self.start_button = ttk.Button(actions_panel, text="Start Game", style="Accent.TButton", command=self.start_game)
        self.start_button.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.restart_button = ttk.Button(actions_panel, text="Restart", style="Secondary.TButton", command=self.restart_game)
        self.restart_button.grid(row=3, column=0, sticky="ew")

    def _build_board_section(self, parent: ttk.Frame) -> None:
        board_panel = ttk.Frame(parent, style="Card.TFrame", padding=18)
        board_panel.grid(row=2, column=0, sticky="nsew", pady=(0, 16))
        board_panel.columnconfigure(0, weight=1)
        board_panel.rowconfigure(1, weight=1)

        board_header = ttk.Frame(board_panel, style="Card.TFrame")
        board_header.grid(row=0, column=0, sticky="ew")
        board_header.columnconfigure(0, weight=1)
        ttk.Label(board_header, text="Board", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            board_header,
            text="Hover a column to preview the drop, then click to place a piece.",
            style="Muted.TLabel",
        ).grid(row=0, column=1, sticky="e")

        self.canvas = Canvas(
            board_panel,
            bg=self.colors.background,
            highlightthickness=0,
            bd=0,
            relief="flat",
            height=680,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Leave>", self._on_canvas_leave)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_footer(self, parent: ttk.Frame) -> None:
        footer = ttk.Frame(parent, style="Card.TFrame", padding=18)
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)
        footer.rowconfigure(4, weight=1)

        self.result_panel = ttk.Frame(footer, style="ResultNeutral.TFrame", padding=0)
        self.result_panel.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.result_panel.columnconfigure(0, weight=1)

        self.result_label = ttk.Label(
            self.result_panel,
            textvariable=self.result_value,
            style="ResultNeutral.TLabel",
            justify="left",
            wraplength=980,
        )
        self.result_label.grid(row=0, column=0, sticky="ew")

        ttk.Label(footer, text="Status", style="Section.TLabel").grid(row=1, column=0, sticky="w", pady=(14, 4))
        ttk.Label(footer, text="Last move", style="Section.TLabel").grid(row=1, column=1, sticky="w", pady=(14, 4))
        ttk.Label(footer, textvariable=self.status_value, style="Body.TLabel", wraplength=520).grid(
            row=2,
            column=0,
            sticky="w",
        )
        ttk.Label(footer, textvariable=self.stats_value, style="Body.TLabel", wraplength=520).grid(
            row=2,
            column=1,
            sticky="w",
        )

        score_panel = ttk.Frame(footer, style="CardAlt.TFrame", padding=14)
        score_panel.grid(row=3, column=0, sticky="nsew", pady=(14, 0), padx=(0, 8))
        score_panel.columnconfigure(0, weight=1)
        ttk.Label(score_panel, text="Scoreboard", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            score_panel,
            text="Live connect-four counts and the heuristic score for the current board.",
            style="Muted.TLabel",
            wraplength=450,
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))
        ttk.Label(score_panel, textvariable=self.score_value, style="Metric.TLabel", wraplength=450).grid(
            row=2,
            column=0,
            sticky="w",
        )
        ttk.Label(score_panel, textvariable=self.ai_score_value, style="Metric.TLabel", wraplength=450).grid(
            row=3,
            column=0,
            sticky="w",
            pady=(6, 0),
        )

        tree_panel = ttk.Frame(footer, style="CardAlt.TFrame", padding=14)
        tree_panel.grid(row=3, column=1, rowspan=2, sticky="nsew", pady=(14, 0), padx=(8, 0))
        tree_panel.columnconfigure(0, weight=1)
        tree_panel.rowconfigure(2, weight=1)
        ttk.Label(tree_panel, text="Search Tree", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            tree_panel,
            text="Depth-limited AI trace for the latest computer move.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 8))

        tree_text_row = ttk.Frame(tree_panel, style="CardAlt.TFrame")
        tree_text_row.grid(row=2, column=0, sticky="nsew")
        tree_text_row.columnconfigure(0, weight=1)
        tree_text_row.rowconfigure(0, weight=1)

        self.tree_view = ttk.Treeview(
            tree_text_row,
            show="tree",
            selectmode="browse",
            height=14,
            style="Search.Treeview",
        )
        self.tree_view.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(tree_text_row, orient="vertical", command=self.tree_view.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        tree_scroll_x = ttk.Scrollbar(tree_text_row, orient="horizontal", command=self.tree_view.xview)
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        self.tree_view.configure(yscrollcommand=tree_scroll.set, xscrollcommand=tree_scroll_x.set)

    def _set_settings_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in self.algorithm_widgets:
            widget.configure(state=state)

    def _set_turn_badge(self) -> None:
        if self.turn_badge is None:
            return

        if not self.game_active:
            style = "BadgeIdle.TLabel"
        elif self.current_player == HUMAN:
            style = "BadgeHuman.TLabel"
        else:
            style = "BadgeComputer.TLabel"
        self.turn_badge.configure(style=style)

    def _set_result_style(self, mode: str) -> None:
        if self.result_panel is None or self.result_label is None:
            return

        if mode == "success":
            panel_style = "ResultSuccess.TFrame"
            label_style = "ResultSuccess.TLabel"
        elif mode == "warning":
            panel_style = "ResultWarning.TFrame"
            label_style = "ResultWarning.TLabel"
        elif mode == "danger":
            panel_style = "ResultDanger.TFrame"
            label_style = "ResultDanger.TLabel"
        else:
            panel_style = "ResultNeutral.TFrame"
            label_style = "ResultNeutral.TLabel"

        self.result_panel.configure(style=panel_style)
        self.result_label.configure(style=label_style)

    def _set_tree_lines(self, lines: list[str]) -> None:
        if self.tree_view is None:
            return

        self.tree_view.delete(*self.tree_view.get_children())

        if not lines:
            self.tree_view.insert("", "end", text="No tree generated for this turn.")
            return

        parents_by_depth: dict[int, str] = {-1: ""}
        for raw_line in lines:
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue

            stripped = line.strip()
            if stripped and all(char == "-" for char in stripped):
                continue

            depth = self._trace_depth(line)
            parent = parents_by_depth.get(depth - 1, "")
            node_text = stripped
            node_id = self.tree_view.insert(parent, "end", text=node_text)
            parents_by_depth[depth] = node_id

            for existing_depth in list(parents_by_depth):
                if existing_depth > depth:
                    del parents_by_depth[existing_depth]

        for root_child in self.tree_view.get_children():
            self._expand_tree(root_child)

    def _set_tree_events(self, events: list[TraceEvent]) -> None:
        if self.tree_view is None:
            return

        self.tree_view.delete(*self.tree_view.get_children())
        if not events:
            self.tree_view.insert("", "end", text="No tree generated for this turn.")
            return

        parents_by_depth: dict[int, str] = {-1: ""}
        for event in events:
            if event.kind == "banner":
                node_id = self.tree_view.insert("", "end", text=f"[SEARCH] {event.text}")
                parents_by_depth = {-1: "", 0: node_id}
                continue

            parent = parents_by_depth.get(event.depth - 1, "")
            prefix = self._event_prefix(event.kind)
            node_text = f"{prefix}{event.text}"
            node_id = self.tree_view.insert(parent, "end", text=node_text)
            parents_by_depth[event.depth] = node_id

            if event.kind == "block" and event.lines:
                for detail_line in event.lines:
                    self.tree_view.insert(node_id, "end", text=detail_line)

            for existing_depth in list(parents_by_depth):
                if existing_depth > event.depth:
                    del parents_by_depth[existing_depth]

        for root_child in self.tree_view.get_children():
            self._expand_tree(root_child)

    def _event_prefix(self, kind: str) -> str:
        if kind == "node":
            return "Node | "
        if kind == "branch":
            return "Branch | "
        if kind == "block":
            return "Board | "
        if kind == "truncated":
            return "Info | "
        return ""

    def _trace_depth(self, line: str) -> int:
        leading_spaces = len(line) - len(line.lstrip(" "))
        return max(0, leading_spaces // 2)

    def _expand_tree(self, item_id: str) -> None:
        if self.tree_view is None:
            return

        self.tree_view.item(item_id, open=True)
        for child in self.tree_view.get_children(item_id):
            self._expand_tree(child)

    def _update_score_display(
        self,
        ai_selected_score: float | None = None,
        reset_ai_score: bool = False,
    ) -> None:
        human_sequences = self.board.count_sequences(HUMAN)
        computer_sequences = self.board.count_sequences(COMPUTER)
        heuristic_score = self.evaluator.evaluate(self.board)

        self.score_value.set(
            "Connect-fours: Human {human} | Computer {computer} | Heuristic(board): {heuristic}".format(
                human=human_sequences,
                computer=computer_sequences,
                heuristic=heuristic_score,
            )
        )

        if ai_selected_score is not None:
            self.ai_score_value.set(f"AI selected score: {ai_selected_score:.2f}")
        elif reset_ai_score:
            self.ai_score_value.set("AI selected score: -")

    def _on_canvas_resize(self, event) -> None:  # type: ignore[no-untyped-def]
        self.canvas_width = max(event.width, 1)
        self.canvas_height = max(event.height, 1)
        self._redraw_scene()

    def _on_canvas_motion(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self._can_preview_move():
            if self.hover_column is not None:
                self.hover_column = None
                self._redraw_scene()
            if self.canvas is not None:
                self.canvas.configure(cursor="arrow")
            return

        column = self._column_from_point(event.x, event.y)
        if column != self.hover_column:
            self.hover_column = column
            self._redraw_scene()

        if self.canvas is not None:
            self.canvas.configure(cursor="hand2" if column is not None else "arrow")

    def _on_canvas_leave(self, _event) -> None:
        if self.hover_column is not None:
            self.hover_column = None
            self._redraw_scene()
        if self.canvas is not None:
            self.canvas.configure(cursor="arrow")

    def _on_canvas_click(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self._can_preview_move():
            return

        column = self._column_from_point(event.x, event.y)
        if column is not None:
            self.handle_human_move(column)

    def _can_preview_move(self) -> bool:
        return self.game_active and not self.animating and self.current_player == HUMAN

    def _compute_layout(self) -> BoardLayout:
        canvas_width = max(self.canvas_width, 1)
        canvas_height = max(self.canvas_height, 1)
        available_width = max(canvas_width - self.board_margin * 2, 1)
        available_height = max(canvas_height - self.board_margin * 2, 1)
        cell_size = max(38, min(available_width // self.board.cols, available_height // self.board.rows))
        board_width = cell_size * self.board.cols
        board_height = cell_size * self.board.rows
        board_x = max((canvas_width - board_width) // 2, 0)
        board_y = max((canvas_height - board_height) // 2, 0)
        slot_inset = max(4, cell_size // 7)
        piece_inset = max(6, cell_size // 11)
        radius = max(14, cell_size // 5)
        return BoardLayout(
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            board_x=board_x,
            board_y=board_y,
            board_width=board_width,
            board_height=board_height,
            cell_size=cell_size,
            slot_inset=slot_inset,
            piece_inset=piece_inset,
            radius=radius,
        )

    def _redraw_scene(self) -> None:
        if self.canvas is None:
            return

        self.layout = self._compute_layout()
        layout = self.layout
        self.canvas.delete("all")
        self.canvas.configure(bg=self.colors.background)

        # The board is drawn from scratch every time so resize and animation
        # updates stay crisp and pixel-aligned.
        self.canvas.create_rectangle(
            0,
            0,
            layout.canvas_width,
            layout.canvas_height,
            fill=self.colors.background,
            outline=self.colors.background,
        )

        shadow_offset = max(8, layout.cell_size // 10)
        self._create_round_rect(
            layout.board_x + shadow_offset,
            layout.board_y + shadow_offset,
            layout.board_x + layout.board_width + shadow_offset,
            layout.board_y + layout.board_height + shadow_offset,
            layout.radius,
            fill=self.colors.board_shadow,
            outline="",
            width=0,
        )
        self._create_round_rect(
            layout.board_x,
            layout.board_y,
            layout.board_x + layout.board_width,
            layout.board_y + layout.board_height,
            layout.radius,
            fill=self.colors.board,
            outline="#0f2440",
            width=2,
        )

        self._draw_slots(layout)
        self._draw_pieces(layout)
        if self._can_preview_move() and self.hover_column is not None:
            self._draw_column_hover(layout, self.hover_column)
            self._draw_preview_piece(layout, self.hover_column)
        self._draw_winner_highlights(layout)

    def _ensure_canvas_visible(self) -> None:
        if self.scroll_canvas is None or self.canvas is None:
            return

        self.scroll_canvas.update_idletasks()
        self.scroll_canvas.yview_moveto(0.0)

    def _draw_slots(self, layout: BoardLayout) -> None:
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                x1, y1, x2, y2 = self._slot_bounds(layout, row, col)
                shadow_shift = max(2, layout.cell_size // 14)
                self.canvas.create_oval(
                    x1 + shadow_shift,
                    y1 + shadow_shift,
                    x2 + shadow_shift,
                    y2 + shadow_shift,
                    fill="#0a1726",
                    outline="",
                )
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.colors.slot,
                    outline=self.colors.slot_edge,
                    width=1,
                )

    def _draw_pieces(self, layout: BoardLayout) -> None:
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                value = self.board.grid[row][col]
                if value == 0:
                    continue
                self._draw_piece(layout, row, col, value)

    def _draw_piece(self, layout: BoardLayout, row: int, col: int, player: int) -> None:
        x1, y1, x2, y2 = self._piece_bounds(layout, row, col)
        color = self.colors.human if player == HUMAN else self.colors.computer
        glow = self.colors.human_glow if player == HUMAN else self.colors.computer_glow
        shadow_shift = max(2, layout.cell_size // 15)
        self.canvas.create_oval(
            x1 + shadow_shift,
            y1 + shadow_shift,
            x2 + shadow_shift,
            y2 + shadow_shift,
            fill="#0b1421",
            outline="",
        )
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=color,
            outline=glow,
            width=2,
        )

    def _draw_preview_piece(self, layout: BoardLayout, column: int) -> None:
        x1, y1, x2, y2 = self._preview_piece_bounds(layout, column)
        self.canvas.create_oval(
            x1 + 2,
            y1 + 2,
            x2 + 2,
            y2 + 2,
            fill="#0b1421",
            outline="",
        )
        self.canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            fill=self.colors.human,
            outline="#ffffff",
            width=2,
        )

    def _draw_column_hover(self, layout: BoardLayout, column: int) -> None:
        x1 = layout.board_x + column * layout.cell_size + 2
        x2 = layout.board_x + (column + 1) * layout.cell_size - 2
        y1 = layout.board_y + 2
        y2 = layout.board_y + layout.board_height - 2
        self._create_round_rect(
            x1,
            y1,
            x2,
            y2,
            max(10, layout.cell_size // 6),
            fill=self.colors.hover,
            outline=self.colors.hover_edge,
            width=2,
        )

    def _draw_winner_highlights(self, layout: BoardLayout) -> None:
        if self.winner_player == 0:
            return

        for sequence in self.board.winning_sequences(self.winner_player):
            for row, col in sequence:
                x1, y1, x2, y2 = self._slot_bounds(layout, row, col, inset=max(2, layout.slot_inset - 2))
                self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline=self.colors.highlight,
                    width=max(3, layout.cell_size // 16),
                )

    def _slot_bounds(self, layout: BoardLayout, row: int, col: int, inset: int | None = None) -> tuple[int, int, int, int]:
        actual_inset = layout.slot_inset if inset is None else inset
        x1 = layout.board_x + col * layout.cell_size + actual_inset
        y1 = layout.board_y + row * layout.cell_size + actual_inset
        x2 = layout.board_x + (col + 1) * layout.cell_size - actual_inset
        y2 = layout.board_y + (row + 1) * layout.cell_size - actual_inset
        return x1, y1, x2, y2

    def _piece_bounds(self, layout: BoardLayout, row: int, col: int) -> tuple[int, int, int, int]:
        x1 = layout.board_x + col * layout.cell_size + layout.piece_inset
        y1 = layout.board_y + row * layout.cell_size + layout.piece_inset
        x2 = layout.board_x + (col + 1) * layout.cell_size - layout.piece_inset
        y2 = layout.board_y + (row + 1) * layout.cell_size - layout.piece_inset
        return x1, y1, x2, y2

    def _preview_piece_bounds(self, layout: BoardLayout, column: int) -> tuple[int, int, int, int]:
        diameter_inset = layout.piece_inset
        x1 = layout.board_x + column * layout.cell_size + diameter_inset
        x2 = layout.board_x + (column + 1) * layout.cell_size - diameter_inset
        preview_top = max(layout.board_y - layout.cell_size // 2, self.board_margin // 2)
        y2 = preview_top + (x2 - x1)
        y1 = preview_top
        return x1, y1, x2, y2

    def _create_round_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        radius: int,
        *,
        fill: str,
        outline: str,
        width: int,
    ) -> int:
        radius = max(1, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            fill=fill,
            outline=outline,
            width=width,
            joinstyle="round",
        )

    def start_game(self) -> None:
        """Validate settings and start a new game session."""

        try:
            depth = int(self.depth_value.get())
        except ValueError:
            messagebox.showerror("Invalid depth", "Please enter a whole number for depth K.")
            return

        if depth < 1:
            messagebox.showerror("Invalid depth", "Depth K must be at least 1.")
            return

        self.board = Connect4Board()
        self.game_active = True
        self.current_player = HUMAN
        self.animating = False
        self.hover_column = None
        self.winner_player = 0
        self.result_value.set("")
        self.status_value.set("Game started. Human begins.")
        self.turn_value.set("Current player: Human")
        self.stats_value.set("Last move: none")
        self._set_tree_lines(["Search tree output will appear after the computer moves."])
        self._update_score_display(reset_ai_score=True)
        self._set_result_style("neutral")
        self._set_turn_badge()
        self._set_settings_enabled(False)
        self._redraw_scene()
        self._ensure_canvas_visible()

    def restart_game(self) -> None:
        """Restart with the current settings."""

        self.start_game()

    def handle_human_move(self, column: int) -> None:
        """Process a click from the human player."""

        if not self.game_active or self.animating or self.current_player != HUMAN:
            return

        if not self.board.is_valid_column(column):
            self.status_value.set(f"Column {column + 1} is full. Choose another column.")
            self.hover_column = None
            self._redraw_scene()
            return

        self.animating = True
        self.status_value.set(f"Human selected column {column + 1}.")
        self.turn_value.set("Animating human move...")
        self._set_turn_badge()
        self._animate_drop(column=column, player=HUMAN, on_complete=self._after_human_move)

    def _after_human_move(self, row: int, column: int) -> None:
        self.animating = False
        self._register_move(row=row, column=column, elapsed_ms=0.0, nodes=0, label="Human")

        if self._finish_if_board_full():
            return

        self.current_player = COMPUTER
        self.turn_value.set("Current player: Computer")
        self.status_value.set("Computer is thinking...")
        self._set_turn_badge()
        self._set_settings_enabled(False)
        self.root.after(250, self._computer_turn)

    def _computer_turn(self) -> None:
        if not self.game_active:
            return

        depth = int(self.depth_value.get())
        algorithm = self.selected_algorithm.get()
        search_board = self.board.clone()
        gui_tree_printer = TreePrinter(
            enabled=True,
            max_depth=self.tree_printer.max_depth,
            sinks=[print],
        )

        try:
            best_column, stats = self.ai.choose_move(search_board, depth, algorithm, gui_tree_printer)
        except Exception as exc:
            messagebox.showerror("AI error", str(exc))
            self.game_active = False
            self.animating = False
            self._set_settings_enabled(True)
            self._set_turn_badge()
            return

        self._set_tree_events(gui_tree_printer.events)
        self._update_score_display(ai_selected_score=stats.selected_score)

        if not self.board.is_valid_column(best_column):
            valid_columns = self.board.valid_columns()
            if not valid_columns:
                self._finish_game()
                return
            best_column = valid_columns[0]

        self.status_value.set(f"Computer chose column {best_column + 1}.")
        self.turn_value.set("Animating computer move...")
        self._set_turn_badge()
        self.animating = True
        self._animate_drop(
            column=best_column,
            player=COMPUTER,
            on_complete=lambda row, column: self._after_computer_move(row, column, stats),
        )

    def _after_computer_move(self, row: int, column: int, stats: SearchStats) -> None:
        self.animating = False
        self._register_move(
            row=row,
            column=column,
            elapsed_ms=stats.elapsed_milliseconds,
            nodes=stats.nodes_expanded,
            label=f"Computer ({stats.algorithm})",
        )

        if self._finish_if_board_full():
            return

        self.current_player = HUMAN
        self.turn_value.set("Current player: Human")
        self.status_value.set("Your move.")
        self._set_turn_badge()

    def _register_move(
        self,
        row: int,
        column: int,
        elapsed_ms: float,
        nodes: int,
        label: str,
    ) -> None:
        self.stats_value.set(
            f"Last move: {label} | column {column + 1} | row {row + 1} | time {elapsed_ms:.2f} ms | nodes {nodes}"
        )
        self._update_score_display()
        self._redraw_scene()

    def _finish_if_board_full(self) -> bool:
        if self.board.is_full():
            self._finish_game()
            return True
        return False

    def _finish_game(self) -> None:
        self.game_active = False
        self.animating = False
        self._set_settings_enabled(True)
        self._set_turn_badge()

        human_sequences = self.board.count_sequences(HUMAN)
        computer_sequences = self.board.count_sequences(COMPUTER)
        human_message = f"Human connect-fours: {human_sequences}"
        computer_message = f"Computer connect-fours: {computer_sequences}"

        if human_sequences > computer_sequences:
            winner_text = "Human wins"
            self.winner_player = HUMAN
            result_mode = "success"
        elif computer_sequences > human_sequences:
            winner_text = "Computer wins"
            self.winner_player = COMPUTER
            result_mode = "warning"
        else:
            winner_text = "Draw"
            self.winner_player = 0
            result_mode = "neutral"

        self.result_value.set(f"Final result: {human_message} | {computer_message} | {winner_text}")
        self.status_value.set("Board is full. Final evaluation complete.")
        self.turn_value.set("Game over")
        self._set_turn_badge()
        self._set_result_style(result_mode)
        self._update_score_display()
        self._redraw_scene()

    def _animate_drop(self, column: int, player: int, on_complete: Callable[[int, int], None]) -> None:
        layout = self.layout
        row = self._find_drop_row(column)
        if row is None or self.canvas is None:
            self.animating = False
            self._set_settings_enabled(True)
            self.turn_value.set("Current player: Human")
            self._set_turn_badge()
            self._redraw_scene()
            return

        piece_color = self.colors.human if player == HUMAN else self.colors.computer
        glow = self.colors.human_glow if player == HUMAN else self.colors.computer_glow
        size = max(24, layout.cell_size - 2 * layout.piece_inset)
        x1 = layout.board_x + column * layout.cell_size + layout.piece_inset
        x2 = x1 + size
        start_y = layout.board_y - layout.cell_size
        end_y = layout.board_y + row * layout.cell_size + layout.piece_inset

        shadow = self.canvas.create_oval(
            x1 + 5,
            start_y + 5,
            x2 + 5,
            start_y + size + 5,
            fill="#0b1421",
            outline="",
        )
        disc = self.canvas.create_oval(
            x1,
            start_y,
            x2,
            start_y + size,
            fill=piece_color,
            outline=glow,
            width=2,
        )

        self.hover_column = None
        self.canvas.configure(cursor="arrow")

        current_step = 0

        def step() -> None:
            nonlocal current_step
            current_step += 1
            progress = current_step / self.drop_animation_steps
            eased = 1 - (1 - progress) ** 3
            top = start_y + (end_y - start_y) * eased
            bottom = top + size
            self.canvas.coords(shadow, x1 + 5, top + 5, x2 + 5, bottom + 5)
            self.canvas.coords(disc, x1, top, x2, bottom)

            if current_step < self.drop_animation_steps:
                self.root.after(self.drop_animation_interval, step)
            else:
                self.canvas.delete(shadow)
                self.canvas.delete(disc)
                self.board.drop_piece(column, player)
                on_complete(row, column)

        step()

    def _find_drop_row(self, column: int) -> int | None:
        for row in range(self.board.rows - 1, -1, -1):
            if self.board.grid[row][column] == 0:
                return row
        return None

    def _column_from_point(self, x: int, y: int) -> int | None:
        layout = self.layout
        if layout.board_width <= 0 or layout.board_height <= 0:
            return None

        if not (layout.board_x <= x < layout.board_x + layout.board_width):
            return None
        if not (layout.board_y <= y < layout.board_y + layout.board_height):
            return None

        column = (x - layout.board_x) // layout.cell_size
        if 0 <= column < self.board.cols:
            return int(column)
        return None


__all__ = ["Connect4App", "GameColors"]
