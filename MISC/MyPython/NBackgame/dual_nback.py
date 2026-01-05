"""
Dual N-Back Game
A cognitive training game that tests working memory for both position and visual stimuli.
Author: Generated using Calude Opus 4.5 for HasanSiddiki
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class GameConfig:
    """Stores all game configuration settings"""
    def __init__(self):
        self.n_level = 2  # N-back level
        self.grid_rows = 3
        self.grid_cols = 3
        self.round_duration = 3000  # milliseconds
        self.total_rounds = 20
        self.string_length = 2
        self.string_type = "letters"  # letters, numbers, combination
        self.letter_case = "capital"  # capital, lowercase, combination
    
    def get_char_pool(self):
        """Get the character pool based on configuration"""
        if self.string_type == "letters":
            if self.letter_case == "capital":
                return string.ascii_uppercase
            elif self.letter_case == "lowercase":
                return string.ascii_lowercase
            else:  # combination
                return string.ascii_letters
        elif self.string_type == "numbers":
            return string.digits
        else:  # combination of letters and numbers
            if self.letter_case == "capital":
                return string.ascii_uppercase + string.digits
            elif self.letter_case == "lowercase":
                return string.ascii_lowercase + string.digits
            else:  # full combination
                return string.ascii_letters + string.digits
        
    def generate_string(self):
        """Generate a random string based on configuration"""
        chars = self.get_char_pool()
        return ''.join(random.choice(chars) for _ in range(self.string_length))


class StimulusGenerator:
    """
    Advanced stimulus generator using uniform distribution with enforced 
    constraints and adaptive tuning for balanced, engaging gameplay.
    """
    
    def __init__(self, config):
        self.config = config
        
        # Target match rates (percentage of rounds that should have matches)
        self.target_position_match_rate = 0.25  # 25% position matches
        self.target_string_match_rate = 0.25    # 25% string matches
        self.target_dual_match_rate = 0.10      # 10% dual matches (both)
        
        # Adaptive tuning parameters
        self.position_matches_count = 0
        self.string_matches_count = 0
        self.dual_matches_count = 0
        self.matchable_rounds = 0  # Rounds where matching was possible
        
        # Streak prevention (avoid too many matches/non-matches in a row)
        self.position_match_streak = 0
        self.string_match_streak = 0
        self.no_match_streak = 0
        self.max_streak = 4  # Maximum consecutive matches or non-matches
        
        # History for n-back lookups
        self.history = []
        
        # Lure settings (near-matches to increase difficulty)
        self.lure_probability = 0.15  # 15% chance of generating lures
    
    def reset(self):
        """Reset generator state for new game"""
        self.position_matches_count = 0
        self.string_matches_count = 0
        self.dual_matches_count = 0
        self.matchable_rounds = 0
        self.position_match_streak = 0
        self.string_match_streak = 0
        self.no_match_streak = 0
        self.history = []
    
    def get_current_match_rates(self):
        """Calculate current match rates"""
        if self.matchable_rounds == 0:
            return 0, 0, 0
        
        pos_rate = self.position_matches_count / self.matchable_rounds
        str_rate = self.string_matches_count / self.matchable_rounds
        dual_rate = self.dual_matches_count / self.matchable_rounds
        return pos_rate, str_rate, dual_rate
    
    def calculate_adaptive_probability(self, current_rate, target_rate, base_prob=0.25):
        """
        Calculate adaptive probability based on how far we are from target.
        Uses sigmoid-like adjustment for smooth transitions.
        """
        if self.matchable_rounds < 3:
            return base_prob  # Not enough data, use base probability
        
        # Calculate deviation from target
        deviation = target_rate - current_rate
        
        # Adjust probability: increase if below target, decrease if above
        # Scale factor controls how aggressively we adapt
        scale_factor = 2.0
        adjustment = deviation * scale_factor
        
        # Clamp probability between reasonable bounds
        adjusted_prob = base_prob + adjustment
        return max(0.1, min(0.5, adjusted_prob))
    
    def should_force_match(self, match_type):
        """Determine if we should force a match based on streaks and rates"""
        # Prevent excessive non-match streaks
        if self.no_match_streak >= self.max_streak:
            return random.random() < 0.6  # 60% chance to force a match
        
        # Prevent excessive match streaks
        if match_type == "position" and self.position_match_streak >= self.max_streak:
            return False
        if match_type == "string" and self.string_match_streak >= self.max_streak:
            return False
        
        return None  # No forcing needed
    
    def generate_position_lure(self, n_back_position):
        """Generate a position that's close to but not matching n-back"""
        if n_back_position is None:
            return self.generate_random_position()
        
        row, col = n_back_position
        
        # Generate adjacent position (lure)
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        random.shuffle(offsets)
        
        for dr, dc in offsets:
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < self.config.grid_rows and 0 <= new_col < self.config.grid_cols:
                return (new_row, new_col)
        
        return self.generate_random_position()
    
    def generate_string_lure(self, n_back_string):
        """Generate a string that's similar to but not matching n-back"""
        if n_back_string is None or len(n_back_string) == 0:
            return self.config.generate_string()
        
        chars = self.config.get_char_pool()
        result = list(n_back_string)
        
        # Change exactly one character (makes it a near-miss)
        change_idx = random.randint(0, len(result) - 1)
        original_char = result[change_idx]
        
        # Pick a different character
        available = [c for c in chars if c != original_char]
        if available:
            result[change_idx] = random.choice(available)
        
        return ''.join(result)
    
    def generate_random_position(self):
        """Generate a uniformly random position"""
        return (
            random.randint(0, self.config.grid_rows - 1),
            random.randint(0, self.config.grid_cols - 1)
        )
    
    def generate_stimulus(self):
        """
        Generate the next position and string stimulus using adaptive algorithm.
        Returns: (position, string, metadata)
        """
        n = self.config.n_level
        
        # Check if we can do n-back matching yet
        can_match = len(self.history) >= n
        
        if not can_match:
            # Not enough history - generate purely random
            position = self.generate_random_position()
            stimulus_string = self.config.generate_string()
            self.history.append((position, stimulus_string))
            return position, stimulus_string, {"type": "random", "can_match": False}
        
        self.matchable_rounds += 1
        n_back = self.history[-n]
        n_back_position, n_back_string = n_back
        
        # Get current match rates for adaptive tuning
        pos_rate, str_rate, dual_rate = self.get_current_match_rates()
        
        # Calculate adaptive probabilities
        pos_match_prob = self.calculate_adaptive_probability(
            pos_rate, self.target_position_match_rate, 0.25
        )
        str_match_prob = self.calculate_adaptive_probability(
            str_rate, self.target_string_match_rate, 0.25
        )
        
        # Determine what kind of stimulus to generate
        roll_pos = random.random()
        roll_str = random.random()
        roll_lure = random.random()
        
        # Check for forced decisions based on streaks
        force_pos = self.should_force_match("position")
        force_str = self.should_force_match("string")
        
        # Decide position match
        if force_pos is not None:
            pos_match = force_pos
        else:
            pos_match = roll_pos < pos_match_prob
        
        # Decide string match
        if force_str is not None:
            str_match = force_str
        else:
            str_match = roll_str < str_match_prob
        
        # Generate position
        if pos_match:
            position = n_back_position
            self.position_matches_count += 1
            self.position_match_streak += 1
        elif roll_lure < self.lure_probability:
            position = self.generate_position_lure(n_back_position)
            self.position_match_streak = 0
        else:
            # Generate non-matching position
            position = self.generate_random_position()
            # Ensure it doesn't accidentally match
            attempts = 0
            while position == n_back_position and attempts < 10:
                position = self.generate_random_position()
                attempts += 1
            self.position_match_streak = 0
        
        # Generate string
        if str_match:
            stimulus_string = n_back_string
            self.string_matches_count += 1
            self.string_match_streak += 1
        elif roll_lure < self.lure_probability:
            stimulus_string = self.generate_string_lure(n_back_string)
            self.string_match_streak = 0
        else:
            # Generate non-matching string
            stimulus_string = self.config.generate_string()
            # Ensure it doesn't accidentally match
            attempts = 0
            while stimulus_string == n_back_string and attempts < 10:
                stimulus_string = self.config.generate_string()
                attempts += 1
            self.string_match_streak = 0
        
        # Track dual matches
        if pos_match and str_match:
            self.dual_matches_count += 1
        
        # Track no-match streaks
        if not pos_match and not str_match:
            self.no_match_streak += 1
        else:
            self.no_match_streak = 0
        
        # Store in history
        self.history.append((position, stimulus_string))
        
        # Build metadata
        metadata = {
            "type": "adaptive",
            "can_match": True,
            "pos_match": pos_match,
            "str_match": str_match,
            "pos_prob": round(pos_match_prob, 2),
            "str_prob": round(str_match_prob, 2),
            "is_lure_pos": not pos_match and roll_lure < self.lure_probability,
            "is_lure_str": not str_match and roll_lure < self.lure_probability
        }
        
        return position, stimulus_string, metadata


class GameStats:
    """Tracks and manages game statistics"""
    def __init__(self):
        self.position_hits = 0
        self.position_misses = 0
        self.position_false_alarms = 0
        self.string_hits = 0
        self.string_misses = 0
        self.string_false_alarms = 0
        self.total_rounds_played = 0
        self.stats_file = os.path.join(os.path.dirname(__file__), "game_stats.json")
        
    def calculate_score(self):
        """Calculate overall game score"""
        position_correct = self.position_hits
        string_correct = self.string_hits
        
        position_attempts = self.position_hits + self.position_misses + self.position_false_alarms
        string_attempts = self.string_hits + self.string_misses + self.string_false_alarms
        
        position_accuracy = (position_correct / max(1, position_attempts)) * 100
        string_accuracy = (string_correct / max(1, string_attempts)) * 100
        
        # Combined score with penalty for false alarms
        penalty = (self.position_false_alarms + self.string_false_alarms) * 5
        total_score = max(0, (position_correct + string_correct) * 10 - penalty)
        
        return {
            "position_accuracy": round(position_accuracy, 1),
            "string_accuracy": round(string_accuracy, 1),
            "total_score": int(total_score),
            "position_hits": self.position_hits,
            "string_hits": self.string_hits,
            "position_misses": self.position_misses,
            "string_misses": self.string_misses,
            "position_false_alarms": self.position_false_alarms,
            "string_false_alarms": self.string_false_alarms
        }
    
    def reset(self):
        """Reset stats for new game"""
        self.position_hits = 0
        self.position_misses = 0
        self.position_false_alarms = 0
        self.string_hits = 0
        self.string_misses = 0
        self.string_false_alarms = 0
        self.total_rounds_played = 0
    
    def save_to_file(self, config, score_data):
        """Save game results to JSON file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    all_stats = json.load(f)
            else:
                all_stats = {"games": [], "high_scores": {}}
        except:
            all_stats = {"games": [], "high_scores": {}}
        
        game_record = {
            "date": datetime.now().isoformat(),
            "n_level": config.n_level,
            "grid_size": f"{config.grid_rows}x{config.grid_cols}",
            "rounds": config.total_rounds,
            "score": score_data["total_score"],
            "position_accuracy": score_data["position_accuracy"],
            "string_accuracy": score_data["string_accuracy"]
        }
        
        all_stats["games"].append(game_record)
        
        # Update high score
        level_key = f"level_{config.n_level}"
        if level_key not in all_stats["high_scores"]:
            all_stats["high_scores"][level_key] = score_data["total_score"]
        else:
            all_stats["high_scores"][level_key] = max(
                all_stats["high_scores"][level_key], 
                score_data["total_score"]
            )
        
        with open(self.stats_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
        
        return all_stats["high_scores"].get(level_key, 0)


class DualNBackGame:
    """Main game class"""
    
    # Green theme colors
    COLORS = {
        "bg_dark": "#0a1f0a",
        "bg_medium": "#143314",
        "bg_light": "#1e4d1e",
        "accent": "#2ecc71",
        "accent_light": "#58d68d",
        "accent_dark": "#27ae60",
        "text": "#ecf0f1",
        "text_dim": "#95a5a6",
        "grid_empty": "#1a3a1a",
        "grid_active": "#2ecc71",
        "grid_border": "#27ae60",
        "button_hover": "#34e079",
        "error": "#e74c3c",
        "warning": "#f39c12",
        "success": "#2ecc71"
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Dual N-Back - Cognitive Training Game")
        self.root.configure(bg=self.COLORS["bg_dark"])
        self.root.geometry("900x750")
        self.root.minsize(800, 700)
        
        # Game state
        self.config = GameConfig()
        self.stats = GameStats()
        self.stimulus_generator = None  # Created when game starts
        self.is_playing = False
        self.is_paused = False
        self.current_round = 0
        self.history = []  # List of (position, string) tuples
        self.current_position = None
        self.current_string = None
        self.position_pressed = False
        self.string_pressed = False
        self.timer_id = None
        
        # Grid cells
        self.grid_cells = []
        
        # Set up styles
        self.setup_styles()
        
        # Show settings screen
        self.show_settings_screen()
        
        # Bind keyboard shortcuts
        self.root.bind('<a>', lambda e: self.check_position())
        self.root.bind('<A>', lambda e: self.check_position())
        self.root.bind('<l>', lambda e: self.check_string())
        self.root.bind('<L>', lambda e: self.check_string())
        self.root.bind('<space>', lambda e: self.toggle_pause())
        self.root.bind('<Escape>', lambda e: self.end_game())
    
    def setup_styles(self):
        """Configure ttk styles for green theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure("Green.TFrame", background=self.COLORS["bg_dark"])
        style.configure("GreenLight.TFrame", background=self.COLORS["bg_medium"])
        
        style.configure("Green.TLabel", 
                       background=self.COLORS["bg_dark"],
                       foreground=self.COLORS["text"],
                       font=("Segoe UI", 11))
        
        style.configure("GreenTitle.TLabel",
                       background=self.COLORS["bg_dark"],
                       foreground=self.COLORS["accent"],
                       font=("Segoe UI", 24, "bold"))
        
        style.configure("GreenSubtitle.TLabel",
                       background=self.COLORS["bg_dark"],
                       foreground=self.COLORS["text_dim"],
                       font=("Segoe UI", 10))
        
        style.configure("GreenBig.TLabel",
                       background=self.COLORS["bg_dark"],
                       foreground=self.COLORS["accent_light"],
                       font=("Segoe UI", 16, "bold"))
        
        style.configure("Green.TButton",
                       background=self.COLORS["accent"],
                       foreground=self.COLORS["bg_dark"],
                       font=("Segoe UI", 11, "bold"),
                       padding=(20, 10))
        
        style.map("Green.TButton",
                 background=[('active', self.COLORS["button_hover"]),
                            ('pressed', self.COLORS["accent_dark"])])
        
        style.configure("GreenSecondary.TButton",
                       background=self.COLORS["bg_light"],
                       foreground=self.COLORS["text"],
                       font=("Segoe UI", 10),
                       padding=(15, 8))
        
        style.map("GreenSecondary.TButton",
                 background=[('active', self.COLORS["bg_medium"])])
        
        # Combobox styling with green theme
        style.configure("Green.TCombobox",
                       fieldbackground=self.COLORS["bg_light"],
                       background=self.COLORS["accent"],
                       foreground=self.COLORS["text"],
                       arrowcolor=self.COLORS["accent"],
                       bordercolor=self.COLORS["accent"],
                       lightcolor=self.COLORS["bg_light"],
                       darkcolor=self.COLORS["bg_dark"])
        
        style.map("Green.TCombobox",
                 fieldbackground=[('readonly', self.COLORS["bg_light"]),
                                  ('disabled', self.COLORS["bg_dark"])],
                 foreground=[('readonly', self.COLORS["text"]),
                            ('disabled', self.COLORS["text_dim"])],
                 background=[('active', self.COLORS["accent"]),
                            ('pressed', self.COLORS["accent_dark"])],
                 arrowcolor=[('disabled', self.COLORS["text_dim"])])
        
        # Configure the dropdown listbox colors using option_add
        self.root.option_add('*TCombobox*Listbox.background', self.COLORS["bg_light"])
        self.root.option_add('*TCombobox*Listbox.foreground', self.COLORS["text"])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.COLORS["accent"])
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.COLORS["bg_dark"])
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))
        
        # Spinbox styling with green theme
        style.configure("Green.TSpinbox",
                       fieldbackground=self.COLORS["bg_light"],
                       background=self.COLORS["accent"],
                       foreground=self.COLORS["text"],
                       arrowcolor=self.COLORS["accent"],
                       bordercolor=self.COLORS["accent"])
        
        style.map("Green.TSpinbox",
                 fieldbackground=[('readonly', self.COLORS["bg_light"])],
                 foreground=[('readonly', self.COLORS["text"])],
                 arrowcolor=[('disabled', self.COLORS["text_dim"])])
        
        style.configure("Green.TLabelframe",
                       background=self.COLORS["bg_dark"],
                       foreground=self.COLORS["accent"])
        
        style.configure("Green.TLabelframe.Label",
                       background=self.COLORS["bg_dark"],
                       foreground=self.COLORS["accent"],
                       font=("Segoe UI", 11, "bold"))
    
    def clear_screen(self):
        """Remove all widgets from root"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_settings_screen(self):
        """Display the pre-game settings screen"""
        self.clear_screen()
        self.is_playing = False
        
        # Main container
        main_frame = ttk.Frame(self.root, style="Green.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Title
        title_label = ttk.Label(main_frame, text="🧠 DUAL N-BACK", style="GreenTitle.TLabel")
        title_label.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, 
                            text="Cognitive Training Game - Train Your Working Memory",
                            style="GreenSubtitle.TLabel")
        subtitle.pack(pady=(0, 30))
        
        # Settings container
        settings_frame = ttk.Frame(main_frame, style="Green.TFrame")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Core settings
        left_frame = ttk.LabelFrame(settings_frame, text=" Core Settings ", 
                                    style="Green.TLabelframe", padding=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Use grid layout for proper alignment
        row = 0
        
        # N-Level
        ttk.Label(left_frame, text="N-Back Level:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.n_level_var = tk.StringVar(value=str(self.config.n_level))
        ttk.Spinbox(left_frame, from_=1, to=9, width=8, textvariable=self.n_level_var, style="Green.TSpinbox").grid(
            row=row, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(left_frame, text="(Steps back to remember)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        row += 1
        
        # Grid Rows
        ttk.Label(left_frame, text="Grid Rows:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.grid_rows_var = tk.StringVar(value=str(self.config.grid_rows))
        ttk.Spinbox(left_frame, from_=2, to=6, width=8, textvariable=self.grid_rows_var, style="Green.TSpinbox").grid(
            row=row, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(left_frame, text="(Rows in grid)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        row += 1
        
        # Grid Columns
        ttk.Label(left_frame, text="Grid Columns:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.grid_cols_var = tk.StringVar(value=str(self.config.grid_cols))
        ttk.Spinbox(left_frame, from_=2, to=6, width=8, textvariable=self.grid_cols_var, style="Green.TSpinbox").grid(
            row=row, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(left_frame, text="(Columns in grid)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        row += 1
        
        # Total Rounds
        ttk.Label(left_frame, text="Total Rounds:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.total_rounds_var = tk.StringVar(value=str(self.config.total_rounds))
        ttk.Spinbox(left_frame, from_=10, to=100, width=8, textvariable=self.total_rounds_var, style="Green.TSpinbox").grid(
            row=row, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(left_frame, text="(Stimuli count)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        row += 1
        
        # Round Duration
        ttk.Label(left_frame, text="Round Duration:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        duration_frame = ttk.Frame(left_frame, style="Green.TFrame")
        duration_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        self.round_duration_var = tk.StringVar(value=str(self.config.round_duration // 1000))
        ttk.Spinbox(duration_frame, from_=1, to=10, width=5, textvariable=self.round_duration_var, style="Green.TSpinbox").pack(side=tk.LEFT)
        ttk.Label(duration_frame, text=" sec", style="Green.TLabel").pack(side=tk.LEFT)
        ttk.Label(left_frame, text="(Time per stimulus)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        
        # Right column - String settings
        right_frame = ttk.LabelFrame(settings_frame, text=" String Settings ",
                                     style="Green.TLabelframe", padding=20)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        row = 0
        
        # String Length
        ttk.Label(right_frame, text="String Length:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.string_length_var = tk.StringVar(value=str(self.config.string_length))
        ttk.Spinbox(right_frame, from_=1, to=6, width=8, textvariable=self.string_length_var, style="Green.TSpinbox").grid(
            row=row, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(right_frame, text="(Characters per string)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        row += 1
        
        # String Type
        ttk.Label(right_frame, text="String Type:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.string_type_var = tk.StringVar(value=self.config.string_type)
        string_type_combo = ttk.Combobox(right_frame, textvariable=self.string_type_var,
                                         values=["letters", "numbers", "combination"],
                                         state="readonly", width=12, style="Green.TCombobox")
        string_type_combo.grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        string_type_combo.bind("<<ComboboxSelected>>", self.on_string_type_change)
        ttk.Label(right_frame, text="(Character type)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        row += 1
        
        # Letter Case
        ttk.Label(right_frame, text="Letter Case:", style="Green.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=8)
        self.letter_case_var = tk.StringVar(value=self.config.letter_case)
        self.letter_case_combo = ttk.Combobox(right_frame, textvariable=self.letter_case_var,
                                              values=["capital", "lowercase", "combination"],
                                              state="readonly", width=12, style="Green.TCombobox")
        self.letter_case_combo.grid(row=row, column=1, sticky=tk.W, padx=10, pady=8)
        ttk.Label(right_frame, text="(Case style)", style="GreenSubtitle.TLabel").grid(
            row=row, column=2, sticky=tk.W, pady=8)
        
        # Update letter case state
        self.on_string_type_change(None)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text=" How to Play ",
                                            style="Green.TLabelframe", padding=15)
        instructions_frame.pack(fill=tk.X, pady=20)
        
        instructions = """
• Watch for POSITION matches: Press 'A' when the current position matches N rounds ago
• Watch for STRING matches: Press 'L' when the current string matches N rounds ago
• Both can match simultaneously - be ready for dual matches!
• Press SPACE to pause/resume, ESC to end the game
• Score is based on correct identifications minus false alarms
        """
        
        inst_label = ttk.Label(instructions_frame, text=instructions.strip(),
                              style="Green.TLabel", justify=tk.LEFT)
        inst_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style="Green.TFrame")
        button_frame.pack(fill=tk.X, pady=20)
        
        # View stats button
        stats_btn = ttk.Button(button_frame, text="📊 View Statistics",
                              style="GreenSecondary.TButton",
                              command=self.show_statistics)
        stats_btn.pack(side=tk.LEFT)
        
        # Start button
        start_btn = ttk.Button(button_frame, text="▶ START GAME",
                              style="Green.TButton",
                              command=self.start_game)
        start_btn.pack(side=tk.RIGHT)
        
        # Quick start with presets
        preset_frame = ttk.Frame(main_frame, style="Green.TFrame")
        preset_frame.pack(fill=tk.X)
        
        ttk.Label(preset_frame, text="Quick Start: ", style="Green.TLabel").pack(side=tk.LEFT)
        
        for name, n, rounds in [("Easy (2-Back)", 2, 20), ("Medium (3-Back)", 3, 25), ("Hard (4-Back)", 4, 30)]:
            btn = ttk.Button(preset_frame, text=name, style="GreenSecondary.TButton",
                            command=lambda n=n, r=rounds: self.apply_preset(n, r))
            btn.pack(side=tk.LEFT, padx=5)
    
    def on_string_type_change(self, event):
        """Handle string type change"""
        if self.string_type_var.get() == "numbers":
            self.letter_case_combo.configure(state="disabled")
        else:
            self.letter_case_combo.configure(state="readonly")
    
    def apply_preset(self, n_level, rounds):
        """Apply a quick-start preset"""
        self.n_level_var.set(str(n_level))
        self.total_rounds_var.set(str(rounds))
    
    def apply_settings(self):
        """Apply all settings from UI to config"""
        try:
            self.config.n_level = int(self.n_level_var.get())
            self.config.grid_rows = int(self.grid_rows_var.get())
            self.config.grid_cols = int(self.grid_cols_var.get())
            self.config.total_rounds = int(self.total_rounds_var.get())
            self.config.round_duration = int(self.round_duration_var.get()) * 1000
            self.config.string_length = int(self.string_length_var.get())
            self.config.string_type = self.string_type_var.get()
            self.config.letter_case = self.letter_case_var.get()
            return True
        except ValueError as e:
            messagebox.showerror("Invalid Settings", f"Please check your settings: {e}")
            return False
    
    def start_game(self):
        """Initialize and start the game"""
        if not self.apply_settings():
            return
        
        # Reset game state
        self.stats.reset()
        self.history = []
        self.current_round = 0
        self.is_playing = True
        self.is_paused = False
        
        # Initialize the adaptive stimulus generator
        self.stimulus_generator = StimulusGenerator(self.config)
        
        # Show game screen
        self.show_game_screen()
        
        # Start the game loop
        self.next_round()
    
    def show_game_screen(self):
        """Display the main game screen"""
        self.clear_screen()
        
        # Main container
        main_frame = ttk.Frame(self.root, style="Green.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top bar - info and controls
        top_bar = ttk.Frame(main_frame, style="Green.TFrame")
        top_bar.pack(fill=tk.X, pady=(0, 20))
        
        # Level info
        level_frame = ttk.Frame(top_bar, style="Green.TFrame")
        level_frame.pack(side=tk.LEFT)
        
        ttk.Label(level_frame, text=f"Level: {self.config.n_level}-Back",
                 style="GreenBig.TLabel").pack(side=tk.LEFT)
        
        # Round counter
        self.round_label = ttk.Label(top_bar, 
                                     text=f"Round: 0 / {self.config.total_rounds}",
                                     style="GreenBig.TLabel")
        self.round_label.pack(side=tk.LEFT, padx=50)
        
        # Score display
        self.score_label = ttk.Label(top_bar, text="Score: 0",
                                     style="GreenBig.TLabel")
        self.score_label.pack(side=tk.RIGHT)
        
        # Controls
        controls_frame = ttk.Frame(top_bar, style="Green.TFrame")
        controls_frame.pack(side=tk.RIGHT, padx=20)
        
        self.pause_btn = ttk.Button(controls_frame, text="⏸ Pause",
                                    style="GreenSecondary.TButton",
                                    command=self.toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="⏹ End",
                  style="GreenSecondary.TButton",
                  command=self.end_game).pack(side=tk.LEFT)
        
        # Game area container
        game_area = ttk.Frame(main_frame, style="Green.TFrame")
        game_area.pack(fill=tk.BOTH, expand=True)
        
        # Grid frame
        grid_container = ttk.Frame(game_area, style="Green.TFrame")
        grid_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Calculate cell size
        cell_size = min(80, 400 // max(self.config.grid_rows, self.config.grid_cols))
        
        # Create grid canvas
        grid_width = self.config.grid_cols * cell_size + 10
        grid_height = self.config.grid_rows * cell_size + 10
        
        self.grid_canvas = tk.Canvas(grid_container, 
                                     width=grid_width, height=grid_height,
                                     bg=self.COLORS["bg_dark"],
                                     highlightthickness=0)
        self.grid_canvas.pack(anchor=tk.CENTER, pady=20)
        
        # Draw grid cells
        self.grid_cells = []
        for row in range(self.config.grid_rows):
            row_cells = []
            for col in range(self.config.grid_cols):
                x1 = col * cell_size + 5
                y1 = row * cell_size + 5
                x2 = x1 + cell_size - 2
                y2 = y1 + cell_size - 2
                
                cell = self.grid_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.COLORS["grid_empty"],
                    outline=self.COLORS["grid_border"],
                    width=2
                )
                row_cells.append(cell)
            self.grid_cells.append(row_cells)
        
        # String display
        self.string_display = ttk.Label(grid_container, text="---",
                                        style="GreenTitle.TLabel",
                                        font=("Consolas", 36, "bold"))
        self.string_display.pack(pady=20)
        
        # Status/feedback area
        self.feedback_label = ttk.Label(grid_container, text="Get Ready...",
                                        style="Green.TLabel",
                                        font=("Segoe UI", 14))
        self.feedback_label.pack(pady=10)
        
        # Right panel - stats and buttons
        right_panel = ttk.Frame(game_area, style="GreenLight.TFrame", padding=20)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        
        # Live stats
        ttk.Label(right_panel, text="Live Stats", style="GreenBig.TLabel").pack(pady=(0, 15))
        
        stats_grid = ttk.Frame(right_panel, style="GreenLight.TFrame")
        stats_grid.pack(fill=tk.X)
        
        # Position stats
        ttk.Label(stats_grid, text="Position", style="Green.TLabel",
                 background=self.COLORS["bg_medium"]).grid(row=0, column=0, sticky=tk.W)
        self.pos_hits_label = ttk.Label(stats_grid, text="Hits: 0", style="Green.TLabel",
                                        background=self.COLORS["bg_medium"])
        self.pos_hits_label.grid(row=1, column=0, sticky=tk.W)
        self.pos_miss_label = ttk.Label(stats_grid, text="Miss: 0", style="Green.TLabel",
                                        background=self.COLORS["bg_medium"])
        self.pos_miss_label.grid(row=2, column=0, sticky=tk.W)
        
        ttk.Label(stats_grid, text="   ", style="Green.TLabel",
                 background=self.COLORS["bg_medium"]).grid(row=0, column=1)
        
        # String stats
        ttk.Label(stats_grid, text="String", style="Green.TLabel",
                 background=self.COLORS["bg_medium"]).grid(row=0, column=2, sticky=tk.W)
        self.str_hits_label = ttk.Label(stats_grid, text="Hits: 0", style="Green.TLabel",
                                        background=self.COLORS["bg_medium"])
        self.str_hits_label.grid(row=1, column=2, sticky=tk.W)
        self.str_miss_label = ttk.Label(stats_grid, text="Miss: 0", style="Green.TLabel",
                                        background=self.COLORS["bg_medium"])
        self.str_miss_label.grid(row=2, column=2, sticky=tk.W)
        
        # Separator
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Response buttons
        ttk.Label(right_panel, text="Response Buttons", style="Green.TLabel",
                 background=self.COLORS["bg_medium"]).pack(pady=(0, 10))
        
        # Position match button
        self.pos_button = tk.Button(right_panel, text="Position Match\n[A]",
                                    bg=self.COLORS["bg_light"],
                                    fg=self.COLORS["text"],
                                    activebackground=self.COLORS["accent"],
                                    font=("Segoe UI", 12, "bold"),
                                    width=15, height=3,
                                    command=self.check_position)
        self.pos_button.pack(pady=10)
        
        # String match button
        self.str_button = tk.Button(right_panel, text="String Match\n[L]",
                                    bg=self.COLORS["bg_light"],
                                    fg=self.COLORS["text"],
                                    activebackground=self.COLORS["accent"],
                                    font=("Segoe UI", 12, "bold"),
                                    width=15, height=3,
                                    command=self.check_string)
        self.str_button.pack(pady=10)
        
        # Instructions reminder
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        reminder = ttk.Label(right_panel, 
                            text="Press when current\nmatches N steps ago",
                            style="GreenSubtitle.TLabel",
                            background=self.COLORS["bg_medium"],
                            justify=tk.CENTER)
        reminder.pack()
    
    def next_round(self):
        """Execute the next round of the game"""
        if not self.is_playing or self.is_paused:
            return
        
        self.current_round += 1
        
        if self.current_round > self.config.total_rounds:
            self.end_game()
            return
        
        # Check for missed matches from previous round
        if len(self.history) >= self.config.n_level:
            n_back = self.history[-(self.config.n_level)]
            
            if not self.position_pressed and self.current_position == n_back[0]:
                self.stats.position_misses += 1
            
            if not self.string_pressed and self.current_string == n_back[1]:
                self.stats.string_misses += 1
        
        # Reset button states
        self.position_pressed = False
        self.string_pressed = False
        self.pos_button.configure(bg=self.COLORS["bg_light"])
        self.str_button.configure(bg=self.COLORS["bg_light"])
        
        # Clear previous cell highlight
        if self.current_position is not None:
            row, col = self.current_position
            self.grid_canvas.itemconfig(self.grid_cells[row][col], 
                                        fill=self.COLORS["grid_empty"])
        
        # Generate new position and string using adaptive stimulus generator
        self.current_position, self.current_string, metadata = self.stimulus_generator.generate_stimulus()
        new_row, new_col = self.current_position
        
        # Sync history with generator's history
        self.history = self.stimulus_generator.history.copy()
        
        # Update display
        self.grid_canvas.itemconfig(self.grid_cells[new_row][new_col],
                                   fill=self.COLORS["grid_active"])
        self.string_display.configure(text=self.current_string)
        
        # Update round counter
        self.round_label.configure(text=f"Round: {self.current_round} / {self.config.total_rounds}")
        
        # Update score display
        score_data = self.stats.calculate_score()
        self.score_label.configure(text=f"Score: {score_data['total_score']}")
        
        # Clear feedback when match checking is possible
        if metadata.get("can_match", False):
            self.feedback_label.configure(text="", foreground=self.COLORS["text"])
        else:
            self.feedback_label.configure(
                text=f"Watch and remember... ({self.config.n_level - len(self.history)} more)",
                foreground=self.COLORS["text_dim"]
            )
        
        # Schedule next round
        self.timer_id = self.root.after(self.config.round_duration, self.next_round)
    
    def check_position(self):
        """Handle position match button press"""
        if not self.is_playing or self.is_paused or self.position_pressed:
            return
        
        if len(self.history) < self.config.n_level + 1:
            self.show_feedback("Too early!", self.COLORS["warning"])
            return
        
        self.position_pressed = True
        n_back = self.history[-(self.config.n_level + 1)]
        
        if self.current_position == n_back[0]:
            self.stats.position_hits += 1
            self.pos_button.configure(bg=self.COLORS["success"])
            self.show_feedback("Position ✓", self.COLORS["success"])
        else:
            self.stats.position_false_alarms += 1
            self.pos_button.configure(bg=self.COLORS["error"])
            self.show_feedback("Position ✗", self.COLORS["error"])
        
        self.update_live_stats()
    
    def check_string(self):
        """Handle string match button press"""
        if not self.is_playing or self.is_paused or self.string_pressed:
            return
        
        if len(self.history) < self.config.n_level + 1:
            self.show_feedback("Too early!", self.COLORS["warning"])
            return
        
        self.string_pressed = True
        n_back = self.history[-(self.config.n_level + 1)]
        
        if self.current_string == n_back[1]:
            self.stats.string_hits += 1
            self.str_button.configure(bg=self.COLORS["success"])
            self.show_feedback("String ✓", self.COLORS["success"])
        else:
            self.stats.string_false_alarms += 1
            self.str_button.configure(bg=self.COLORS["error"])
            self.show_feedback("String ✗", self.COLORS["error"])
        
        self.update_live_stats()
    
    def show_feedback(self, message, color):
        """Show temporary feedback message"""
        self.feedback_label.configure(text=message, foreground=color)
    
    def update_live_stats(self):
        """Update the live statistics display"""
        self.pos_hits_label.configure(text=f"Hits: {self.stats.position_hits}")
        self.pos_miss_label.configure(text=f"Miss: {self.stats.position_misses}")
        self.str_hits_label.configure(text=f"Hits: {self.stats.string_hits}")
        self.str_miss_label.configure(text=f"Miss: {self.stats.string_misses}")
        
        score_data = self.stats.calculate_score()
        self.score_label.configure(text=f"Score: {score_data['total_score']}")
    
    def toggle_pause(self):
        """Pause or resume the game"""
        if not self.is_playing:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.pause_btn.configure(text="▶ Resume")
            self.feedback_label.configure(text="PAUSED - Press SPACE to resume",
                                         foreground=self.COLORS["warning"])
        else:
            self.pause_btn.configure(text="⏸ Pause")
            self.feedback_label.configure(text="")
            self.next_round()
    
    def end_game(self):
        """End the current game and show results"""
        self.is_playing = False
        
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        # Calculate final score
        score_data = self.stats.calculate_score()
        
        # Save stats
        high_score = self.stats.save_to_file(self.config, score_data)
        
        # Show results screen
        self.show_results_screen(score_data, high_score)
    
    def show_results_screen(self, score_data, high_score):
        """Display the game results"""
        self.clear_screen()
        
        main_frame = ttk.Frame(self.root, style="Green.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Title
        ttk.Label(main_frame, text="🎮 GAME COMPLETE",
                 style="GreenTitle.TLabel").pack(pady=(0, 30))
        
        # Score card
        score_frame = ttk.LabelFrame(main_frame, text=" Final Score ",
                                     style="Green.TLabelframe", padding=30)
        score_frame.pack(fill=tk.X, pady=10)
        
        # Big score display
        score_text = f"🏆 {score_data['total_score']}"
        ttk.Label(score_frame, text=score_text,
                 style="GreenTitle.TLabel",
                 font=("Segoe UI", 48, "bold")).pack()
        
        # High score indicator
        if score_data['total_score'] >= high_score:
            ttk.Label(score_frame, text="🌟 NEW HIGH SCORE! 🌟",
                     style="Green.TLabel",
                     foreground=self.COLORS["warning"],
                     font=("Segoe UI", 14, "bold")).pack(pady=10)
        else:
            ttk.Label(score_frame, text=f"High Score: {high_score}",
                     style="GreenSubtitle.TLabel").pack(pady=10)
        
        # Details
        details_frame = ttk.Frame(main_frame, style="Green.TFrame")
        details_frame.pack(fill=tk.X, pady=20)
        
        # Position results
        pos_frame = ttk.LabelFrame(details_frame, text=" Position Matching ",
                                   style="Green.TLabelframe", padding=20)
        pos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(pos_frame, 
                 text=f"Accuracy: {score_data['position_accuracy']}%",
                 style="GreenBig.TLabel").pack()
        ttk.Label(pos_frame,
                 text=f"Correct: {score_data['position_hits']}",
                 style="Green.TLabel").pack()
        ttk.Label(pos_frame,
                 text=f"Missed: {score_data['position_misses']}",
                 style="Green.TLabel").pack()
        ttk.Label(pos_frame,
                 text=f"False Alarms: {score_data['position_false_alarms']}",
                 style="Green.TLabel").pack()
        
        # String results
        str_frame = ttk.LabelFrame(details_frame, text=" String Matching ",
                                   style="Green.TLabelframe", padding=20)
        str_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(str_frame,
                 text=f"Accuracy: {score_data['string_accuracy']}%",
                 style="GreenBig.TLabel").pack()
        ttk.Label(str_frame,
                 text=f"Correct: {score_data['string_hits']}",
                 style="Green.TLabel").pack()
        ttk.Label(str_frame,
                 text=f"Missed: {score_data['string_misses']}",
                 style="Green.TLabel").pack()
        ttk.Label(str_frame,
                 text=f"False Alarms: {score_data['string_false_alarms']}",
                 style="Green.TLabel").pack()
        
        # Game info
        info_frame = ttk.Frame(main_frame, style="Green.TFrame")
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"Level: {self.config.n_level}-Back | Grid: {self.config.grid_rows}x{self.config.grid_cols} | Rounds: {self.config.total_rounds}"
        ttk.Label(info_frame, text=info_text, style="GreenSubtitle.TLabel").pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style="Green.TFrame")
        button_frame.pack(fill=tk.X, pady=30)
        
        ttk.Button(button_frame, text="📊 Statistics",
                  style="GreenSecondary.TButton",
                  command=self.show_statistics).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="🔄 Play Again",
                  style="Green.TButton",
                  command=self.start_game).pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="⚙ Settings",
                  style="GreenSecondary.TButton",
                  command=self.show_settings_screen).pack(side=tk.RIGHT, padx=10)
    
    def show_statistics(self):
        """Show historical statistics"""
        try:
            stats_file = os.path.join(os.path.dirname(__file__), "game_stats.json")
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    all_stats = json.load(f)
            else:
                all_stats = {"games": [], "high_scores": {}}
        except:
            all_stats = {"games": [], "high_scores": {}}
        
        # Create stats window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Game Statistics")
        stats_window.geometry("600x500")
        stats_window.configure(bg=self.COLORS["bg_dark"])
        
        main_frame = ttk.Frame(stats_window, style="Green.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="📊 Statistics",
                 style="GreenTitle.TLabel").pack(pady=(0, 20))
        
        if not all_stats["games"]:
            ttk.Label(main_frame, text="No games played yet!",
                     style="Green.TLabel").pack(pady=20)
        else:
            # High scores
            hs_frame = ttk.LabelFrame(main_frame, text=" High Scores ",
                                      style="Green.TLabelframe", padding=15)
            hs_frame.pack(fill=tk.X, pady=10)
            
            for level, score in sorted(all_stats["high_scores"].items()):
                level_num = level.replace("level_", "")
                ttk.Label(hs_frame, 
                         text=f"{level_num}-Back: {score} points",
                         style="Green.TLabel").pack(anchor=tk.W)
            
            # Recent games
            recent_frame = ttk.LabelFrame(main_frame, text=" Recent Games ",
                                          style="Green.TLabelframe", padding=15)
            recent_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Create scrollable list
            canvas = tk.Canvas(recent_frame, bg=self.COLORS["bg_dark"],
                              highlightthickness=0)
            scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL,
                                      command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas, style="Green.TFrame")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add game records (last 20)
            for game in reversed(all_stats["games"][-20:]):
                game_text = f"{game['date'][:10]} | {game['n_level']}-Back | Score: {game['score']} | Pos: {game['position_accuracy']}% | Str: {game['string_accuracy']}%"
                ttk.Label(scrollable_frame, text=game_text,
                         style="Green.TLabel").pack(anchor=tk.W, pady=2)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  style="GreenSecondary.TButton",
                  command=stats_window.destroy).pack(pady=20)


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Center window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 900) // 2
    y = (screen_height - 750) // 2
    root.geometry(f"900x750+{x}+{y}")
    
    game = DualNBackGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
